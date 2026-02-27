"""Tests for scenario integration in the LiteLLM generator."""

from __future__ import annotations

import random

from tests.factories import make_scenario_template, make_seed
from uncase.core.generator.litellm_generator import (
    _build_scenario_block,
    _build_system_prompt,
    _select_scenario,
)


class TestSelectScenario:
    """Tests for weighted scenario selection."""

    def test_returns_none_without_scenarios(self) -> None:
        seed = make_seed()
        assert _select_scenario(seed) is None

    def test_returns_scenario_when_present(self) -> None:
        seed = make_seed(scenarios=[make_scenario_template()])
        result = _select_scenario(seed)
        assert result is not None
        assert result.name == "brand_search"

    def test_single_scenario_always_selected(self) -> None:
        scenario = make_scenario_template(name="only_one")
        seed = make_seed(scenarios=[scenario])
        for _ in range(10):
            result = _select_scenario(seed)
            assert result is not None
            assert result.name == "only_one"

    def test_weighted_selection_distribution(self) -> None:
        """Higher-weight scenarios are selected more frequently."""
        heavy = make_scenario_template(name="heavy", weight=9.0)
        light = make_scenario_template(name="light", weight=1.0)
        seed = make_seed(scenarios=[heavy, light])

        rng = random.Random(42)  # noqa: S311
        counts: dict[str, int] = {"heavy": 0, "light": 0}
        for _ in range(1000):
            result = _select_scenario(seed, rng=rng)
            assert result is not None
            counts[result.name] += 1

        # Heavy should be selected ~90% of the time
        assert counts["heavy"] > 800
        assert counts["light"] > 50  # But light should still appear

    def test_deterministic_with_fixed_rng(self) -> None:
        scenarios = [
            make_scenario_template(name="a", weight=1.0),
            make_scenario_template(name="b", weight=1.0),
            make_scenario_template(name="c", weight=1.0),
        ]
        seed = make_seed(scenarios=scenarios)

        rng1 = random.Random(12345)  # noqa: S311
        rng2 = random.Random(12345)  # noqa: S311

        results1 = [_select_scenario(seed, rng=rng1) for _ in range(20)]
        results2 = [_select_scenario(seed, rng=rng2) for _ in range(20)]

        names1 = [r.name for r in results1 if r]
        names2 = [r.name for r in results2 if r]
        assert names1 == names2


class TestBuildScenarioBlock:
    """Tests for scenario prompt block generation."""

    def test_basic_scenario_block(self) -> None:
        scenario = make_scenario_template()
        block = _build_scenario_block(scenario)
        assert "## Scenario Archetype" in block
        assert "brand_search" in block
        assert scenario.intent in block

    def test_skill_level_in_block(self) -> None:
        for level in ("basic", "intermediate", "advanced"):
            scenario = make_scenario_template(skill_level=level)
            block = _build_scenario_block(scenario)
            assert level in block

    def test_tool_sequence_in_block(self) -> None:
        scenario = make_scenario_template(
            expected_tool_sequence=["buscar_inventario", "cotizar_vehiculo"],
        )
        block = _build_scenario_block(scenario)
        assert "buscar_inventario" in block
        assert "cotizar_vehiculo" in block
        assert "→" in block  # Arrow between tools

    def test_empty_tool_sequence(self) -> None:
        scenario = make_scenario_template(expected_tool_sequence=[])
        block = _build_scenario_block(scenario)
        assert "Expected tool usage order" not in block

    def test_edge_case_flag_in_block(self) -> None:
        scenario = make_scenario_template(edge_case=True)
        block = _build_scenario_block(scenario)
        assert "Edge case scenario" in block
        assert "NON-happy-path" in block

    def test_no_edge_case_when_false(self) -> None:
        scenario = make_scenario_template(edge_case=False)
        block = _build_scenario_block(scenario)
        assert "Edge case" not in block


class TestSystemPromptWithScenario:
    """Tests for scenario injection into the system prompt."""

    def test_prompt_without_scenario(self) -> None:
        seed = make_seed()
        prompt = _build_system_prompt(seed)
        assert "Scenario Archetype" not in prompt
        assert "automotive" in prompt.lower() or "sales" in prompt.lower()

    def test_prompt_with_scenario(self) -> None:
        scenario = make_scenario_template()
        seed = make_seed(scenarios=[scenario])
        prompt = _build_system_prompt(seed, scenario=scenario)
        assert "## Scenario Archetype" in prompt
        assert "brand_search" in prompt
        assert scenario.intent in prompt

    def test_scenario_flow_overrides_seed_flow(self) -> None:
        """When scenario has flow_steps, they override seed's flujo_esperado."""
        scenario = make_scenario_template(
            flow_steps=["Step Alpha", "Step Beta", "Step Gamma"],
        )
        seed = make_seed(scenarios=[scenario])
        prompt = _build_system_prompt(seed, scenario=scenario)
        assert "Step Alpha" in prompt
        assert "Step Beta" in prompt
        # Seed's default flow should NOT be present
        assert "saludo" not in prompt
        assert "consulta" not in prompt

    def test_empty_scenario_flow_uses_seed_flow(self) -> None:
        """When scenario has empty flow_steps, seed's flujo_esperado is used."""
        scenario = make_scenario_template(flow_steps=[])
        seed = make_seed(scenarios=[scenario])
        prompt = _build_system_prompt(seed, scenario=scenario)
        # Seed's default flow should be present
        assert "saludo" in prompt
        assert "consulta" in prompt
