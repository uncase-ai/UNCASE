"""LLM provider configuration database model."""

from __future__ import annotations

from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from uncase.db.base import Base, TimestampMixin


class LLMProviderModel(TimestampMixin, Base):
    """Database model for LLM provider configurations.

    Stores connection details for cloud and local LLM providers.
    API keys are encrypted at rest using Fernet symmetric encryption.
    """

    __tablename__ = "llm_providers"

    # Identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # anthropic, openai, google, ollama, vllm, groq, custom

    # Connection
    api_base: Mapped[str | None] = mapped_column(String(512), nullable=True)
    api_key_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_model: Mapped[str] = mapped_column(String(255), nullable=False)

    # Defaults
    max_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=4096)
    temperature_default: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Multi-tenant
    organization_id: Mapped[str | None] = mapped_column(
        String(32),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    __table_args__ = (
        Index("ix_llm_providers_org_active", "organization_id", "is_active"),
        Index("ix_llm_providers_type", "provider_type"),
    )

    def __repr__(self) -> str:
        return f"<LLMProviderModel id={self.id} name={self.name} type={self.provider_type}>"
