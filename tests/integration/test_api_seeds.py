"""Integration tests for the Seeds API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from uncase.db.models.seed import SeedModel

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


def _seed_create_payload(**overrides: object) -> dict[str, object]:
    """Build a valid SeedCreateRequest payload with fictional defaults."""
    payload: dict[str, object] = {
        "dominio": "automotive.sales",
        "idioma": "es",
        "objetivo": "Consulta ficticia sobre vehiculos de prueba",
        "tono": "profesional",
        "roles": ["vendedor", "cliente"],
        "descripcion_roles": {
            "vendedor": "Asesor de ventas ficticio",
            "cliente": "Cliente ficticio interesado",
        },
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 20,
            "flujo_esperado": ["saludo", "consulta", "resolucion"],
        },
        "parametros_factuales": {
            "contexto": "Concesionario ficticio de prueba",
            "restricciones": ["Solo vehiculos nuevos"],
            "herramientas": ["crm"],
            "metadata": {},
        },
    }
    payload.update(overrides)
    return payload


@pytest.fixture()
async def sample_seed(async_session: AsyncSession) -> SeedModel:
    """Create a sample seed directly in the DB for read tests."""
    seed = SeedModel(
        id="seed-test-001",
        dominio="automotive.sales",
        idioma="es",
        version="1.0",
        etiquetas=["test", "fictional"],
        objetivo="Consulta ficticia sobre vehiculos",
        tono="profesional",
        roles=["vendedor", "cliente"],
        descripcion_roles={
            "vendedor": "Asesor ficticio",
            "cliente": "Cliente ficticio",
        },
        pasos_turnos={
            "turnos_min": 6,
            "turnos_max": 20,
            "flujo_esperado": ["saludo", "consulta", "resolucion"],
        },
        parametros_factuales={
            "contexto": "Concesionario ficticio",
            "restricciones": ["Solo vehiculos nuevos"],
            "herramientas": ["crm"],
            "metadata": {},
        },
        privacidad={
            "nivel": "alto",
            "pii_tolerance": 0.0,
            "anonimizacion": True,
            "dp_epsilon": 8.0,
        },
        metricas_calidad={
            "rouge_l_min": 0.65,
            "fidelidad_min": 0.90,
            "diversidad_min": 0.55,
            "coherencia_min": 0.85,
        },
        organization_id=None,
    )
    async_session.add(seed)
    await async_session.commit()
    await async_session.refresh(seed)
    return seed


@pytest.fixture()
async def second_seed(async_session: AsyncSession) -> SeedModel:
    """Create a second seed in a different domain."""
    seed = SeedModel(
        id="seed-test-002",
        dominio="medical.consultation",
        idioma="es",
        version="1.0",
        etiquetas=["test", "medical"],
        objetivo="Consulta medica ficticia",
        tono="empatico",
        roles=["medico", "paciente"],
        descripcion_roles={
            "medico": "Medico ficticio",
            "paciente": "Paciente ficticio",
        },
        pasos_turnos={
            "turnos_min": 4,
            "turnos_max": 15,
            "flujo_esperado": ["saludo", "anamnesis", "diagnostico"],
        },
        parametros_factuales={
            "contexto": "Clinica ficticia de prueba",
            "restricciones": ["Sin PII"],
            "herramientas": [],
            "metadata": {},
        },
        privacidad={
            "nivel": "alto",
            "pii_tolerance": 0.0,
            "anonimizacion": True,
            "dp_epsilon": 8.0,
        },
        metricas_calidad={
            "rouge_l_min": 0.65,
            "fidelidad_min": 0.90,
            "diversidad_min": 0.55,
            "coherencia_min": 0.85,
        },
        organization_id=None,
    )
    async_session.add(seed)
    await async_session.commit()
    await async_session.refresh(seed)
    return seed


@pytest.mark.integration
class TestListSeeds:
    """Test GET /api/v1/seeds."""

    async def test_list_empty(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/seeds")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1

    async def test_list_with_seed(self, client: AsyncClient, sample_seed: SeedModel) -> None:
        response = await client.get("/api/v1/seeds")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == "seed-test-001"
        assert data["items"][0]["dominio"] == "automotive.sales"

    async def test_filter_by_domain(self, client: AsyncClient, sample_seed: SeedModel, second_seed: SeedModel) -> None:
        response = await client.get("/api/v1/seeds", params={"domain": "medical.consultation"})
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["dominio"] == "medical.consultation"

    async def test_filter_by_domain_no_results(self, client: AsyncClient, sample_seed: SeedModel) -> None:
        response = await client.get("/api/v1/seeds", params={"domain": "finance.advisory"})
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_pagination(self, client: AsyncClient, sample_seed: SeedModel, second_seed: SeedModel) -> None:
        response = await client.get("/api/v1/seeds", params={"page": 1, "page_size": 1})
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 1
        assert data["page"] == 1
        assert data["page_size"] == 1


@pytest.mark.integration
class TestCreateSeed:
    """Test POST /api/v1/seeds."""

    async def test_create_seed(self, client: AsyncClient) -> None:
        payload = _seed_create_payload()
        response = await client.post("/api/v1/seeds", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["dominio"] == "automotive.sales"
        assert data["idioma"] == "es"
        assert "id" in data
        assert "created_at" in data

    async def test_create_seed_custom_domain(self, client: AsyncClient) -> None:
        payload = _seed_create_payload(
            dominio="legal.advisory",
            objetivo="Asesoria legal ficticia de prueba",
            roles=["abogado", "cliente"],
            descripcion_roles={"abogado": "Abogado ficticio", "cliente": "Cliente ficticio"},
            parametros_factuales={
                "contexto": "Bufete ficticio",
                "restricciones": [],
                "herramientas": [],
                "metadata": {},
            },
        )
        response = await client.post("/api/v1/seeds", json=payload)
        assert response.status_code == 201
        assert response.json()["dominio"] == "legal.advisory"

    async def test_create_seed_missing_required_field(self, client: AsyncClient) -> None:
        payload = _seed_create_payload()
        del payload["objetivo"]  # type: ignore[arg-type]
        response = await client.post("/api/v1/seeds", json=payload)
        assert response.status_code == 422

    async def test_create_seed_too_few_roles(self, client: AsyncClient) -> None:
        payload = _seed_create_payload(roles=["solo_uno"])
        response = await client.post("/api/v1/seeds", json=payload)
        assert response.status_code == 422


@pytest.mark.integration
class TestGetSeed:
    """Test GET /api/v1/seeds/{seed_id}."""

    async def test_get_existing(self, client: AsyncClient, sample_seed: SeedModel) -> None:
        response = await client.get(f"/api/v1/seeds/{sample_seed.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_seed.id
        assert data["dominio"] == "automotive.sales"

    async def test_get_nonexistent(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/seeds/nonexistent-seed-id")
        assert response.status_code == 404


@pytest.mark.integration
class TestUpdateSeed:
    """Test PUT /api/v1/seeds/{seed_id}."""

    async def test_update_objetivo(self, client: AsyncClient, sample_seed: SeedModel) -> None:
        response = await client.put(
            f"/api/v1/seeds/{sample_seed.id}",
            json={"objetivo": "Objetivo ficticio actualizado"},
        )
        assert response.status_code == 200
        assert response.json()["objetivo"] == "Objetivo ficticio actualizado"

    async def test_update_tono(self, client: AsyncClient, sample_seed: SeedModel) -> None:
        response = await client.put(
            f"/api/v1/seeds/{sample_seed.id}",
            json={"tono": "informal"},
        )
        assert response.status_code == 200
        assert response.json()["tono"] == "informal"

    async def test_update_nonexistent(self, client: AsyncClient) -> None:
        response = await client.put(
            "/api/v1/seeds/no-such-seed",
            json={"tono": "casual"},
        )
        assert response.status_code == 404

    async def test_update_empty_body(self, client: AsyncClient, sample_seed: SeedModel) -> None:
        response = await client.put(
            f"/api/v1/seeds/{sample_seed.id}",
            json={},
        )
        # Service raises ValidationError("No fields to update")
        assert response.status_code == 422


@pytest.mark.integration
class TestDeleteSeed:
    """Test DELETE /api/v1/seeds/{seed_id}."""

    async def test_delete_existing(self, client: AsyncClient, sample_seed: SeedModel) -> None:
        response = await client.delete(f"/api/v1/seeds/{sample_seed.id}")
        assert response.status_code == 204

        # Verify it's gone
        get_response = await client.get(f"/api/v1/seeds/{sample_seed.id}")
        assert get_response.status_code == 404

    async def test_delete_nonexistent(self, client: AsyncClient) -> None:
        response = await client.delete("/api/v1/seeds/no-such-seed")
        assert response.status_code == 404
