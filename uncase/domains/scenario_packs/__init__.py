"""Built-in scenario packs for all supported domains.

Each domain ships a curated set of ScenarioTemplate definitions that
guide the generator toward specific conversation archetypes.

Usage:
    from uncase.domains.scenario_packs import get_scenario_pack, list_scenario_packs

    pack = get_scenario_pack("automotive.sales")
    for scenario in pack.scenarios:
        print(scenario.name, scenario.weight)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uncase.schemas.scenario import ScenarioPack

# Lazy-loaded packs — avoid heavy import at module level
_PACKS: dict[str, ScenarioPack] | None = None


def _load_packs() -> dict[str, ScenarioPack]:
    """Load all built-in scenario packs."""
    from uncase.domains.scenario_packs.automotive import AUTOMOTIVE_SCENARIO_PACK
    from uncase.domains.scenario_packs.education import EDUCATION_SCENARIO_PACK
    from uncase.domains.scenario_packs.finance import FINANCE_SCENARIO_PACK
    from uncase.domains.scenario_packs.industrial import INDUSTRIAL_SCENARIO_PACK
    from uncase.domains.scenario_packs.legal import LEGAL_SCENARIO_PACK
    from uncase.domains.scenario_packs.medical import MEDICAL_SCENARIO_PACK

    return {
        pack.domain: pack
        for pack in [
            AUTOMOTIVE_SCENARIO_PACK,
            MEDICAL_SCENARIO_PACK,
            FINANCE_SCENARIO_PACK,
            LEGAL_SCENARIO_PACK,
            INDUSTRIAL_SCENARIO_PACK,
            EDUCATION_SCENARIO_PACK,
        ]
    }


def get_scenario_pack(domain: str) -> ScenarioPack | None:
    """Get the built-in scenario pack for a domain, or None."""
    global _PACKS
    if _PACKS is None:
        _PACKS = _load_packs()
    return _PACKS.get(domain)


def list_scenario_packs() -> list[ScenarioPack]:
    """List all built-in scenario packs."""
    global _PACKS
    if _PACKS is None:
        _PACKS = _load_packs()
    return list(_PACKS.values())
