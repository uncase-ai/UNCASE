"""Exhaustive tests for SeedSchema v1."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from tests.factories import make_seed
from uncase.schemas.seed import SUPPORTED_DOMAINS, PasosTurnos, SeedSchema


class TestSeedSchemaValid:
    """Tests for valid seed creation."""

    def test_create_minimal_seed(self) -> None:
        seed = make_seed()
        assert seed.dominio == "automotive.sales"
        assert seed.version == "1.0"
        assert len(seed.roles) >= 2

    @pytest.mark.parametrize("domain", sorted(SUPPORTED_DOMAINS))
    def test_all_supported_domains(self, domain: str) -> None:
        seed = make_seed(dominio=domain)
        assert seed.dominio == domain

    def test_seed_id_auto_generated(self) -> None:
        seed = make_seed()
        assert seed.seed_id
        assert len(seed.seed_id) == 32

    def test_custom_seed_id(self) -> None:
        seed = make_seed(seed_id="custom_id")
        assert seed.seed_id == "custom_id"

    def test_multiple_roles(self) -> None:
        seed = make_seed(roles=["vendedor", "cliente", "gerente"])
        assert len(seed.roles) == 3

    def test_roundtrip_serialization(self) -> None:
        seed = make_seed()
        data = seed.model_dump()
        restored = SeedSchema.model_validate(data)
        assert restored.seed_id == seed.seed_id
        assert restored.dominio == seed.dominio
        assert restored.roles == seed.roles

    def test_json_roundtrip(self) -> None:
        seed = make_seed()
        json_str = seed.model_dump_json()
        restored = SeedSchema.model_validate_json(json_str)
        assert restored.seed_id == seed.seed_id


class TestSeedSchemaValidation:
    """Tests for schema validation errors."""

    def test_unsupported_domain(self) -> None:
        with pytest.raises(ValidationError, match="Unsupported domain"):
            make_seed(dominio="invalid.domain")

    def test_roles_minimum_two(self) -> None:
        with pytest.raises(ValidationError):
            make_seed(roles=["solo_role"])

    def test_roles_empty_rejected(self) -> None:
        with pytest.raises(ValidationError):
            make_seed(roles=[])

    def test_flujo_esperado_minimum_one(self) -> None:
        with pytest.raises(ValidationError):
            PasosTurnos(turnos_min=5, turnos_max=10, flujo_esperado=[])

    def test_turnos_min_less_than_max(self) -> None:
        with pytest.raises(ValidationError, match="turnos_min"):
            PasosTurnos(turnos_min=10, turnos_max=10, flujo_esperado=["step"])

    def test_turnos_min_greater_than_max(self) -> None:
        with pytest.raises(ValidationError, match="turnos_min"):
            PasosTurnos(turnos_min=20, turnos_max=10, flujo_esperado=["step"])

    def test_pii_consistency_detected_but_not_removed(self) -> None:
        from uncase.schemas.seed import Privacidad

        with pytest.raises(ValidationError, match="PII fields were detected"):
            make_seed(
                privacidad=Privacidad(
                    pii_eliminado=False,
                    campos_sensibles_detectados=["nombre"],
                )
            )

    def test_pii_consistency_detected_and_removed_ok(self) -> None:
        from uncase.schemas.seed import Privacidad

        seed = make_seed(
            privacidad=Privacidad(
                pii_eliminado=True,
                campos_sensibles_detectados=["nombre"],
            )
        )
        assert seed.privacidad.pii_eliminado is True

    def test_objetivo_required(self) -> None:
        with pytest.raises(ValidationError):
            SeedSchema(
                dominio="automotive.sales",
                roles=["a", "b"],
                pasos_turnos=PasosTurnos(turnos_min=1, turnos_max=5, flujo_esperado=["s"]),
                parametros_factuales={"contexto": "test"},
            )  # type: ignore[call-arg]
