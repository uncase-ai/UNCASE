"""Conversation schemas — structured representation of dialogues."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from uncase.tools.schemas import ToolCall, ToolResult  # noqa: TC001


class ConversationTurn(BaseModel):
    """A single turn in a conversation."""

    turno: int = Field(..., ge=1, description="Turn number (1-indexed)")
    rol: str = Field(..., description="Role of the speaker")
    contenido: str = Field(..., min_length=1, description="Turn content")
    herramientas_usadas: list[str] = Field(default_factory=list, description="Tools used in this turn")
    tool_calls: list[ToolCall] | None = Field(default=None, description="Tool calls made in this turn")
    tool_results: list[ToolResult] | None = Field(default=None, description="Tool results received in this turn")
    metadata: dict[str, str] = Field(default_factory=dict, description="Turn-level metadata")


class Conversation(BaseModel):
    """A complete conversation with traceability back to its seed."""

    conversation_id: str = Field(default_factory=lambda: uuid.uuid4().hex, description="Unique conversation identifier")
    seed_id: str = Field(..., description="Origin seed ID for traceability")
    dominio: str = Field(..., description="Domain namespace")
    idioma: str = Field(default="es", description="Conversation language")
    turnos: list[ConversationTurn] = Field(..., min_length=1, description="Ordered list of turns")
    es_sintetica: bool = Field(default=False, description="Whether this is a synthetic conversation")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Creation timestamp")
    metadata: dict[str, str] = Field(default_factory=dict, description="Conversation-level metadata")

    @property
    def num_turnos(self) -> int:
        """Number of turns in the conversation."""
        return len(self.turnos)

    @property
    def roles_presentes(self) -> set[str]:
        """Set of unique roles present in the conversation."""
        return {t.rol for t in self.turnos}
