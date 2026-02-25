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


class ProviderNotFoundError(UNCASEError):
    """Requested LLM provider does not exist."""

    status_code = 404
    detail = "Provider not found"


class PluginNotFoundError(UNCASEError):
    """Requested plugin does not exist or is not installed."""

    status_code = 404
    detail = "Plugin not found"


class PluginAlreadyInstalledError(UNCASEError):
    """Plugin is already installed for this organization."""

    status_code = 409
    detail = "Plugin already installed"


class CustomToolNotFoundError(UNCASEError):
    """Requested custom tool does not exist."""

    status_code = 404
    detail = "Custom tool not found"


class TemplateConfigNotFoundError(UNCASEError):
    """Template configuration not found for this organization."""

    status_code = 404
    detail = "Template configuration not found"


class KnowledgeDocumentNotFoundError(UNCASEError):
    """Requested knowledge document does not exist."""

    status_code = 404
    detail = "Knowledge document not found"


class JobNotFoundError(UNCASEError):
    """Requested background job does not exist."""

    status_code = 404
    detail = "Job not found"


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


# -- Sandbox --


class SandboxError(UNCASEError):
    """E2B sandbox execution failed."""

    status_code = 500
    detail = "Sandbox execution failed"


class SandboxNotConfiguredError(UNCASEError):
    """E2B sandbox is not configured or enabled."""

    status_code = 503
    detail = "E2B sandbox not configured. Set E2B_API_KEY and E2B_ENABLED=true."


class SandboxTimeoutError(SandboxError):
    """E2B sandbox execution timed out."""

    status_code = 504
    detail = "Sandbox execution timed out"


# -- ML / Training Pipeline --


class MLDependencyError(UNCASEError):
    """Required ML dependencies not installed. Install with: pip install 'uncase[ml]'"""

    status_code = 503
    detail = "Required ML dependencies not installed. Install with: pip install 'uncase[ml]'"


class TrainingError(UNCASEError):
    """Training pipeline error."""

    status_code = 500
    detail = "Training pipeline error"


class DatasetPreparationError(UNCASEError):
    """Dataset preparation failed."""

    status_code = 500
    detail = "Dataset preparation failed"
