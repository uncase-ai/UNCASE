"""Tests for compliance profile definitions."""

from __future__ import annotations

import pytest

from uncase.domains.compliance.profiles import (
    AI_ACT_PROFILE,
    COMPLIANCE_PROFILES,
    GDPR_PROFILE,
    HIPAA_PROFILE,
    LFPDPPP_PROFILE,
    SOX_PROFILE,
    ComplianceProfile,
    get_profile,
)


class TestComplianceProfile:
    """Test ComplianceProfile dataclass."""

    def test_is_frozen(self) -> None:
        with pytest.raises(AttributeError):
            HIPAA_PROFILE.name = "Modified"  # type: ignore[misc]

    def test_default_values(self) -> None:
        profile = ComplianceProfile(
            name="Test",
            regulation="TEST",
            description="Test profile",
        )
        assert profile.dp_required is False
        assert profile.dp_max_epsilon == 8.0
        assert profile.audit_required is True
        assert profile.data_retention_days == 365
        assert profile.encryption_at_rest is True
        assert profile.access_control == "rbac"


class TestHIPAAProfile:
    """Test HIPAA compliance profile."""

    def test_basic_attributes(self) -> None:
        assert HIPAA_PROFILE.regulation == "HIPAA"
        assert "US" in HIPAA_PROFILE.jurisdictions

    def test_requires_dp(self) -> None:
        assert HIPAA_PROFILE.dp_required is True
        assert HIPAA_PROFILE.dp_max_epsilon <= 3.0

    def test_strict_memorization(self) -> None:
        assert HIPAA_PROFILE.quality_thresholds["memorizacion_max"] <= 0.005

    def test_zero_privacy(self) -> None:
        assert HIPAA_PROFILE.quality_thresholds["privacy_score"] == 0.0

    def test_hipaa_pii_categories(self) -> None:
        assert "PERSON" in HIPAA_PROFILE.pii_categories
        assert "US_SSN" in HIPAA_PROFILE.pii_categories
        assert "MEDICAL_RECORD_NUMBER" in HIPAA_PROFILE.pii_categories

    def test_7_year_retention(self) -> None:
        assert HIPAA_PROFILE.data_retention_days >= 2555

    def test_mfa_access_control(self) -> None:
        assert "mfa" in HIPAA_PROFILE.access_control

    def test_baa_rule(self) -> None:
        assert "business_associate" in HIPAA_PROFILE.additional_rules


class TestGDPRProfile:
    """Test GDPR compliance profile."""

    def test_basic_attributes(self) -> None:
        assert GDPR_PROFILE.regulation == "GDPR"
        assert "EU" in GDPR_PROFILE.jurisdictions

    def test_requires_dp(self) -> None:
        assert GDPR_PROFILE.dp_required is True
        assert GDPR_PROFILE.dp_max_epsilon <= 5.0

    def test_data_minimization(self) -> None:
        assert "data_minimization" in GDPR_PROFILE.additional_rules

    def test_right_to_erasure(self) -> None:
        assert "right_to_erasure" in GDPR_PROFILE.additional_rules

    def test_special_categories(self) -> None:
        assert "GENETIC_DATA" in GDPR_PROFILE.pii_categories
        assert "POLITICAL_OPINION" in GDPR_PROFILE.pii_categories


class TestSOXProfile:
    """Test SOX compliance profile."""

    def test_basic_attributes(self) -> None:
        assert SOX_PROFILE.regulation == "SOX"
        assert SOX_PROFILE.dp_required is True

    def test_high_fidelity(self) -> None:
        assert SOX_PROFILE.quality_thresholds["fidelidad_min"] >= 0.95

    def test_audit_trail_rule(self) -> None:
        assert "audit_trail" in SOX_PROFILE.additional_rules


class TestLFPDPPPProfile:
    """Test Mexican LFPDPPP compliance profile."""

    def test_basic_attributes(self) -> None:
        assert LFPDPPP_PROFILE.regulation == "LFPDPPP"
        assert "MX" in LFPDPPP_PROFILE.jurisdictions

    def test_dp_not_required(self) -> None:
        assert LFPDPPP_PROFILE.dp_required is False

    def test_arco_rights(self) -> None:
        assert "derechos_arco" in LFPDPPP_PROFILE.additional_rules


class TestAIActProfile:
    """Test EU AI Act compliance profile."""

    def test_basic_attributes(self) -> None:
        assert AI_ACT_PROFILE.regulation == "AI_ACT"
        assert "EU" in AI_ACT_PROFILE.jurisdictions

    def test_higher_diversity(self) -> None:
        assert AI_ACT_PROFILE.quality_thresholds["diversidad_lexica_min"] >= 0.60

    def test_bias_testing(self) -> None:
        assert "bias_testing" in AI_ACT_PROFILE.additional_rules


class TestGetProfile:
    """Test profile lookup."""

    def test_get_hipaa(self) -> None:
        profile = get_profile("hipaa")
        assert profile is not None
        assert profile.regulation == "HIPAA"

    def test_case_insensitive(self) -> None:
        assert get_profile("HIPAA") is not None
        assert get_profile("Gdpr") is not None

    def test_not_found(self) -> None:
        assert get_profile("nonexistent") is None

    def test_all_profiles_registered(self) -> None:
        assert len(COMPLIANCE_PROFILES) == 5
        for key in ("hipaa", "gdpr", "sox", "lfpdppp", "ai_act"):
            assert key in COMPLIANCE_PROFILES


class TestAllProfilesConsistency:
    """Cross-profile consistency checks."""

    @pytest.mark.parametrize("profile", COMPLIANCE_PROFILES.values(), ids=lambda p: p.regulation)
    def test_zero_privacy_score(self, profile: ComplianceProfile) -> None:
        assert profile.quality_thresholds.get("privacy_score", 0.0) == 0.0

    @pytest.mark.parametrize("profile", COMPLIANCE_PROFILES.values(), ids=lambda p: p.regulation)
    def test_has_person_pii(self, profile: ComplianceProfile) -> None:
        assert "PERSON" in profile.pii_categories

    @pytest.mark.parametrize("profile", COMPLIANCE_PROFILES.values(), ids=lambda p: p.regulation)
    def test_audit_required(self, profile: ComplianceProfile) -> None:
        assert profile.audit_required is True

    @pytest.mark.parametrize("profile", COMPLIANCE_PROFILES.values(), ids=lambda p: p.regulation)
    def test_encryption_at_rest(self, profile: ComplianceProfile) -> None:
        assert profile.encryption_at_rest is True
