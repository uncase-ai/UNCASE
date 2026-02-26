"""Conversation database model."""

from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from uncase.db.base import Base, TimestampMixin


class ConversationModel(TimestampMixin, Base):
    """Persisted conversation with full turn data."""

    __tablename__ = "conversations"

    # Core fields
    conversation_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    seed_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("seeds.id", ondelete="SET NULL"), nullable=True, index=True
    )
    organization_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Classification
    dominio: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    idioma: Mapped[str] = mapped_column(String(10), nullable=False, default="es")
    es_sintetica: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Turn data stored as JSON array
    turnos: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    num_turnos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Metadata
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # User-editable fields
    status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    tags: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_conv_dominio_org", "dominio", "organization_id"),
        Index("ix_conv_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<ConversationModel id={self.id} conversation_id={self.conversation_id}>"
