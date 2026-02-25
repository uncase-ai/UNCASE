"""Prometheus metrics endpoint and request instrumentation.

Exposes ``/metrics`` in Prometheus text format with key platform metrics.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import TYPE_CHECKING

import structlog
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware

if TYPE_CHECKING:
    from collections.abc import Callable

    from fastapi import Request
    from starlette.responses import Response

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["metrics"])

# In-memory metric counters (swap to prometheus_client if installed)
_request_count: dict[str, int] = defaultdict(int)
_request_duration_sum: dict[str, float] = defaultdict(float)
_request_duration_count: dict[str, int] = defaultdict(int)
_error_count: dict[str, int] = defaultdict(int)
_active_requests: int = 0


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware that collects request metrics for the /metrics endpoint."""

    async def dispatch(self, request: Request, call_next: Callable[..., Response]) -> Response:  # type: ignore[override]
        """Instrument request with timing and status tracking."""
        global _active_requests

        path = request.url.path
        method = request.method

        # Skip metrics endpoint itself
        if path == "/metrics":
            return await call_next(request)  # type: ignore[misc, no-any-return]

        _active_requests += 1
        start = time.monotonic()

        try:
            response = await call_next(request)  # type: ignore[misc]
        except Exception:
            _error_count[f"{method}_{path}_500"] += 1
            _active_requests -= 1
            raise

        duration = time.monotonic() - start
        status = response.status_code

        key = f"{method}_{path}_{status}"
        _request_count[key] += 1
        _request_duration_sum[key] += duration
        _request_duration_count[key] += 1

        if status >= 400:
            _error_count[key] += 1

        _active_requests -= 1

        return response  # type: ignore[no-any-return]


@router.get("/metrics", response_class=PlainTextResponse, include_in_schema=False)
async def prometheus_metrics() -> str:
    """Prometheus-compatible metrics endpoint.

    Exports:
    - uncase_http_requests_total: Total HTTP requests by method, path, status
    - uncase_http_request_duration_seconds: Request duration histogram
    - uncase_http_errors_total: Total HTTP errors
    - uncase_active_requests: Currently active requests
    """
    lines: list[str] = []

    # Request count
    lines.append("# HELP uncase_http_requests_total Total HTTP requests")
    lines.append("# TYPE uncase_http_requests_total counter")
    for key, count in sorted(_request_count.items()):
        parts = key.rsplit("_", 1)
        if len(parts) == 2:
            method_path, status = parts
            lines.append(f'uncase_http_requests_total{{endpoint="{method_path}",status="{status}"}} {count}')

    # Request duration
    lines.append("# HELP uncase_http_request_duration_seconds Request duration in seconds")
    lines.append("# TYPE uncase_http_request_duration_seconds summary")
    for key, total in sorted(_request_duration_sum.items()):
        count = _request_duration_count.get(key, 1)
        avg = total / count if count > 0 else 0
        parts = key.rsplit("_", 1)
        if len(parts) == 2:
            method_path, status = parts
            lines.append(
                f'uncase_http_request_duration_seconds{{endpoint="{method_path}",status="{status}"}} {avg:.6f}'
            )

    # Error count
    lines.append("# HELP uncase_http_errors_total Total HTTP errors (4xx + 5xx)")
    lines.append("# TYPE uncase_http_errors_total counter")
    for key, count in sorted(_error_count.items()):
        parts = key.rsplit("_", 1)
        if len(parts) == 2:
            method_path, status = parts
            lines.append(f'uncase_http_errors_total{{endpoint="{method_path}",status="{status}"}} {count}')

    # Active requests
    lines.append("# HELP uncase_active_requests Currently processing requests")
    lines.append("# TYPE uncase_active_requests gauge")
    lines.append(f"uncase_active_requests {_active_requests}")

    return "\n".join(lines) + "\n"
