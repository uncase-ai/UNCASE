"""Integration tests for the Audit API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from uncase.db.models.audit import AuditLogModel

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture()
async def sample_audit_logs(async_session: AsyncSession) -> list[AuditLogModel]:
    """Create sample audit log entries directly in the DB."""
    logs = [
        AuditLogModel(
            action="create",
            resource_type="seed",
            resource_id="seed-abc",
            actor_type="user",
            actor_id="user-001",
            organization_id=None,
            ip_address="127.0.0.1",
            endpoint="/api/v1/seeds",
            http_method="POST",
            detail="Created fictional seed for testing",
            status="success",
        ),
        AuditLogModel(
            action="delete",
            resource_type="seed",
            resource_id="seed-def",
            actor_type="system",
            actor_id="system",
            organization_id=None,
            ip_address=None,
            endpoint="/api/v1/seeds/seed-def",
            http_method="DELETE",
            detail="Deleted fictional seed",
            status="success",
        ),
        AuditLogModel(
            action="read",
            resource_type="job",
            resource_id="job-001",
            actor_type="api_key",
            actor_id="key-001",
            organization_id=None,
            ip_address="192.168.1.100",
            endpoint="/api/v1/jobs/job-001",
            http_method="GET",
            detail="Read job status",
            status="success",
        ),
        AuditLogModel(
            action="login",
            resource_type="api_key",
            resource_id=None,
            actor_type="user",
            actor_id="user-blocked",
            organization_id=None,
            ip_address="10.0.0.1",
            endpoint="/api/v1/auth/login",
            http_method="POST",
            detail="Login attempt denied",
            status="denied",
        ),
    ]
    async_session.add_all(logs)
    await async_session.commit()
    for log in logs:
        await async_session.refresh(log)
    return logs


@pytest.mark.integration
class TestListAuditLogs:
    """Test GET /api/v1/audit."""

    async def test_list_empty(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/audit")
        assert response.status_code == 200
        data = response.json()
        assert data == []

    async def test_list_with_logs(self, client: AsyncClient, sample_audit_logs: list[AuditLogModel]) -> None:
        response = await client.get("/api/v1/audit")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4

    async def test_filter_by_action(self, client: AsyncClient, sample_audit_logs: list[AuditLogModel]) -> None:
        response = await client.get("/api/v1/audit", params={"action": "create"})
        data = response.json()
        assert len(data) == 1
        assert data[0]["action"] == "create"

    async def test_filter_by_resource_type(self, client: AsyncClient, sample_audit_logs: list[AuditLogModel]) -> None:
        response = await client.get("/api/v1/audit", params={"resource_type": "seed"})
        data = response.json()
        assert len(data) == 2
        for entry in data:
            assert entry["resource_type"] == "seed"

    async def test_filter_by_action_and_resource_type(
        self, client: AsyncClient, sample_audit_logs: list[AuditLogModel]
    ) -> None:
        response = await client.get(
            "/api/v1/audit",
            params={"action": "delete", "resource_type": "seed"},
        )
        data = response.json()
        assert len(data) == 1
        assert data[0]["action"] == "delete"
        assert data[0]["resource_type"] == "seed"

    async def test_filter_no_results(self, client: AsyncClient, sample_audit_logs: list[AuditLogModel]) -> None:
        response = await client.get("/api/v1/audit", params={"action": "export"})
        data = response.json()
        assert len(data) == 0

    async def test_pagination(self, client: AsyncClient, sample_audit_logs: list[AuditLogModel]) -> None:
        response = await client.get("/api/v1/audit", params={"page": 1, "page_size": 2})
        data = response.json()
        assert len(data) == 2

    async def test_pagination_second_page(self, client: AsyncClient, sample_audit_logs: list[AuditLogModel]) -> None:
        response = await client.get("/api/v1/audit", params={"page": 2, "page_size": 2})
        data = response.json()
        assert len(data) == 2

    async def test_audit_entry_fields(self, client: AsyncClient, sample_audit_logs: list[AuditLogModel]) -> None:
        """Verify that audit log entries contain the expected fields."""
        response = await client.get("/api/v1/audit")
        data = response.json()
        entry = data[0]
        expected_fields = {
            "id",
            "action",
            "resource_type",
            "resource_id",
            "actor_type",
            "actor_id",
            "organization_id",
            "ip_address",
            "endpoint",
            "http_method",
            "detail",
            "extra_data",
            "status",
            "created_at",
        }
        assert expected_fields.issubset(set(entry.keys()))

    async def test_denied_status_entry(self, client: AsyncClient, sample_audit_logs: list[AuditLogModel]) -> None:
        response = await client.get("/api/v1/audit", params={"action": "login"})
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "denied"
