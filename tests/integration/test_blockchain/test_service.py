"""Integration tests for BlockchainService with an in-memory SQLite database."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from uncase.db.base import Base
from uncase.db.models.blockchain import (
    EvaluationHashModel,
    MerkleProofModel,
)

# We need the evaluation_reports table for the FK.
from uncase.db.models.evaluation import EvaluationReportModel
from uncase.schemas.quality import QualityMetrics, QualityReport
from uncase.services.blockchain import BlockchainService


@pytest.fixture()
async def session() -> AsyncSession:
    """Provide a fresh async SQLite session with all tables created."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as sess:
        yield sess  # type: ignore[misc]

    await engine.dispose()


def _make_report(conversation_id: str = "conv-001", seed_id: str = "seed-001") -> QualityReport:
    return QualityReport(
        conversation_id=conversation_id,
        seed_id=seed_id,
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


async def _create_eval_report(session: AsyncSession) -> str:
    """Insert a dummy evaluation_reports row and return its ID."""
    model = EvaluationReportModel(
        conversation_id="conv-001",
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
    return model.id


class TestHashAndStore:
    @pytest.mark.asyncio()
    async def test_creates_hash_record(self, session: AsyncSession) -> None:
        report_id = await _create_eval_report(session)
        report = _make_report()

        service = BlockchainService(session)
        result = await service.hash_and_store(report, report_id)

        assert len(result.report_hash) == 64
        assert result.evaluation_report_id == report_id
        assert result.canonical_json is not None
        assert result.batch_id is None

    @pytest.mark.asyncio()
    async def test_same_report_same_hash(self, session: AsyncSession) -> None:
        """Two calls with the same report data produce the same hash string."""
        report = _make_report()
        id1 = await _create_eval_report(session)

        service = BlockchainService(session)
        h1 = await service.hash_and_store(report, id1)

        # We can't insert the same FK twice, but we can verify the hash value.
        from uncase.core.blockchain.hasher import hash_report

        assert h1.report_hash == hash_report(report)


class TestBuildBatch:
    @pytest.mark.asyncio()
    async def test_batch_build_without_anchor(self, session: AsyncSession) -> None:
        """Build a batch from 3 hashes without on-chain anchoring."""
        service = BlockchainService(session)

        # Create 3 evaluation hashes
        for i in range(3):
            rid = await _create_eval_report(session)
            report = _make_report(conversation_id=f"conv-{i}")
            await service.hash_and_store(report, rid)

        result = await service.build_batch()

        assert result.batch_number == 1
        assert result.leaf_count == 3
        assert result.tree_depth >= 1
        assert len(result.merkle_root) == 64
        assert result.anchored is False
        assert result.tx_hash is None

        # Verify proofs were created
        proofs = (await session.execute(select(MerkleProofModel))).scalars().all()
        assert len(proofs) == 3

        # Verify hashes were assigned batch_id
        hashes = (await session.execute(select(EvaluationHashModel))).scalars().all()
        for h in hashes:
            assert h.batch_id is not None
            assert h.leaf_index is not None

    @pytest.mark.asyncio()
    async def test_batch_build_no_unbatched_raises(self, session: AsyncSession) -> None:
        service = BlockchainService(session)
        with pytest.raises(ValueError, match="No unbatched"):
            await service.build_batch()

    @pytest.mark.asyncio()
    async def test_sequential_batch_numbers(self, session: AsyncSession) -> None:
        """Batch numbers increment sequentially."""
        service = BlockchainService(session)

        for i in range(2):
            rid = await _create_eval_report(session)
            await service.hash_and_store(_make_report(conversation_id=f"conv-a{i}"), rid)
        batch1 = await service.build_batch()

        for i in range(2):
            rid = await _create_eval_report(session)
            await service.hash_and_store(_make_report(conversation_id=f"conv-b{i}"), rid)
        batch2 = await service.build_batch()

        assert batch1.batch_number == 1
        assert batch2.batch_number == 2


class TestVerify:
    @pytest.mark.asyncio()
    async def test_verify_unbatched(self, session: AsyncSession) -> None:
        """Verification before batching returns hash but no proof."""
        rid = await _create_eval_report(session)
        report = _make_report()

        service = BlockchainService(session)
        await service.hash_and_store(report, rid)

        result = await service.verify(rid)
        assert result.report_hash is not None
        assert result.batch_id is None
        assert result.proof is None
        assert result.anchored is False

    @pytest.mark.asyncio()
    async def test_verify_batched(self, session: AsyncSession) -> None:
        """Verification after batching includes proof and batch info."""
        rid = await _create_eval_report(session)
        report = _make_report()

        service = BlockchainService(session)
        await service.hash_and_store(report, rid)
        await service.build_batch()

        result = await service.verify(rid)
        assert result.report_hash is not None
        assert result.batch_id is not None
        assert result.batch_number == 1
        assert result.proof is not None
        assert len(result.proof.merkle_root) == 64

    @pytest.mark.asyncio()
    async def test_verify_unknown_raises(self, session: AsyncSession) -> None:
        service = BlockchainService(session)
        with pytest.raises(ValueError, match="No hash found"):
            await service.verify("nonexistent-id")


class TestGetStats:
    @pytest.mark.asyncio()
    async def test_empty_stats(self, session: AsyncSession) -> None:
        service = BlockchainService(session)
        stats = await service.get_stats()
        assert stats.total_hashed == 0
        assert stats.total_batches == 0
        assert stats.total_anchored == 0

    @pytest.mark.asyncio()
    async def test_stats_after_batch(self, session: AsyncSession) -> None:
        service = BlockchainService(session)

        for i in range(3):
            rid = await _create_eval_report(session)
            await service.hash_and_store(_make_report(conversation_id=f"conv-{i}"), rid)

        await service.build_batch()

        stats = await service.get_stats()
        assert stats.total_hashed == 3
        assert stats.total_batched == 3
        assert stats.total_unbatched == 0
        assert stats.total_batches == 1
        assert stats.total_anchored == 0  # No anchor client
