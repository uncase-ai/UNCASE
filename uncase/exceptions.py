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


class TemplateNotFoundError(UNCASEError):
    """Requested template does not exist."""

    status_code = 404
    detail = "Template not found"


class ToolNotFoundError(UNCASEError):
    """Requested tool does not exist."""

    status_code = 404
    detail = "Tool not found"


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


class ImportFormatError(UNCASEError):
    """Import format is not supported."""

    status_code = 422
    detail = "Unsupported import format"


class ImportParsingError(UNCASEError):
    """Failed to parse the provided import data."""

    status_code = 422
    detail = "Failed to parse import data"


# -- Conflict --


class DuplicateError(UNCASEError):
    """Resource already exists."""

    status_code = 409
    detail = "Resource already exists"


# -- Generation / LLM --


class GenerationError(UNCASEError):
    """Synthetic conversation generation failed."""

    status_code = 500
    detail = "Generation failed"


class LLMConfigurationError(UNCASEError):
    """LLM provider is not configured or unreachable."""

    status_code = 503
    detail = "LLM provider not configured"
