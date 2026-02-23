"""Shared test fixtures."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from uncase.api.deps import get_db, get_settings
from uncase.api.main import create_app
from uncase.config import UNCASESettings
from uncase.db.base import Base

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


@pytest.fixture()
def settings() -> UNCASESettings:
    """Test settings with safe defaults."""
    return UNCASESettings(
        uncase_env="development",
        uncase_log_level="DEBUG",
        database_url="sqlite+aiosqlite://",
        api_secret_key="test-secret",
    )


@pytest.fixture()
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """Async session using in-memory SQLite for tests."""
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)

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
    app = create_app()

    async def _override_db() -> AsyncGenerator[AsyncSession, None]:
        yield async_session

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_settings] = lambda: settings

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
