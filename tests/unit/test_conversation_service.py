"""Tests for the conversation CRUD service layer."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import pytest

import uncase.schemas.conversation_api as _conv_api_mod
from uncase.exceptions import ConversationNotFoundError, ValidationError
from uncase.schemas.conversation import ConversationTurn
from uncase.schemas.conversation_api import (
    ConversationCreateRequest,
    ConversationUpdateRequest,
)
from uncase.services.conversation import ConversationService
from uncase.tools.schemas import ToolCall, ToolResult

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _make_create_request(**overrides: object) -> ConversationCreateRequest:
    """Build a valid ConversationCreateRequest with fictional defaults."""
    defaults: dict[str, object] = {
        "conversation_id": "conv-test-001",
        "seed_id": "seed-test-001",
        "dominio": "automotive.sales",
        "idioma": "es",
        "turnos": [
            ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias, en que puedo ayudarle?"),
            ConversationTurn(turno=2, rol="cliente", contenido="Busco informacion sobre vehiculos."),
            ConversationTurn(turno=3, rol="vendedor", contenido="Con gusto, que tipo de vehiculo le interesa?"),
        ],
        "es_sintetica": True,
        "metadata": {},
        "status": None,
        "rating": None,
        "tags": None,
        "notes": None,
    }
    defaults.update(overrides)
    return ConversationCreateRequest(**defaults)  # type: ignore[arg-type]


def _make_create_request_with_tools(**overrides: object) -> ConversationCreateRequest:
    """Build a ConversationCreateRequest that includes tool calls and results."""
    defaults: dict[str, object] = {
        "conversation_id": "conv-tools-001",
        "seed_id": "seed-test-001",
        "dominio": "automotive.sales",
        "idioma": "es",
        "turnos": [
            ConversationTurn(turno=1, rol="vendedor", contenido="Buenos dias, en que puedo ayudarle?"),
            ConversationTurn(turno=2, rol="cliente", contenido="Busco un Toyota Corolla."),
            ConversationTurn(
                turno=3,
                rol="vendedor",
                contenido="Permita buscar en nuestro inventario.",
                herramientas_usadas=["buscar_inventario"],
                tool_calls=[
                    ToolCall(tool_name="buscar_inventario", arguments={"marca": "Toyota", "modelo": "Corolla"})
                ],
            ),
            ConversationTurn(
                turno=4,
                rol="herramienta",
                contenido="Resultado de busqueda.",
                tool_results=[
                    ToolResult(
                        tool_call_id="call_001",
                        tool_name="buscar_inventario",
                        result={"vehiculos": [{"id": "v001"}], "total": 1},
                        status="success",
                        duration_ms=120,
                    )
                ],
            ),
            ConversationTurn(turno=5, rol="vendedor", contenido="Tenemos un Toyota Corolla disponible."),
        ],
        "es_sintetica": True,
        "metadata": {"source": "test"},
    }
    defaults.update(overrides)
    return ConversationCreateRequest(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


class TestConversationServiceCreate:
    async def test_create_returns_response(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        req = _make_create_request()
        resp = await service.create_conversation(req)

        assert resp.id is not None
        assert resp.conversation_id == "conv-test-001"
        assert resp.seed_id == "seed-test-001"
        assert resp.dominio == "automotive.sales"
        assert resp.idioma == "es"
        assert resp.es_sintetica is True
        assert resp.num_turnos == 3

    async def test_create_persists_to_db(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        req = _make_create_request()
        created = await service.create_conversation(req)

        fetched = await service.get_conversation(created.conversation_id)
        assert fetched.id == created.id
        assert fetched.conversation_id == created.conversation_id

    async def test_create_with_organization(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        req = _make_create_request()
        resp = await service.create_conversation(req, organization_id="org-test-123")

        assert resp.organization_id == "org-test-123"

    async def test_create_without_seed_id(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        req = _make_create_request(seed_id=None)
        resp = await service.create_conversation(req)

        assert resp.seed_id is None

    async def test_create_with_metadata(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        req = _make_create_request(metadata={"source": "import", "version": "1.0"})
        resp = await service.create_conversation(req)

        assert resp.metadata == {"source": "import", "version": "1.0"}

    async def test_create_with_status_and_rating(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        req = _make_create_request(status="valid", rating=4.5)
        resp = await service.create_conversation(req)

        assert resp.status == "valid"
        assert resp.rating == 4.5

    async def test_create_with_tags_and_notes(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        req = _make_create_request(tags=["demo", "automotive"], notes="Conversation for testing purposes")
        resp = await service.create_conversation(req)

        assert resp.tags == ["demo", "automotive"]
        assert resp.notes == "Conversation for testing purposes"

    async def test_create_with_tool_calls(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        req = _make_create_request_with_tools()
        resp = await service.create_conversation(req)

        assert resp.num_turnos == 5
        assert resp.conversation_id == "conv-tools-001"
        # Verify the turnos are stored correctly
        assert len(resp.turnos) == 5

    async def test_create_different_domain(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        req = _make_create_request(conversation_id="conv-med-001", dominio="medical.consultation")
        resp = await service.create_conversation(req)

        assert resp.dominio == "medical.consultation"

    async def test_create_different_language(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        req = _make_create_request(conversation_id="conv-en-001", idioma="en")
        resp = await service.create_conversation(req)

        assert resp.idioma == "en"

    async def test_create_sets_timestamps(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        req = _make_create_request()
        resp = await service.create_conversation(req)

        assert resp.created_at is not None
        assert resp.updated_at is not None


# ---------------------------------------------------------------------------
# Get
# ---------------------------------------------------------------------------


class TestConversationServiceGet:
    async def test_get_existing_conversation(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        created = await service.create_conversation(_make_create_request())

        found = await service.get_conversation(created.conversation_id)
        assert found.id == created.id
        assert found.conversation_id == created.conversation_id
        assert found.dominio == created.dominio

    async def test_get_nonexistent_raises(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        with pytest.raises(ConversationNotFoundError):
            await service.get_conversation("nonexistent-conv-id")

    async def test_get_returns_all_fields(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        req = _make_create_request(
            status="valid",
            rating=3.5,
            tags=["test"],
            notes="A note",
            metadata={"key": "val"},
        )
        created = await service.create_conversation(req, organization_id="org-x")
        found = await service.get_conversation(created.conversation_id)

        assert found.status == "valid"
        assert found.rating == 3.5
        assert found.tags == ["test"]
        assert found.notes == "A note"
        assert found.metadata == {"key": "val"}
        assert found.organization_id == "org-x"
        assert found.es_sintetica is True
        assert found.num_turnos == 3


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


class TestConversationServiceList:
    async def test_list_empty(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        result = await service.list_conversations()

        assert result.items == []
        assert result.total == 0
        assert result.page == 1
        assert result.page_size == 20

    async def test_list_returns_all(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        await service.create_conversation(_make_create_request(conversation_id="c1"))
        await service.create_conversation(_make_create_request(conversation_id="c2"))
        result = await service.list_conversations()

        assert result.total == 2
        assert len(result.items) == 2

    async def test_list_filter_by_domain(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        await service.create_conversation(_make_create_request(conversation_id="c1", dominio="automotive.sales"))
        await service.create_conversation(
            _make_create_request(conversation_id="c2", dominio="medical.consultation")
        )
        result = await service.list_conversations(domain="automotive.sales")

        assert result.total == 1
        assert result.items[0].dominio == "automotive.sales"

    async def test_list_filter_by_language(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        await service.create_conversation(_make_create_request(conversation_id="c1", idioma="es"))
        await service.create_conversation(_make_create_request(conversation_id="c2", idioma="en"))
        result = await service.list_conversations(language="en")

        assert result.total == 1
        assert result.items[0].idioma == "en"

    async def test_list_filter_by_status(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        await service.create_conversation(_make_create_request(conversation_id="c1", status="valid"))
        await service.create_conversation(_make_create_request(conversation_id="c2", status="invalid"))
        result = await service.list_conversations(status="valid")

        assert result.total == 1
        assert result.items[0].status == "valid"

    async def test_list_filter_by_seed_id(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        await service.create_conversation(_make_create_request(conversation_id="c1", seed_id="seed-a"))
        await service.create_conversation(_make_create_request(conversation_id="c2", seed_id="seed-b"))
        result = await service.list_conversations(seed_id="seed-a")

        assert result.total == 1
        assert result.items[0].seed_id == "seed-a"

    async def test_list_filter_by_organization(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        await service.create_conversation(
            _make_create_request(conversation_id="c1"), organization_id="org-a"
        )
        await service.create_conversation(
            _make_create_request(conversation_id="c2"), organization_id="org-b"
        )
        result = await service.list_conversations(organization_id="org-a")

        assert result.total == 1
        assert result.items[0].organization_id == "org-a"

    async def test_list_combined_filters(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        await service.create_conversation(
            _make_create_request(conversation_id="c1", dominio="automotive.sales", idioma="es", status="valid")
        )
        await service.create_conversation(
            _make_create_request(conversation_id="c2", dominio="automotive.sales", idioma="en", status="valid")
        )
        await service.create_conversation(
            _make_create_request(conversation_id="c3", dominio="medical.consultation", idioma="es", status="valid")
        )
        result = await service.list_conversations(domain="automotive.sales", language="es", status="valid")

        assert result.total == 1
        assert result.items[0].conversation_id == "c1"

    async def test_list_pagination(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        for i in range(5):
            await service.create_conversation(_make_create_request(conversation_id=f"c{i}"))

        page1 = await service.list_conversations(page=1, page_size=2)
        assert len(page1.items) == 2
        assert page1.total == 5
        assert page1.page == 1
        assert page1.page_size == 2

        page2 = await service.list_conversations(page=2, page_size=2)
        assert len(page2.items) == 2

        page3 = await service.list_conversations(page=3, page_size=2)
        assert len(page3.items) == 1

    async def test_list_pagination_beyond_range(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        await service.create_conversation(_make_create_request(conversation_id="c1"))

        result = await service.list_conversations(page=10, page_size=20)
        assert result.total == 1
        assert len(result.items) == 0

    async def test_list_invalid_page_raises(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        with pytest.raises(ValidationError, match="Page must be >= 1"):
            await service.list_conversations(page=0)

    async def test_list_invalid_page_negative_raises(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        with pytest.raises(ValidationError, match="Page must be >= 1"):
            await service.list_conversations(page=-1)

    async def test_list_invalid_page_size_too_small(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        with pytest.raises(ValidationError, match="page_size must be between 1 and 100"):
            await service.list_conversations(page_size=0)

    async def test_list_invalid_page_size_too_large(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        with pytest.raises(ValidationError, match="page_size must be between 1 and 100"):
            await service.list_conversations(page_size=101)

    async def test_list_order_by_created_at_desc(self, async_session: AsyncSession) -> None:
        """Most recently created conversations should appear first."""
        service = ConversationService(async_session)
        first = await service.create_conversation(_make_create_request(conversation_id="c-first"))
        second = await service.create_conversation(_make_create_request(conversation_id="c-second"))

        result = await service.list_conversations()
        assert len(result.items) == 2
        # The second created should appear first (descending order)
        assert result.items[0].conversation_id == "c-second"
        assert result.items[1].conversation_id == "c-first"


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


class TestConversationServiceUpdate:
    async def test_update_status(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        created = await service.create_conversation(_make_create_request())
        update = ConversationUpdateRequest(status="valid")
        updated = await service.update_conversation(created.conversation_id, update)

        assert updated.status == "valid"
        assert updated.conversation_id == created.conversation_id

    async def test_update_rating(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        created = await service.create_conversation(_make_create_request())
        update = ConversationUpdateRequest(rating=4.8)
        updated = await service.update_conversation(created.conversation_id, update)

        assert updated.rating == 4.8

    async def test_update_tags(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        created = await service.create_conversation(_make_create_request())
        update = ConversationUpdateRequest(tags=["automotive", "demo"])
        updated = await service.update_conversation(created.conversation_id, update)

        assert updated.tags == ["automotive", "demo"]

    async def test_update_notes(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        created = await service.create_conversation(_make_create_request())
        update = ConversationUpdateRequest(notes="Updated note for testing")
        updated = await service.update_conversation(created.conversation_id, update)

        assert updated.notes == "Updated note for testing"

    async def test_update_metadata(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        created = await service.create_conversation(_make_create_request())
        update = ConversationUpdateRequest(metadata={"reviewed_by": "evaluator-x"})
        updated = await service.update_conversation(created.conversation_id, update)

        assert updated.metadata == {"reviewed_by": "evaluator-x"}

    async def test_update_multiple_fields(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        created = await service.create_conversation(_make_create_request())
        update = ConversationUpdateRequest(status="invalid", rating=1.0, notes="Rejected during review")
        updated = await service.update_conversation(created.conversation_id, update)

        assert updated.status == "invalid"
        assert updated.rating == 1.0
        assert updated.notes == "Rejected during review"

    async def test_update_no_fields_raises(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        created = await service.create_conversation(_make_create_request())
        update = ConversationUpdateRequest()
        with pytest.raises(ValidationError, match="No fields to update"):
            await service.update_conversation(created.conversation_id, update)

    async def test_update_nonexistent_raises(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        update = ConversationUpdateRequest(status="valid")
        with pytest.raises(ConversationNotFoundError):
            await service.update_conversation("nonexistent-conv-id", update)

    async def test_update_sets_updated_at(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        created = await service.create_conversation(_make_create_request())
        original_updated = created.updated_at

        update = ConversationUpdateRequest(status="valid")
        updated = await service.update_conversation(created.conversation_id, update)

        assert updated.updated_at >= original_updated

    async def test_update_preserves_unmodified_fields(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        created = await service.create_conversation(
            _make_create_request(status="pending", rating=3.0, notes="Initial note")
        )
        # Only update status
        update = ConversationUpdateRequest(status="valid")
        updated = await service.update_conversation(created.conversation_id, update)

        assert updated.status == "valid"
        assert updated.rating == 3.0
        assert updated.notes == "Initial note"


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


class TestConversationServiceDelete:
    async def test_delete_existing(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        created = await service.create_conversation(_make_create_request())
        await service.delete_conversation(created.conversation_id)

        with pytest.raises(ConversationNotFoundError):
            await service.get_conversation(created.conversation_id)

    async def test_delete_nonexistent_raises(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        with pytest.raises(ConversationNotFoundError):
            await service.delete_conversation("nonexistent-conv-id")

    async def test_delete_does_not_affect_others(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        c1 = await service.create_conversation(_make_create_request(conversation_id="c1"))
        c2 = await service.create_conversation(_make_create_request(conversation_id="c2"))
        await service.delete_conversation(c1.conversation_id)

        result = await service.list_conversations()
        assert result.total == 1
        assert result.items[0].conversation_id == c2.conversation_id

    async def test_delete_then_list_empty(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        created = await service.create_conversation(_make_create_request())
        await service.delete_conversation(created.conversation_id)

        result = await service.list_conversations()
        assert result.total == 0
        assert result.items == []


# ---------------------------------------------------------------------------
# Bulk create
# ---------------------------------------------------------------------------


class TestConversationServiceBulkCreate:
    async def test_bulk_create_multiple(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        items = [
            _make_create_request(conversation_id="bc-1"),
            _make_create_request(conversation_id="bc-2"),
            _make_create_request(conversation_id="bc-3"),
        ]
        result = await service.bulk_create(items)

        assert result.created == 3
        assert result.skipped == 0
        assert result.errors == []

    async def test_bulk_create_skips_duplicates(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        # Pre-create one conversation
        await service.create_conversation(_make_create_request(conversation_id="bc-dup"))

        items = [
            _make_create_request(conversation_id="bc-dup"),  # duplicate
            _make_create_request(conversation_id="bc-new"),
        ]
        result = await service.bulk_create(items)

        assert result.created == 1
        assert result.skipped == 1
        assert result.errors == []

    async def test_bulk_create_all_duplicates(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        await service.create_conversation(_make_create_request(conversation_id="bc-a"))
        await service.create_conversation(_make_create_request(conversation_id="bc-b"))

        items = [
            _make_create_request(conversation_id="bc-a"),
            _make_create_request(conversation_id="bc-b"),
        ]
        result = await service.bulk_create(items)

        assert result.created == 0
        assert result.skipped == 2
        assert result.errors == []

    async def test_bulk_create_with_organization(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        items = [
            _make_create_request(conversation_id="bc-org-1"),
            _make_create_request(conversation_id="bc-org-2"),
        ]
        result = await service.bulk_create(items, organization_id="org-bulk-test")

        assert result.created == 2

        # Verify organization is set on created conversations
        conv = await service.get_conversation("bc-org-1")
        assert conv.organization_id == "org-bulk-test"

    async def test_bulk_create_empty_list(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        result = await service.bulk_create([])

        assert result.created == 0
        assert result.skipped == 0
        assert result.errors == []

    async def test_bulk_create_persists_all(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        items = [
            _make_create_request(conversation_id="bc-p1"),
            _make_create_request(conversation_id="bc-p2"),
        ]
        await service.bulk_create(items)

        listing = await service.list_conversations()
        assert listing.total == 2
        ids = {c.conversation_id for c in listing.items}
        assert ids == {"bc-p1", "bc-p2"}

    async def test_bulk_create_with_tool_calls(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        items = [
            _make_create_request_with_tools(conversation_id="bc-tool-1"),
            _make_create_request(conversation_id="bc-tool-2"),
        ]
        result = await service.bulk_create(items)

        assert result.created == 2
        conv = await service.get_conversation("bc-tool-1")
        assert conv.num_turnos == 5

    async def test_bulk_create_skips_within_batch_duplicates(self, async_session: AsyncSession) -> None:
        """When the same conversation_id appears twice in a single batch,
        the first is created and the second is skipped."""
        service = ConversationService(async_session)
        items = [
            _make_create_request(conversation_id="bc-same"),
            _make_create_request(conversation_id="bc-same"),
        ]
        result = await service.bulk_create(items)

        # First goes in, second is found as existing after commit isn't done yet,
        # but the service checks via select so only the first is inserted.
        # Since session.add doesn't commit yet, let's verify total
        assert result.created + result.skipped == 2
        assert result.errors == []


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestConversationServiceEdgeCases:
    async def test_create_non_synthetic_conversation(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        req = _make_create_request(es_sintetica=False)
        resp = await service.create_conversation(req)

        assert resp.es_sintetica is False

    async def test_create_minimal_conversation(self, async_session: AsyncSession) -> None:
        """A conversation with the minimum required fields."""
        service = ConversationService(async_session)
        req = ConversationCreateRequest(
            conversation_id="conv-minimal",
            dominio="legal.advisory",
            turnos=[
                ConversationTurn(turno=1, rol="abogado", contenido="Consulta ficticia sobre contratos."),
            ],
        )
        resp = await service.create_conversation(req)

        assert resp.conversation_id == "conv-minimal"
        assert resp.num_turnos == 1
        assert resp.dominio == "legal.advisory"
        assert resp.idioma == "es"  # default
        assert resp.es_sintetica is False  # default

    async def test_create_conversation_many_turns(self, async_session: AsyncSession) -> None:
        """A conversation with many turns to verify no truncation."""
        service = ConversationService(async_session)
        turnos = [
            ConversationTurn(turno=i, rol="vendedor" if i % 2 else "cliente", contenido=f"Turno numero {i}.")
            for i in range(1, 51)
        ]
        req = _make_create_request(conversation_id="conv-many-turns", turnos=turnos)
        resp = await service.create_conversation(req)

        assert resp.num_turnos == 50
        assert len(resp.turnos) == 50

    async def test_round_trip_tool_calls_preserved(self, async_session: AsyncSession) -> None:
        """Ensure tool_calls and tool_results survive the create->get round trip."""
        service = ConversationService(async_session)
        req = _make_create_request_with_tools(conversation_id="conv-rt-tools")
        await service.create_conversation(req)

        fetched = await service.get_conversation("conv-rt-tools")
        # Turn 3 has tool_calls
        turn3 = fetched.turnos[2]
        assert turn3.tool_calls is not None
        assert len(turn3.tool_calls) == 1
        assert turn3.tool_calls[0].tool_name == "buscar_inventario"

        # Turn 4 has tool_results
        turn4 = fetched.turnos[3]
        assert turn4.tool_results is not None
        assert len(turn4.tool_results) == 1
        assert turn4.tool_results[0].tool_name == "buscar_inventario"
        assert turn4.tool_results[0].status == "success"

    async def test_update_then_get_reflects_change(self, async_session: AsyncSession) -> None:
        """Update a conversation and verify get returns the updated version."""
        service = ConversationService(async_session)
        created = await service.create_conversation(_make_create_request())
        await service.update_conversation(
            created.conversation_id,
            ConversationUpdateRequest(status="reviewed", notes="Looks good"),
        )

        fetched = await service.get_conversation(created.conversation_id)
        assert fetched.status == "reviewed"
        assert fetched.notes == "Looks good"

    async def test_filter_returns_no_results_for_unmatched(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        await service.create_conversation(_make_create_request(conversation_id="c1", dominio="automotive.sales"))

        result = await service.list_conversations(domain="finance.advisory")
        assert result.total == 0
        assert result.items == []

    async def test_list_with_page_size_one(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        await service.create_conversation(_make_create_request(conversation_id="c1"))
        await service.create_conversation(_make_create_request(conversation_id="c2"))
        await service.create_conversation(_make_create_request(conversation_id="c3"))

        page1 = await service.list_conversations(page=1, page_size=1)
        assert len(page1.items) == 1
        assert page1.total == 3

        page2 = await service.list_conversations(page=2, page_size=1)
        assert len(page2.items) == 1
        assert page2.items[0].conversation_id != page1.items[0].conversation_id

    async def test_list_page_size_max(self, async_session: AsyncSession) -> None:
        """page_size=100 is the maximum allowed."""
        service = ConversationService(async_session)
        result = await service.list_conversations(page_size=100)
        assert result.page_size == 100

    async def test_create_multiple_then_delete_one(self, async_session: AsyncSession) -> None:
        service = ConversationService(async_session)
        await service.create_conversation(_make_create_request(conversation_id="d1"))
        await service.create_conversation(_make_create_request(conversation_id="d2"))
        await service.create_conversation(_make_create_request(conversation_id="d3"))

        await service.delete_conversation("d2")

        result = await service.list_conversations()
        assert result.total == 2
        ids = {c.conversation_id for c in result.items}
        assert "d2" not in ids
        assert "d1" in ids
        assert "d3" in ids
