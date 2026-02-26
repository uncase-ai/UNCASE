"""Shared test fixtures."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from uncase.api.deps import get_db, get_settings
from uncase.api.main import create_app
from uncase.api.rate_limit import _counter
from uncase.config import UNCASESettings
from uncase.db.base import Base

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

# Allow overriding with a real PostgreSQL URL in CI (e.g. TEST_DATABASE_URL)
_TEST_DB_URL = os.environ.get("TEST_DATABASE_URL", "sqlite+aiosqlite://")


@pytest.fixture()
def settings() -> UNCASESettings:
    """Test settings with safe defaults."""
    return UNCASESettings(
        uncase_env="development",
        uncase_log_level="DEBUG",
        database_url=_TEST_DB_URL,
        api_secret_key="test-secret",
    )


@pytest.fixture()
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """Async session — uses PostgreSQL if TEST_DATABASE_URL is set, SQLite otherwise."""
    is_sqlite = _TEST_DB_URL.startswith("sqlite")

    engine_kwargs: dict[str, object] = {"echo": False}

    if not is_sqlite:
        engine_kwargs["pool_size"] = 5
        engine_kwargs["max_overflow"] = 10

    engine = create_async_engine(_TEST_DB_URL, **engine_kwargs)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture()
async def client(async_session: AsyncSession, settings: UNCASESettings) -> AsyncGenerator[AsyncClient, None]:
    """Test client with database session override."""
    _counter.reset()
    app = create_app()

    async def _override_db() -> AsyncGenerator[AsyncSession, None]:
        yield async_session

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_settings] = lambda: settings

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
