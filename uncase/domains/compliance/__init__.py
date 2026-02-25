"""Compliance-as-code profiles for regulated industries.

Each profile defines pre-configured thresholds, required audit hooks,
PII categories, and data handling rules for a specific regulatory framework.
"""

from uncase.domains.compliance.profiles import (
    COMPLIANCE_PROFILES,
    ComplianceProfile,
    get_profile,
)

__all__ = [
    "COMPLIANCE_PROFILES",
    "ComplianceProfile",
    "get_profile",
]
