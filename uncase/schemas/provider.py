"""API request/response schemas for LLM provider management."""

from __future__ import annotations

from pydantic import BaseModel, Field

PROVIDER_TYPES = [
    "anthropic",
    "openai",
    "google",
    "ollama",
    "vllm",
    "groq",
    "custom",
]


class ProviderCreateRequest(BaseModel):
    """Request body for registering an LLM provider."""

    name: str = Field(..., min_length=1, max_length=255, description="Display name for this provider")
    provider_type: str = Field(
        ...,
        description="Provider type: anthropic, openai, google, ollama, vllm, groq, custom",
    )
    api_base: str | None = Field(
        default=None,
        description="Base URL for the API (required for ollama, vllm, custom)",
        examples=["http://localhost:11434", "https://api.openai.com/v1"],
    )
    api_key: str | None = Field(
        default=None,
        description="API key (encrypted at rest, never returned in responses)",
    )
    default_model: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Default model to use with this provider",
        examples=["claude-sonnet-4-20250514", "gpt-4o", "llama3.1:8b"],
    )
    max_tokens: int = Field(default=4096, ge=1, le=128000, description="Default max tokens")
    temperature_default: float = Field(default=0.7, ge=0.0, le=2.0, description="Default temperature")
    is_default: bool = Field(default=False, description="Set as the default provider for generation")


class ProviderUpdateRequest(BaseModel):
    """Request body for updating an LLM provider."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    api_base: str | None = None
    api_key: str | None = Field(default=None, description="New API key (replaces existing)")
    default_model: str | None = Field(default=None, min_length=1, max_length=255)
    max_tokens: int | None = Field(default=None, ge=1, le=128000)
    temperature_default: float | None = Field(default=None, ge=0.0, le=2.0)
    is_active: bool | None = None
    is_default: bool | None = None


class ProviderResponse(BaseModel):
    """Response body for an LLM provider (API key is never exposed)."""

    id: str
    name: str
    provider_type: str
    api_base: str | None
    has_api_key: bool = Field(description="Whether an API key is configured (key itself is never returned)")
    default_model: str
    max_tokens: int
    temperature_default: float
    is_active: bool
    is_default: bool
    organization_id: str | None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class ProviderTestResponse(BaseModel):
    """Response from testing a provider connection."""

    provider_id: str
    provider_name: str
    status: str = Field(description="ok, error, timeout")
    latency_ms: float | None = Field(default=None, description="Response time in milliseconds")
    model_tested: str
    error: str | None = None


class ProviderListResponse(BaseModel):
    """Paginated list of providers."""

    items: list[ProviderResponse]
    total: int
