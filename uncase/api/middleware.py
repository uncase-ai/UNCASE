"""FastAPI exception handlers and middleware."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from uncase.exceptions import UNCASEError
from uncase.logging import get_logger

if TYPE_CHECKING:
    from fastapi import FastAPI, Request

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on the FastAPI app."""

    @app.exception_handler(UNCASEError)
    async def uncase_error_handler(request: Request, exc: UNCASEError) -> JSONResponse:
        """Handle all custom UNCASE exceptions."""
        # Discriminate severity by status code
        log_fn = logger.error if exc.status_code >= 500 else logger.warning
        log_fn(
            "uncase_error",
            error_type=type(exc).__name__,
            status_code=exc.status_code,
            detail=exc.detail,
            method=request.method,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle Pydantic request validation failures with structured logging."""
        errors = exc.errors()
        logger.warning(
            "request_validation_error",
            method=request.method,
            path=request.url.path,
            error_count=len(errors),
            errors=[{"loc": e.get("loc"), "type": e.get("type")} for e in errors],
        )
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Request validation failed",
                "errors": [
                    {
                        "field": ".".join(str(loc) for loc in e.get("loc", [])),
                        "message": e.get("msg", ""),
                        "type": e.get("type", ""),
                    }
                    for e in errors
                ],
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """Catch-all for unhandled exceptions — never expose stack traces."""
        logger.error(
            "unhandled_error",
            error_type=type(exc).__name__,
            detail=str(exc),
            method=request.method,
            path=request.url.path,
            exc_info=exc,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
