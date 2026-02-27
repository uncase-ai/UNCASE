"""Tests for built-in domain scenario packs."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from uncase.domains.scenario_packs import get_scenario_pack, list_scenario_packs

if TYPE_CHECKING:
    from uncase.schemas.scenario import ScenarioPack


class TestScenarioPackLoading:
    """Tests for the scenario pack registry."""

    def test_list_all_packs(self) -> None:
        packs = list_scenario_packs()
        assert len(packs) == 6
        domains = {p.domain for p in packs}
        assert domains == {
            "automotive.sales",
            "medical.consultation",
            "finance.advisory",
            "legal.advisory",
            "industrial.support",
            "education.tutoring",
        }

    def test_get_pack_by_domain(self) -> None:
        for domain in [
            "automotive.sales",
            "medical.consultation",
            "finance.advisory",
            "legal.advisory",
            "industrial.support",
            "education.tutoring",
        ]:
            pack = get_scenario_pack(domain)
            assert pack is not None
            assert pack.domain == domain

    def test_get_unknown_domain_returns_none(self) -> None:
        assert get_scenario_pack("nonexistent.domain") is None

    def test_packs_are_cached(self) -> None:
        """Repeated calls return the same pack instances."""
        pack1 = get_scenario_pack("automotive.sales")
        pack2 = get_scenario_pack("automotive.sales")
        assert pack1 is pack2


class TestAutomotiveScenarioPack:
    """Tests for the automotive sales scenario pack."""

    @pytest.fixture()
    def pack(self) -> ScenarioPack:
        result = get_scenario_pack("automotive.sales")
        assert result is not None
        return result

    def test_scenario_count(self, pack: ScenarioPack) -> None:
        assert len(pack.scenarios) == 12

    def test_has_edge_cases(self, pack: ScenarioPack) -> None:
        edge_cases = [s for s in pack.scenarios if s.edge_case]
        assert len(edge_cases) >= 4

    def test_has_happy_path(self, pack: ScenarioPack) -> None:
        happy = [s for s in pack.scenarios if not s.edge_case]
        assert len(happy) >= 5

    def test_all_scenarios_have_domain(self, pack: ScenarioPack) -> None:
        for s in pack.scenarios:
            assert s.domain == "automotive.sales"

    def test_weights_are_positive(self, pack: ScenarioPack) -> None:
        for s in pack.scenarios:
            assert s.weight > 0

    def test_full_purchase_flow_is_advanced(self, pack: ScenarioPack) -> None:
        flow = next(s for s in pack.scenarios if s.name == "full_purchase_flow")
        assert flow.skill_level == "advanced"
        assert len(flow.expected_tool_sequence) >= 2

    def test_unique_names(self, pack: ScenarioPack) -> None:
        names = pack.scenario_names
        assert len(names) == len(set(names))


class TestAllPacksStructure:
    """Structural tests that apply to ALL scenario packs."""

    @pytest.fixture(params=[
        "automotive.sales",
        "medical.consultation",
        "finance.advisory",
        "legal.advisory",
        "industrial.support",
        "education.tutoring",
    ])
    def pack(self, request: pytest.FixtureRequest) -> ScenarioPack:
        result = get_scenario_pack(request.param)
        assert result is not None
        return result

    def test_has_at_least_6_scenarios(self, pack: ScenarioPack) -> None:
        assert len(pack.scenarios) >= 6

    def test_has_edge_cases(self, pack: ScenarioPack) -> None:
        edge_cases = [s for s in pack.scenarios if s.edge_case]
        assert len(edge_cases) >= 2, f"{pack.domain} needs at least 2 edge cases"

    def test_has_varied_skill_levels(self, pack: ScenarioPack) -> None:
        levels = {s.skill_level for s in pack.scenarios}
        assert len(levels) >= 2, f"{pack.domain} needs varied skill levels"

    def test_unique_scenario_names(self, pack: ScenarioPack) -> None:
        names = pack.scenario_names
        assert len(names) == len(set(names)), f"{pack.domain} has duplicate names"

    def test_all_scenarios_have_intent(self, pack: ScenarioPack) -> None:
        for s in pack.scenarios:
            assert len(s.intent) > 10, f"Scenario '{s.name}' has too short an intent"

    def test_all_scenarios_have_description(self, pack: ScenarioPack) -> None:
        for s in pack.scenarios:
            assert len(s.description) > 10

    def test_total_weight_positive(self, pack: ScenarioPack) -> None:
        assert pack.total_weight > 0

    def test_pack_metadata_complete(self, pack: ScenarioPack) -> None:
        assert pack.id
        assert pack.name
        assert pack.description
        assert pack.version
