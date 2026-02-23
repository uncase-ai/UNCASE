"""UNCASE custom exceptions with HTTP status code mapping."""

from __future__ import annotations


class UNCASEError(Exception):
    """Base exception for all UNCASE errors."""

    status_code: int = 500
    detail: str = "Internal server error"

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.__class__.detail
        super().__init__(self.detail)


# -- Authentication / Authorization --


class AuthenticationError(UNCASEError):
    """Invalid or missing API key."""

    status_code = 401
    detail = "Invalid or missing API key"


class AuthorizationError(UNCASEError):
    """Insufficient permissions for the requested operation."""

    status_code = 403
    detail = "Insufficient permissions"


class APIKeyRevokedError(AuthenticationError):
    """API key has been revoked."""

    detail = "API key has been revoked"


# -- Not Found --


class SeedNotFoundError(UNCASEError):
    """Requested seed does not exist."""

    status_code = 404
    detail = "Seed not found"


class DomainNotFoundError(UNCASEError):
    """Requested domain is not registered."""

    status_code = 404
    detail = "Domain not found"


class OrganizationNotFoundError(UNCASEError):
    """Requested organization does not exist."""

    status_code = 404
    detail = "Organization not found"


class APIKeyNotFoundError(UNCASEError):
    """Requested API key does not exist."""

    status_code = 404
    detail = "API key not found"


# -- Validation --


class PIIDetectedError(UNCASEError):
    """PII detected in data that must be clean."""

    status_code = 422
    detail = "PII detected in output data"


class ValidationError(UNCASEError):
    """Schema or data validation failure."""

    status_code = 422
    detail = "Validation error"


class QualityThresholdError(UNCASEError):
    """Generated data did not meet quality thresholds."""

    status_code = 422
    detail = "Quality thresholds not met"


# -- Conflict --


class DuplicateError(UNCASEError):
    """Resource already exists."""

    status_code = 409
    detail = "Resource already exists"
