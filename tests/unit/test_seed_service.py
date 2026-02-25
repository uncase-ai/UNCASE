"""Tests for the seed CRUD service layer."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import pytest

import uncase.schemas.seed_api as _seed_api_mod
from uncase.exceptions import SeedNotFoundError, ValidationError
from uncase.schemas.seed import MetricasCalidad, ParametrosFactuales, PasosTurnos, Privacidad
from uncase.schemas.seed_api import SeedCreateRequest, SeedUpdateRequest
from uncase.services.seed import SeedService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

# SeedResponse uses TYPE_CHECKING import for datetime; inject it and rebuild.
_seed_api_mod.datetime = datetime  # type: ignore[attr-defined]
_seed_api_mod.SeedResponse.model_rebuild()
_seed_api_mod.SeedListResponse.model_rebuild()


def _make_create_request(**overrides: object) -> SeedCreateRequest:
    """Build a valid SeedCreateRequest with fictional defaults."""
    defaults: dict[str, object] = {
        "dominio": "automotive.sales",
        "idioma": "es",
        "objetivo": "Consulta ficticia sobre vehiculos de prueba",
        "tono": "profesional",
        "roles": ["vendedor", "cliente"],
        "descripcion_roles": {
            "vendedor": "Asesor de ventas ficticio",
            "cliente": "Cliente ficticio",
        },
        "pasos_turnos": PasosTurnos(
            turnos_min=6,
            turnos_max=20,
            flujo_esperado=["saludo", "consulta", "resolucion"],
        ),
        "parametros_factuales": ParametrosFactuales(
            contexto="Concesionario ficticio de prueba",
            restricciones=["Restriccion de prueba"],
            herramientas=["crm"],
            metadata={},
        ),
        "privacidad": Privacidad(),
        "metricas_calidad": MetricasCalidad(),
    }
    defaults.update(overrides)
    return SeedCreateRequest(**defaults)  # type: ignore[arg-type]


class TestSeedServiceCreate:
    async def test_create_seed_returns_response(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        req = _make_create_request()
        resp = await service.create_seed(req)

        assert resp.id is not None
        assert resp.dominio == "automotive.sales"
        assert resp.idioma == "es"
        assert resp.objetivo == "Consulta ficticia sobre vehiculos de prueba"
        assert resp.tono == "profesional"
        assert resp.roles == ["vendedor", "cliente"]

    async def test_create_seed_with_organization(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        req = _make_create_request()
        resp = await service.create_seed(req, organization_id="org-abc123")

        assert resp.organization_id == "org-abc123"

    async def test_create_seed_persists_to_db(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        req = _make_create_request()
        resp = await service.create_seed(req)

        fetched = await service.get_seed(resp.id)
        assert fetched.id == resp.id
        assert fetched.dominio == resp.dominio

    async def test_create_seed_with_etiquetas(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        req = _make_create_request(etiquetas=["prueba", "demo"])
        resp = await service.create_seed(req)

        assert resp.etiquetas == ["prueba", "demo"]

    async def test_create_seed_different_domain(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        req = _make_create_request(dominio="medical.consultation")
        resp = await service.create_seed(req)

        assert resp.dominio == "medical.consultation"


class TestSeedServiceGet:
    async def test_get_existing_seed(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        created = await service.create_seed(_make_create_request())
        found = await service.get_seed(created.id)

        assert found.id == created.id
        assert found.dominio == created.dominio

    async def test_get_nonexistent_seed_raises(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        with pytest.raises(SeedNotFoundError):
            await service.get_seed("nonexistent-id")


class TestSeedServiceList:
    async def test_list_empty(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        result = await service.list_seeds()

        assert result.items == []
        assert result.total == 0
        assert result.page == 1
        assert result.page_size == 20

    async def test_list_returns_all(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        await service.create_seed(_make_create_request())
        await service.create_seed(_make_create_request(dominio="medical.consultation"))
        result = await service.list_seeds()

        assert result.total == 2
        assert len(result.items) == 2

    async def test_list_filter_by_domain(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        await service.create_seed(_make_create_request(dominio="automotive.sales"))
        await service.create_seed(_make_create_request(dominio="medical.consultation"))
        result = await service.list_seeds(domain="automotive.sales")

        assert result.total == 1
        assert result.items[0].dominio == "automotive.sales"

    async def test_list_filter_by_organization(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        await service.create_seed(_make_create_request(), organization_id="org-a")
        await service.create_seed(_make_create_request(), organization_id="org-b")
        result = await service.list_seeds(organization_id="org-a")

        assert result.total == 1
        assert result.items[0].organization_id == "org-a"

    async def test_list_pagination(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        for _ in range(5):
            await service.create_seed(_make_create_request())

        page1 = await service.list_seeds(page=1, page_size=2)
        assert len(page1.items) == 2
        assert page1.total == 5
        assert page1.page == 1

        page2 = await service.list_seeds(page=2, page_size=2)
        assert len(page2.items) == 2

        page3 = await service.list_seeds(page=3, page_size=2)
        assert len(page3.items) == 1

    async def test_list_invalid_page_raises(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        with pytest.raises(ValidationError, match="Page must be >= 1"):
            await service.list_seeds(page=0)

    async def test_list_invalid_page_size_too_small(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        with pytest.raises(ValidationError, match="page_size must be between 1 and 100"):
            await service.list_seeds(page_size=0)

    async def test_list_invalid_page_size_too_large(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        with pytest.raises(ValidationError, match="page_size must be between 1 and 100"):
            await service.list_seeds(page_size=101)


class TestSeedServiceUpdate:
    async def test_update_objetivo(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        created = await service.create_seed(_make_create_request())
        update = SeedUpdateRequest(objetivo="Nuevo objetivo ficticio")
        updated = await service.update_seed(created.id, update)

        assert updated.objetivo == "Nuevo objetivo ficticio"
        assert updated.id == created.id

    async def test_update_tono(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        created = await service.create_seed(_make_create_request())
        update = SeedUpdateRequest(tono="informal")
        updated = await service.update_seed(created.id, update)

        assert updated.tono == "informal"

    async def test_update_no_fields_raises(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        created = await service.create_seed(_make_create_request())
        update = SeedUpdateRequest()
        with pytest.raises(ValidationError, match="No fields to update"):
            await service.update_seed(created.id, update)

    async def test_update_nonexistent_seed_raises(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        update = SeedUpdateRequest(tono="casual")
        with pytest.raises(SeedNotFoundError):
            await service.update_seed("nonexistent-id", update)

    async def test_update_domain_validates(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        created = await service.create_seed(_make_create_request())
        update = SeedUpdateRequest(dominio="medical.consultation")
        updated = await service.update_seed(created.id, update)

        assert updated.dominio == "medical.consultation"

    async def test_update_to_invalid_domain_raises(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        created = await service.create_seed(_make_create_request())
        update = SeedUpdateRequest(dominio="invalid.domain")
        with pytest.raises(ValidationError):
            await service.update_seed(created.id, update)

    async def test_update_etiquetas(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        created = await service.create_seed(_make_create_request())
        update = SeedUpdateRequest(etiquetas=["nueva", "etiqueta"])
        updated = await service.update_seed(created.id, update)

        assert updated.etiquetas == ["nueva", "etiqueta"]

    async def test_update_sets_updated_at(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        created = await service.create_seed(_make_create_request())
        original_updated = created.updated_at
        update = SeedUpdateRequest(tono="casual")
        updated = await service.update_seed(created.id, update)

        assert updated.updated_at >= original_updated


class TestSeedServiceDelete:
    async def test_delete_existing_seed(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        created = await service.create_seed(_make_create_request())
        await service.delete_seed(created.id)

        with pytest.raises(SeedNotFoundError):
            await service.get_seed(created.id)

    async def test_delete_nonexistent_seed_raises(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        with pytest.raises(SeedNotFoundError):
            await service.delete_seed("nonexistent-id")

    async def test_delete_does_not_affect_other_seeds(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        s1 = await service.create_seed(_make_create_request())
        s2 = await service.create_seed(_make_create_request())
        await service.delete_seed(s1.id)

        result = await service.list_seeds()
        assert result.total == 1
        assert result.items[0].id == s2.id


class TestSeedServiceHelpers:
    async def test_to_schema_dict(self, async_session: AsyncSession) -> None:
        service = SeedService(async_session)
        created = await service.create_seed(_make_create_request())
        seed_model = await service._get_seed_or_raise(created.id)
        schema_dict = SeedService._to_schema_dict(seed_model)

        assert schema_dict["dominio"] == "automotive.sales"
        assert schema_dict["idioma"] == "es"
        assert "roles" in schema_dict
        assert "pasos_turnos" in schema_dict
