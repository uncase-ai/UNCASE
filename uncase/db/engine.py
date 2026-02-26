"""Async database engine and session management."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from uncase.config import UNCASESettings

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_engine(settings: UNCASESettings) -> None:
    """Initialize the async engine and session factory.

    Args:
        settings: Application settings with database_url.
    """
    global _engine, _session_factory

    engine_kwargs: dict[str, object] = {
        "echo": not settings.is_production,
    }

    # QueuePool options are not compatible with SQLite (uses StaticPool)
    if not settings.database_url.startswith("sqlite"):
        engine_kwargs["pool_size"] = 5
        engine_kwargs["max_overflow"] = 10
        engine_kwargs["pool_pre_ping"] = True

    _engine = create_async_engine(settings.database_url, **engine_kwargs)
    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an async database session.

    Yields:
        AsyncSession bound to the configured engine.

    Raises:
        RuntimeError: If init_engine() has not been called.
    """
    if _session_factory is None:
        msg = "Database engine not initialized. Call init_engine() first."
        raise RuntimeError(msg)
    async with _session_factory() as session:
        yield session


async def close_engine() -> None:
    """Dispose the engine connection pool."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
