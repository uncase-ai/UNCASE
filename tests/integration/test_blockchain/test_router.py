"""Integration tests for blockchain API endpoints."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from uncase.db.base import Base
from uncase.db.models.blockchain import EvaluationHashModel, MerkleBatchModel, MerkleProofModel  # noqa: F401
from uncase.db.models.evaluation import EvaluationReportModel
from uncase.schemas.quality import QualityMetrics, QualityReport
from uncase.services.blockchain import BlockchainService


@pytest.fixture()
async def engine():
    eng = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest.fixture()
async def session(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as sess:
        yield sess


@pytest.fixture()
async def client(engine, session):
    """Create a test HTTP client with overridden DB dependency."""
    from uncase.api.deps import get_db
    from uncase.api.main import create_app

    app = create_app()

    async def _override_db():
        yield session

    app.dependency_overrides[get_db] = _override_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def _seed_data(session: AsyncSession, count: int = 3) -> list[str]:
    """Create evaluation reports and hash them, return report IDs."""
    report_ids = []
    service = BlockchainService(session)

    for i in range(count):
        model = EvaluationReportModel(
            conversation_id=f"conv-{i}",
            seed_id="seed-001",
            rouge_l=0.75,
            fidelidad_factual=0.92,
            diversidad_lexica=0.60,
            coherencia_dialogica=0.88,
            privacy_score=0.0,
            memorizacion=0.005,
            composite_score=0.60,
            passed=True,
            failures=[],
        )
        session.add(model)
        await session.flush()
        report_ids.append(model.id)

        report = QualityReport(
            conversation_id=f"conv-{i}",
            seed_id="seed-001",
            metrics=QualityMetrics(
                rouge_l=0.75,
                fidelidad_factual=0.92,
                diversidad_lexica=0.60,
                coherencia_dialogica=0.88,
                privacy_score=0.0,
                memorizacion=0.005,
            ),
            composite_score=0.60,
            passed=True,
            failures=[],
            evaluated_at=datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC),
        )
        await service.hash_and_store(report, model.id)

    await session.commit()
    return report_ids


class TestVerifyEndpoint:
    @pytest.mark.asyncio()
    async def test_verify_returns_hash(self, client: AsyncClient, session: AsyncSession) -> None:
        ids = await _seed_data(session, 1)
        resp = await client.get(f"/api/v1/blockchain/verify/{ids[0]}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["evaluation_report_id"] == ids[0]
        assert len(data["report_hash"]) == 64
        assert data["anchored"] is False

    @pytest.mark.asyncio()
    async def test_verify_unknown_returns_404(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/blockchain/verify/nonexistent")
        assert resp.status_code == 404


class TestBatchEndpoint:
    @pytest.mark.asyncio()
    async def test_build_batch(self, client: AsyncClient, session: AsyncSession) -> None:
        await _seed_data(session, 3)
        resp = await client.post("/api/v1/blockchain/batch", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert data["batch_number"] == 1
        assert data["leaf_count"] == 3
        assert len(data["merkle_root"]) == 64

    @pytest.mark.asyncio()
    async def test_build_batch_empty_returns_400(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/blockchain/batch", json={})
        assert resp.status_code == 400


class TestBatchesEndpoint:
    @pytest.mark.asyncio()
    async def test_list_batches_empty(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/blockchain/batches")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio()
    async def test_list_batches_after_build(self, client: AsyncClient, session: AsyncSession) -> None:
        await _seed_data(session, 2)
        await client.post("/api/v1/blockchain/batch", json={})

        resp = await client.get("/api/v1/blockchain/batches")
        assert resp.status_code == 200
        batches = resp.json()
        assert len(batches) == 1
        assert batches[0]["batch_number"] == 1


class TestStatsEndpoint:
    @pytest.mark.asyncio()
    async def test_stats_empty(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/blockchain/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_hashed"] == 0
        assert data["total_batches"] == 0

    @pytest.mark.asyncio()
    async def test_stats_after_hashing(self, client: AsyncClient, session: AsyncSession) -> None:
        await _seed_data(session, 3)
        resp = await client.get("/api/v1/blockchain/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_hashed"] == 3
        assert data["total_unbatched"] == 3
