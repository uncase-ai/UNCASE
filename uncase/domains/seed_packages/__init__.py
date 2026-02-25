"""Pre-built domain seed packages for quick-start onboarding.

Each domain package provides 50 curated SeedSchema v1 seeds covering
common interaction patterns for that industry vertical.
"""

from __future__ import annotations

from uncase.domains.seed_packages.automotive import AUTOMOTIVE_SEEDS
from uncase.domains.seed_packages.finance import FINANCE_SEEDS
from uncase.domains.seed_packages.medical import MEDICAL_SEEDS

DOMAIN_PACKAGES: dict[str, list[dict[str, object]]] = {
    "automotive.sales": AUTOMOTIVE_SEEDS,
    "medical.consultation": MEDICAL_SEEDS,
    "finance.advisory": FINANCE_SEEDS,
}

__all__ = [
    "AUTOMOTIVE_SEEDS",
    "DOMAIN_PACKAGES",
    "FINANCE_SEEDS",
    "MEDICAL_SEEDS",
]
