"""Rate limiting middleware — per-key request throttling.

Uses Redis when ``REDIS_URL`` is set, falls back to an in-memory sliding
window counter otherwise.
"""

from __future__ import annotations

import os
import time
from collections import defaultdict
from typing import TYPE_CHECKING, Protocol

import structlog
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

if TYPE_CHECKING:
    from collections.abc import Callable

    from fastapi import Request
    from starlette.responses import Response

logger = structlog.get_logger(__name__)

# Default rate limits per tier
RATE_LIMITS: dict[str, tuple[int, int]] = {
    # tier: (requests, window_seconds)
    "free": (60, 60),
    "developer": (300, 60),
    "enterprise": (1000, 60),
    "default": (120, 60),
}

# Paths exempt from rate limiting
EXEMPT_PATHS: frozenset[str] = frozenset(
    {
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/health",
        "/api/v1/health/detailed",
    }
)


class RateLimitBackend(Protocol):
    """Protocol for rate limit backends."""

    def reset(self) -> None: ...
    def is_allowed(self, key: str, limit: int, window: int) -> tuple[bool, int, int]: ...


class _SlidingWindowCounter:
    """In-memory sliding window rate limiter."""

    def __init__(self) -> None:
        self._windows: dict[str, list[float]] = defaultdict(list)

    def reset(self) -> None:
        """Clear all rate limit windows (used in tests)."""
        self._windows.clear()

    def is_allowed(self, key: str, limit: int, window: int) -> tuple[bool, int, int]:
        """Check if a request is allowed under the rate limit.

        Args:
            key: Rate limit key (e.g. API key or IP).
            limit: Max requests per window.
            window: Window size in seconds.

        Returns:
            Tuple of (allowed, remaining, reset_seconds).
        """
        now = time.monotonic()
        cutoff = now - window

        # Remove expired entries
        self._windows[key] = [t for t in self._windows[key] if t > cutoff]

        current = len(self._windows[key])
        remaining = max(0, limit - current)

        if current >= limit:
            # Find the oldest entry to calculate reset time
            reset = int(self._windows[key][0] - cutoff) + 1 if self._windows[key] else window
            return False, 0, reset

        self._windows[key].append(now)
        return True, remaining - 1, window


class _RedisCounter:
    """Redis-backed sliding window rate limiter using sorted sets."""

    def __init__(self, redis_url: str) -> None:
        from redis import Redis

        self._redis: Redis = Redis.from_url(redis_url, decode_responses=True)
        logger.info("rate_limit_backend", backend="redis", url=redis_url.split("@")[-1])

    def reset(self) -> None:
        """Flush all rate limit keys (used in tests)."""
        for key in self._redis.scan_iter("rl:*"):
            self._redis.delete(key)

    def is_allowed(self, key: str, limit: int, window: int) -> tuple[bool, int, int]:
        """Check rate limit using a Redis sorted set with timestamps as scores."""
        now = time.time()
        cutoff = now - window
        rkey = f"rl:{key}"

        pipe = self._redis.pipeline(transaction=True)
        pipe.zremrangebyscore(rkey, "-inf", cutoff)
        pipe.zcard(rkey)
        pipe.zadd(rkey, {f"{now}": now})
        pipe.expire(rkey, window)
        results = pipe.execute()

        current: int = results[1]
        remaining = max(0, limit - current)

        if current >= limit:
            return False, 0, window

        return True, remaining - 1, window


def _create_backend() -> RateLimitBackend:
    """Create the appropriate rate limit backend based on environment."""
    redis_url = os.environ.get("REDIS_URL", "")

    if redis_url:
        try:
            return _RedisCounter(redis_url)
        except Exception:
            logger.warning("redis_rate_limit_fallback", message="Redis unavailable, using in-memory counter.")

    return _SlidingWindowCounter()


_counter: RateLimitBackend = _create_backend()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for per-key rate limiting.

    Identifies the client by:
    1. X-API-Key header (if present)
    2. Authorization header (if present)
    3. Client IP address (fallback)

    Rate limit headers are included in every response:
    - X-RateLimit-Limit: Maximum requests per window
    - X-RateLimit-Remaining: Remaining requests
    - X-RateLimit-Reset: Seconds until window resets
    """

    async def dispatch(self, request: Request, call_next: Callable[..., Response]) -> Response:  # type: ignore[override]
        """Apply rate limiting to the request."""
        path = request.url.path

        # Skip exempt paths
        if path in EXEMPT_PATHS:
            return await call_next(request)  # type: ignore[misc, no-any-return]

        # Determine rate limit key
        api_key = request.headers.get("x-api-key", "")
        auth_header = request.headers.get("authorization", "")
        client_ip = request.client.host if request.client else "unknown"

        rate_key = api_key or auth_header or client_ip

        # Determine tier (default for now — could be loaded from DB)
        tier = "default"
        limit, window = RATE_LIMITS[tier]

        allowed, remaining, reset = _counter.is_allowed(rate_key, limit, window)

        if not allowed:
            logger.warning(
                "rate_limit_exceeded",
                path=path,
                client=client_ip,
                limit=limit,
                window=window,
            )
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset),
                    "Retry-After": str(reset),
                },
            )

        response = await call_next(request)  # type: ignore[misc]

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset)

        return response  # type: ignore[no-any-return]
