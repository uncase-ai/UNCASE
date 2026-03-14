"""In-memory session store for Layer 0 extraction engines.

Stores AgenticExtractionEngine instances keyed by UUID with a TTL of 1 hour.
"""

from __future__ import annotations

import time
import uuid
from typing import TYPE_CHECKING

from uncase.log_config import get_logger

if TYPE_CHECKING:
    from uncase.core.seed_engine.layer0.engine import AgenticExtractionEngine

logger = get_logger(__name__)

_TTL_SECONDS = 3600  # 1 hour


class _SessionEntry:
    __slots__ = ("engine", "created_at")

    def __init__(self, engine: AgenticExtractionEngine) -> None:
        self.engine = engine
        self.created_at = time.monotonic()

    def is_expired(self) -> bool:
        return (time.monotonic() - self.created_at) > _TTL_SECONDS


class SessionStore:
    """Thread-safe in-memory store for extraction engine sessions."""

    def __init__(self) -> None:
        self._sessions: dict[str, _SessionEntry] = {}

    def create(self, engine: AgenticExtractionEngine) -> str:
        """Store an engine and return its session ID."""
        self._purge_expired()
        session_id = uuid.uuid4().hex
        self._sessions[session_id] = _SessionEntry(engine)
        logger.info("session_created", session_id=session_id)
        return session_id

    def get(self, session_id: str) -> AgenticExtractionEngine | None:
        """Retrieve an engine by session ID, or None if expired/missing."""
        entry = self._sessions.get(session_id)
        if entry is None:
            return None
        if entry.is_expired():
            del self._sessions[session_id]
            logger.info("session_expired", session_id=session_id)
            return None
        return entry.engine

    def delete(self, session_id: str) -> bool:
        """Remove a session. Returns True if it existed."""
        removed = self._sessions.pop(session_id, None) is not None
        if removed:
            logger.info("session_deleted", session_id=session_id)
        return removed

    def _purge_expired(self) -> None:
        """Remove all expired sessions."""
        expired = [sid for sid, entry in self._sessions.items() if entry.is_expired()]
        for sid in expired:
            del self._sessions[sid]
        if expired:
            logger.debug("sessions_purged", count=len(expired))


# Singleton instance
extraction_sessions = SessionStore()
