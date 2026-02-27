"""Tests for SeedSchema with scenarios field integration."""

from __future__ import annotations

import warnings

from tests.factories import make_scenario_template, make_seed
from uncase.schemas.seed import ParametrosFactuales


class TestSeedSchemaWithScenarios:
    """Tests for the optional scenarios field on SeedSchema."""

    def test_seed_without_scenarios(self) -> None:
        seed = make_seed()
        assert seed.scenarios is None

    def test_seed_with_scenarios(self) -> None:
        scenarios = [make_scenario_template(), make_scenario_template(name="budget_search")]
        seed = make_seed(scenarios=scenarios)
        assert seed.scenarios is not None
        assert len(seed.scenarios) == 2
        assert seed.scenarios[0].name == "brand_search"
        assert seed.scenarios[1].name == "budget_search"

    def test_scenario_tool_reference_warning(self) -> None:
        """Scenario referencing unknown tool triggers a warning."""
        scenario = make_scenario_template(
            expected_tool_sequence=["nonexistent_tool"],
        )
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            make_seed(
                parametros_factuales=ParametrosFactuales(
                    contexto="Test",
                    restricciones=[],
                    herramientas=["crm"],
                    metadata={},
                ),
                scenarios=[scenario],
            )
            tool_warnings = [x for x in w if "nonexistent_tool" in str(x.message)]
            assert len(tool_warnings) >= 1

    def test_no_warning_when_tools_match(self) -> None:
        """No warning when scenario tools match seed herramientas."""
        scenario = make_scenario_template(
            expected_tool_sequence=["crm"],
        )
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            make_seed(
                parametros_factuales=ParametrosFactuales(
                    contexto="Test",
                    restricciones=[],
                    herramientas=["crm"],
                    metadata={},
                ),
                scenarios=[scenario],
            )
            tool_warnings = [x for x in w if "not in seed" in str(x.message)]
            assert len(tool_warnings) == 0

    def test_no_warning_when_seed_has_no_tools(self) -> None:
        """No warning when seed defines no tools (scenarios can still reference tools)."""
        scenario = make_scenario_template(
            expected_tool_sequence=["some_tool"],
        )
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            make_seed(
                parametros_factuales=ParametrosFactuales(
                    contexto="Test",
                    restricciones=[],
                    herramientas=[],
                    metadata={},
                ),
                scenarios=[scenario],
            )
            tool_warnings = [x for x in w if "not in seed" in str(x.message)]
            assert len(tool_warnings) == 0

    def test_scenario_empty_tool_sequence_no_warning(self) -> None:
        """Scenario with no expected tools triggers no warning."""
        scenario = make_scenario_template(expected_tool_sequence=[])
        seed = make_seed(scenarios=[scenario])
        assert seed.scenarios is not None

    def test_backwards_compatible_serialization(self) -> None:
        """SeedSchema without scenarios serializes cleanly."""
        seed = make_seed()
        data = seed.model_dump()
        assert data["scenarios"] is None

    def test_roundtrip_with_scenarios(self) -> None:
        """SeedSchema with scenarios round-trips through serialization."""
        from uncase.schemas.seed import SeedSchema

        scenarios = [make_scenario_template()]
        seed = make_seed(scenarios=scenarios)
        data = seed.model_dump()
        restored = SeedSchema(**data)
        assert restored.scenarios is not None
        assert restored.scenarios[0].name == "brand_search"
