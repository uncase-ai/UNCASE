"""Tests for domain seed packages — validates all curated seeds."""

from __future__ import annotations

import pytest

from uncase.domains.seed_packages.automotive import AUTOMOTIVE_SEEDS
from uncase.domains.seed_packages.finance import FINANCE_SEEDS
from uncase.domains.seed_packages.medical import MEDICAL_SEEDS

REQUIRED_FIELDS = {
    "dominio",
    "idioma",
    "roles",
    "descripcion_roles",
    "objetivo",
    "tono",
    "pasos_turnos",
    "parametros_factuales",
}


class TestAutomotiveSeeds:
    """Validate automotive domain seed package."""

    def test_has_50_seeds(self) -> None:
        assert len(AUTOMOTIVE_SEEDS) == 50

    def test_correct_domain(self) -> None:
        for seed in AUTOMOTIVE_SEEDS:
            assert seed["dominio"] == "automotive.sales"

    @pytest.mark.parametrize("seed", AUTOMOTIVE_SEEDS[:5], ids=lambda s: str(s.get("objetivo", ""))[:50])
    def test_required_fields(self, seed: dict[str, object]) -> None:
        for field in REQUIRED_FIELDS:
            assert field in seed, f"Missing field '{field}' in seed: {seed.get('objetivo', 'unknown')}"

    def test_roles_are_list(self) -> None:
        for seed in AUTOMOTIVE_SEEDS:
            assert isinstance(seed["roles"], list)
            assert len(seed["roles"]) >= 2

    def test_pasos_turnos_structure(self) -> None:
        for seed in AUTOMOTIVE_SEEDS:
            pt = seed["pasos_turnos"]
            assert isinstance(pt, dict)
            assert "turnos_min" in pt
            assert "turnos_max" in pt
            assert pt["turnos_min"] <= pt["turnos_max"]  # type: ignore[operator]

    def test_no_pii(self) -> None:
        """Ensure no real PII in seed data."""
        pii_patterns = ["@gmail", "@hotmail", "+52", "+1-", "SSN", "CURP"]
        for seed in AUTOMOTIVE_SEEDS:
            text = str(seed)
            for pattern in pii_patterns:
                assert pattern not in text, f"Possible PII found: {pattern}"


class TestMedicalSeeds:
    """Validate medical domain seed package."""

    def test_has_50_seeds(self) -> None:
        assert len(MEDICAL_SEEDS) == 50

    def test_correct_domain(self) -> None:
        for seed in MEDICAL_SEEDS:
            assert seed["dominio"] == "medical.consultation"

    @pytest.mark.parametrize("seed", MEDICAL_SEEDS[:5], ids=lambda s: str(s.get("objetivo", ""))[:50])
    def test_required_fields(self, seed: dict[str, object]) -> None:
        for field in REQUIRED_FIELDS:
            assert field in seed, f"Missing field '{field}'"

    def test_roles_are_list(self) -> None:
        for seed in MEDICAL_SEEDS:
            assert isinstance(seed["roles"], list)
            assert len(seed["roles"]) >= 2


class TestFinanceSeeds:
    """Validate finance domain seed package."""

    def test_has_50_seeds(self) -> None:
        assert len(FINANCE_SEEDS) == 50

    def test_correct_domain(self) -> None:
        for seed in FINANCE_SEEDS:
            assert seed["dominio"] == "finance.advisory"

    @pytest.mark.parametrize("seed", FINANCE_SEEDS[:5], ids=lambda s: str(s.get("objetivo", ""))[:50])
    def test_required_fields(self, seed: dict[str, object]) -> None:
        for field in REQUIRED_FIELDS:
            assert field in seed, f"Missing field '{field}'"

    def test_roles_are_list(self) -> None:
        for seed in FINANCE_SEEDS:
            assert isinstance(seed["roles"], list)
            assert len(seed["roles"]) >= 2


class TestCrossDomainConsistency:
    """Ensure consistency across all seed packages."""

    @pytest.mark.parametrize(
        "package,domain",
        [
            (AUTOMOTIVE_SEEDS, "automotive.sales"),
            (MEDICAL_SEEDS, "medical.consultation"),
            (FINANCE_SEEDS, "finance.advisory"),
        ],
    )
    def test_all_have_valid_language(self, package: list[dict[str, object]], domain: str) -> None:
        for seed in package:
            assert seed["idioma"] in ("es", "en"), f"Invalid language in {domain} seed"

    @pytest.mark.parametrize(
        "package",
        [AUTOMOTIVE_SEEDS, MEDICAL_SEEDS, FINANCE_SEEDS],
    )
    def test_all_have_descripcion_roles(self, package: list[dict[str, object]]) -> None:
        for seed in package:
            desc = seed["descripcion_roles"]
            assert isinstance(desc, dict)
            assert len(desc) >= 2
