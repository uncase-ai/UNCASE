"""Validation schemas for pipeline checks."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


class ValidationCheck(BaseModel):
    """A single validation check result."""

    name: str = Field(..., description="Check name")
    passed: bool = Field(..., description="Whether the check passed")
    severity: Literal["error", "warning", "info"] = Field(default="error", description="Check severity")
    message: str = Field(default="", description="Human-readable result message")


class ValidationReport(BaseModel):
    """Aggregated validation report."""

    target_id: str = Field(..., description="ID of the validated resource")
    target_type: str = Field(..., description="Type of resource (seed, conversation, etc.)")
    checks: list[ValidationCheck] = Field(default_factory=list, description="Individual check results")
    validated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Validation timestamp")

    @property
    def passed(self) -> bool:
        """True if all error-severity checks passed."""
        return all(c.passed for c in self.checks if c.severity == "error")

    @property
    def error_count(self) -> int:
        """Number of failed error-severity checks."""
        return sum(1 for c in self.checks if c.severity == "error" and not c.passed)

    @property
    def warning_count(self) -> int:
        """Number of failed warning-severity checks."""
        return sum(1 for c in self.checks if c.severity == "warning" and not c.passed)
