"""Tests for the audit logging service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from uncase.db.models.audit import AuditLogModel
from uncase.services.audit import AuditService, audit

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class TestAuditFunction:
    async def test_basic_audit(self, async_session: AsyncSession) -> None:
        await audit(
            async_session,
            action="create",
            resource_type="seed",
            resource_id="seed-001",
            actor_id="org-001",
            detail="Created seed for automotive domain",
        )
        # Verify it was persisted
        service = AuditService(async_session)
        logs = await service.list_logs(action="create")
        assert len(logs) == 1
        assert logs[0].action == "create"
        assert logs[0].resource_type == "seed"
        assert logs[0].resource_id == "seed-001"
        assert logs[0].detail == "Created seed for automotive domain"

    async def test_audit_with_metadata(self, async_session: AsyncSession) -> None:
        await audit(
            async_session,
            action="pipeline_run",
            resource_type="job",
            resource_id="job-100",
            extra_data={"domain": "automotive.sales", "count": 100},
        )
        service = AuditService(async_session)
        logs = await service.list_logs(action="pipeline_run")
        assert len(logs) == 1
        assert logs[0].extra_data["domain"] == "automotive.sales"

    async def test_audit_denied_status(self, async_session: AsyncSession) -> None:
        await audit(
            async_session,
            action="read",
            resource_type="seed",
            resource_id="seed-002",
            status="denied",
            detail="Insufficient permissions",
        )
        service = AuditService(async_session)
        logs = await service.list_logs()
        assert logs[0].status == "denied"


class TestAuditService:
    async def test_list_empty(self, async_session: AsyncSession) -> None:
        service = AuditService(async_session)
        logs = await service.list_logs()
        assert logs == []

    async def test_filter_by_action(self, async_session: AsyncSession) -> None:
        await audit(async_session, action="create", resource_type="seed")
        await audit(async_session, action="delete", resource_type="seed")
        service = AuditService(async_session)
        logs = await service.list_logs(action="create")
        assert len(logs) == 1

    async def test_filter_by_resource_type(self, async_session: AsyncSession) -> None:
        await audit(async_session, action="create", resource_type="seed")
        await audit(async_session, action="create", resource_type="job")
        service = AuditService(async_session)
        logs = await service.list_logs(resource_type="job")
        assert len(logs) == 1

    async def test_filter_by_org(self, async_session: AsyncSession) -> None:
        await audit(async_session, action="create", resource_type="seed", organization_id="org-1")
        await audit(async_session, action="create", resource_type="seed", organization_id="org-2")
        service = AuditService(async_session)
        logs = await service.list_logs(organization_id="org-1")
        assert len(logs) == 1

    async def test_pagination(self, async_session: AsyncSession) -> None:
        for i in range(5):
            await audit(async_session, action="create", resource_type="seed", resource_id=f"s-{i}")
        service = AuditService(async_session)
        page1 = await service.list_logs(page=1, page_size=2)
        page2 = await service.list_logs(page=2, page_size=2)
        assert len(page1) == 2
        assert len(page2) == 2


class TestAuditLogModel:
    def test_tablename(self) -> None:
        assert AuditLogModel.__tablename__ == "audit_logs"
