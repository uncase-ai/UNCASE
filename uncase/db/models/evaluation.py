"""Evaluation report database model."""

from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from uncase.db.base import Base, TimestampMixin


class EvaluationReportModel(TimestampMixin, Base):
    """Persisted quality evaluation report for a conversation."""

    __tablename__ = "evaluation_reports"

    # References
    conversation_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    seed_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("seeds.id", ondelete="SET NULL"), nullable=True, index=True
    )
    organization_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Individual metrics
    rouge_l: Mapped[float] = mapped_column(Float, nullable=False)
    fidelidad_factual: Mapped[float] = mapped_column(Float, nullable=False)
    diversidad_lexica: Mapped[float] = mapped_column(Float, nullable=False)
    coherencia_dialogica: Mapped[float] = mapped_column(Float, nullable=False)
    privacy_score: Mapped[float] = mapped_column(Float, nullable=False)
    memorizacion: Mapped[float] = mapped_column(Float, nullable=False)

    # Composite result
    composite_score: Mapped[float] = mapped_column(Float, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    failures: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=list)

    # Context
    dominio: Mapped[str | None] = mapped_column(String(100), nullable=True)
    evaluation_context: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_eval_seed_org", "seed_id", "organization_id"),
        Index("ix_eval_passed", "passed"),
    )

    def __repr__(self) -> str:
        return f"<EvaluationReportModel id={self.id} passed={self.passed} score={self.composite_score}>"
