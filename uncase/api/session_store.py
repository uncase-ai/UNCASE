"""In-memory session store for Layer 0 extraction engines.

Stores AgenticExtractionEngine instances keyed by UUID with a TTL of 1 hour.
"""

from __future__ import annotations

import secrets
import time
from typing import TYPE_CHECKING

from uncase.log_config import get_logger

if TYPE_CHECKING:
    from uncase.core.seed_engine.layer0.engine import AgenticExtractionEngine

logger = get_logger(__name__)

_TTL_SECONDS = 3600  # 1 hour


class _SessionEntry:
    __slots__ = ("created_at", "engine", "organization_id")

    def __init__(self, engine: AgenticExtractionEngine, organization_id: str | None = None) -> None:
        self.engine = engine
        self.created_at = time.monotonic()
        self.organization_id = organization_id

    def is_expired(self) -> bool:
        return (time.monotonic() - self.created_at) > _TTL_SECONDS


class SessionStore:
    """Thread-safe in-memory store for extraction engine sessions."""

    def __init__(self) -> None:
        self._sessions: dict[str, _SessionEntry] = {}

    def create(self, engine: AgenticExtractionEngine, organization_id: str | None = None) -> str:
        """Store an engine and return its session ID."""
        self._purge_expired()
        session_id = secrets.token_urlsafe(32)
        self._sessions[session_id] = _SessionEntry(engine, organization_id=organization_id)
        logger.info("session_created", session_id=session_id, organization_id=organization_id)
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

    def get_verified(self, session_id: str, organization_id: str | None) -> AgenticExtractionEngine | None:
        """Retrieve engine only if org matches the session's org.

        Args:
            session_id: The session identifier.
            organization_id: Expected organization ID to verify ownership.

        Returns:
            The engine if found, not expired, and org matches; None otherwise.
        """
        entry = self._sessions.get(session_id)
        if entry is None:
            return None
        if entry.is_expired():
            del self._sessions[session_id]
            logger.info("session_expired", session_id=session_id)
            return None
        if organization_id is not None and entry.organization_id != organization_id:
            logger.warning(
                "session_org_mismatch",
                session_id=session_id,
                expected=entry.organization_id,
                got=organization_id,
            )
            return None
        return entry.engine

    def get_organization_id(self, session_id: str) -> str | None:
        """Retrieve the organization ID for a session, or None if not set/expired/missing."""
        entry = self._sessions.get(session_id)
        if entry is None or entry.is_expired():
            return None
        return entry.organization_id

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
