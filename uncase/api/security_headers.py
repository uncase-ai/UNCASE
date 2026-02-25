"""Security headers middleware — OWASP recommended headers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware

if TYPE_CHECKING:
    from collections.abc import Callable

    from fastapi import Request
    from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add OWASP-recommended security headers to all responses.

    Headers added:
    - Strict-Transport-Security (HSTS)
    - X-Content-Type-Options
    - X-Frame-Options
    - X-XSS-Protection
    - Content-Security-Policy
    - Referrer-Policy
    - Permissions-Policy
    - Cache-Control (for API responses)
    """

    async def dispatch(self, request: Request, call_next: Callable[..., Response]) -> Response:  # type: ignore[override]
        """Add security headers to the response."""
        response = await call_next(request)  # type: ignore[misc]

        # HSTS: force HTTPS in production
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # XSS protection (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content Security Policy
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions policy (restrict browser features)
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

        # Cache control for API responses
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"

        return response  # type: ignore[no-any-return]
