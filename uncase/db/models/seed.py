"""Seed database model."""

from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from uncase.db.base import Base, TimestampMixin


class SeedModel(TimestampMixin, Base):
    """Database model for seeds."""

    __tablename__ = "seeds"

    # Classification
    dominio: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    idioma: Mapped[str] = mapped_column(String(10), nullable=False, default="es")
    version: Mapped[str] = mapped_column(String(10), nullable=False, default="1.0")
    etiquetas: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=list)

    # Content
    objetivo: Mapped[str] = mapped_column(Text, nullable=False)
    tono: Mapped[str] = mapped_column(String(50), nullable=False, default="profesional")
    roles: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    descripcion_roles: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Structured data (JSON for nested Pydantic models)
    pasos_turnos: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    parametros_factuales: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    privacidad: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    metricas_calidad: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Rating & run tracking
    rating: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)
    rating_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    run_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_quality_score: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)

    # Organization ownership
    organization_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationships
    organization: Mapped[OrganizationModel | None] = relationship(back_populates="seeds")  # type: ignore[name-defined] # noqa: F821

    __table_args__ = (Index("ix_seeds_dominio_org", "dominio", "organization_id"),)

    def __repr__(self) -> str:
        return f"<SeedModel id={self.id} dominio={self.dominio}>"
