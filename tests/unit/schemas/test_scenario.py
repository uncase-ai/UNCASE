"""Tests for ScenarioTemplate and ScenarioPack schemas."""

from __future__ import annotations

import pytest

from tests.factories import make_scenario_template
from uncase.schemas.scenario import ScenarioPack, ScenarioTemplate


class TestScenarioTemplate:
    """Tests for the ScenarioTemplate model."""

    def test_minimal_creation(self) -> None:
        scenario = ScenarioTemplate(
            name="test_scenario",
            description="A test scenario.",
            domain="automotive.sales",
            intent="Customer asks about a vehicle.",
        )
        assert scenario.name == "test_scenario"
        assert scenario.skill_level == "intermediate"
        assert scenario.weight == 1.0
        assert scenario.edge_case is False
        assert scenario.expected_tool_sequence == []
        assert scenario.flow_steps == []

    def test_factory_defaults(self) -> None:
        scenario = make_scenario_template()
        assert scenario.name == "brand_search"
        assert scenario.domain == "automotive.sales"
        assert scenario.weight == 5.0

    def test_factory_overrides(self) -> None:
        scenario = make_scenario_template(
            name="custom",
            skill_level="advanced",
            edge_case=True,
            weight=2.0,
        )
        assert scenario.name == "custom"
        assert scenario.skill_level == "advanced"
        assert scenario.edge_case is True
        assert scenario.weight == 2.0

    def test_skill_levels(self) -> None:
        for level in ("basic", "intermediate", "advanced"):
            s = make_scenario_template(skill_level=level)
            assert s.skill_level == level

    def test_invalid_skill_level(self) -> None:
        with pytest.raises(ValueError):
            make_scenario_template(skill_level="expert")

    def test_weight_must_be_positive(self) -> None:
        with pytest.raises(ValueError):
            make_scenario_template(weight=0.0)

    def test_weight_negative_rejected(self) -> None:
        with pytest.raises(ValueError):
            make_scenario_template(weight=-1.0)

    def test_tool_sequence(self) -> None:
        scenario = make_scenario_template(
            expected_tool_sequence=["buscar_inventario", "cotizar_vehiculo"],
        )
        assert scenario.expected_tool_sequence == ["buscar_inventario", "cotizar_vehiculo"]

    def test_tags(self) -> None:
        scenario = make_scenario_template(tags=["search", "tool_usage"])
        assert "search" in scenario.tags


class TestScenarioPack:
    """Tests for the ScenarioPack model."""

    def test_creation(self) -> None:
        scenarios = [make_scenario_template(), make_scenario_template(name="second", weight=3.0)]
        pack = ScenarioPack(
            id="test-pack",
            name="Test Pack",
            description="A test pack.",
            domain="automotive.sales",
            scenarios=scenarios,
        )
        assert pack.id == "test-pack"
        assert len(pack.scenarios) == 2

    def test_scenario_names(self) -> None:
        scenarios = [
            make_scenario_template(name="a"),
            make_scenario_template(name="b"),
        ]
        pack = ScenarioPack(
            id="test",
            name="Test",
            description="Test",
            domain="automotive.sales",
            scenarios=scenarios,
        )
        assert pack.scenario_names == ["a", "b"]

    def test_total_weight(self) -> None:
        scenarios = [
            make_scenario_template(weight=5.0),
            make_scenario_template(name="other", weight=3.0),
        ]
        pack = ScenarioPack(
            id="test",
            name="Test",
            description="Test",
            domain="automotive.sales",
            scenarios=scenarios,
        )
        assert pack.total_weight == 8.0

    def test_requires_at_least_one_scenario(self) -> None:
        with pytest.raises(ValueError):
            ScenarioPack(
                id="empty",
                name="Empty",
                description="Empty",
                domain="automotive.sales",
                scenarios=[],
            )
