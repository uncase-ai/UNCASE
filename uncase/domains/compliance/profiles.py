"""Compliance profile definitions for regulated industries."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ComplianceProfile:
    """A compliance profile defines regulatory requirements as code.

    Attributes:
        name: Human-readable profile name.
        regulation: Regulatory framework identifier.
        description: Brief description of the regulation.
        jurisdictions: Applicable jurisdictions.
        pii_categories: PII entity types that MUST be detected and removed.
        quality_thresholds: Minimum quality metric thresholds (override defaults).
        dp_required: Whether differential privacy is required during training.
        dp_max_epsilon: Maximum allowed epsilon for DP-SGD.
        audit_required: Whether audit logging is mandatory.
        data_retention_days: Maximum data retention period (0 = delete immediately after use).
        encryption_at_rest: Whether encryption at rest is required.
        access_control: Required access control level.
        additional_rules: Extra regulatory requirements as key-value pairs.
    """

    name: str
    regulation: str
    description: str
    jurisdictions: tuple[str, ...] = ()
    pii_categories: tuple[str, ...] = ()
    quality_thresholds: dict[str, float] = field(default_factory=dict)
    dp_required: bool = False
    dp_max_epsilon: float = 8.0
    audit_required: bool = True
    data_retention_days: int = 365
    encryption_at_rest: bool = True
    access_control: str = "rbac"
    additional_rules: dict[str, str] = field(default_factory=dict)


# HIPAA — Health Insurance Portability and Accountability Act (US)
HIPAA_PROFILE = ComplianceProfile(
    name="HIPAA Compliance",
    regulation="HIPAA",
    description="US health data privacy regulation requiring protection of Protected Health Information (PHI).",
    jurisdictions=("US",),
    pii_categories=(
        "PERSON",
        "DATE_TIME",
        "PHONE_NUMBER",
        "EMAIL_ADDRESS",
        "LOCATION",
        "US_SSN",
        "MEDICAL_LICENSE",
        "US_BANK_NUMBER",
        "IP_ADDRESS",
        "US_PASSPORT",
        "US_DRIVER_LICENSE",
        "NRP",
        # HIPAA-specific PHI identifiers
        "MEDICAL_RECORD_NUMBER",
        "HEALTH_PLAN_NUMBER",
        "ACCOUNT_NUMBER",
        "CERTIFICATE_NUMBER",
        "VEHICLE_IDENTIFIER",
        "DEVICE_IDENTIFIER",
        "URL",
        "BIOMETRIC_IDENTIFIER",
    ),
    quality_thresholds={
        "rouge_l_min": 0.65,
        "fidelidad_min": 0.95,  # Higher fidelity for medical accuracy
        "diversidad_lexica_min": 0.55,
        "coherencia_dialogica_min": 0.90,  # Higher coherence for clinical conversations
        "privacy_score": 0.00,
        "memorizacion_max": 0.005,  # Stricter memorization threshold
    },
    dp_required=True,
    dp_max_epsilon=3.0,  # Strict privacy budget for health data
    audit_required=True,
    data_retention_days=2555,  # 7 years as required by HIPAA
    encryption_at_rest=True,
    access_control="rbac_with_mfa",
    additional_rules={
        "minimum_necessary": "Only process minimum necessary PHI for the intended purpose",
        "business_associate": "All third-party LLM providers must sign BAA",
        "breach_notification": "Notify within 60 days of discovering a breach",
        "training_required": "All personnel must complete HIPAA training annually",
        "de_identification": "Apply Safe Harbor or Expert Determination method",
    },
)

# GDPR — General Data Protection Regulation (EU)
GDPR_PROFILE = ComplianceProfile(
    name="GDPR Compliance",
    regulation="GDPR",
    description="EU data protection regulation enforcing privacy rights and data processing constraints.",
    jurisdictions=("EU", "EEA", "UK"),
    pii_categories=(
        "PERSON",
        "DATE_TIME",
        "PHONE_NUMBER",
        "EMAIL_ADDRESS",
        "LOCATION",
        "IBAN_CODE",
        "IP_ADDRESS",
        "NRP",
        "CREDIT_CARD",
        # GDPR-specific
        "GENETIC_DATA",
        "BIOMETRIC_DATA",
        "POLITICAL_OPINION",
        "RELIGIOUS_BELIEF",
        "TRADE_UNION_MEMBERSHIP",
        "SEXUAL_ORIENTATION",
        "CRIMINAL_RECORD",
    ),
    quality_thresholds={
        "rouge_l_min": 0.65,
        "fidelidad_min": 0.90,
        "diversidad_lexica_min": 0.55,
        "coherencia_dialogica_min": 0.85,
        "privacy_score": 0.00,
        "memorizacion_max": 0.008,
    },
    dp_required=True,
    dp_max_epsilon=5.0,
    audit_required=True,
    data_retention_days=365,  # Purpose limitation — delete when no longer needed
    encryption_at_rest=True,
    access_control="rbac",
    additional_rules={
        "lawful_basis": "Document lawful basis for processing (consent, legitimate interest, etc.)",
        "data_minimization": "Process only data adequate, relevant, and limited to purpose",
        "right_to_erasure": "Support data subject right to deletion within 30 days",
        "right_to_portability": "Support data export in machine-readable format",
        "dpia_required": "Conduct Data Protection Impact Assessment for high-risk processing",
        "cross_border": "Ensure adequate safeguards for international data transfers",
        "dpo_required": "Designate a Data Protection Officer if processing at scale",
    },
)

# SOX — Sarbanes-Oxley Act (US Financial)
SOX_PROFILE = ComplianceProfile(
    name="SOX Compliance",
    regulation="SOX",
    description="US financial reporting regulation requiring internal controls and audit trails.",
    jurisdictions=("US",),
    pii_categories=(
        "PERSON",
        "PHONE_NUMBER",
        "EMAIL_ADDRESS",
        "US_SSN",
        "US_BANK_NUMBER",
        "CREDIT_CARD",
        "IBAN_CODE",
        "NRP",
        "ACCOUNT_NUMBER",
    ),
    quality_thresholds={
        "rouge_l_min": 0.70,  # Higher structural fidelity for financial conversations
        "fidelidad_min": 0.95,  # Very high factual accuracy for financial data
        "diversidad_lexica_min": 0.55,
        "coherencia_dialogica_min": 0.90,
        "privacy_score": 0.00,
        "memorizacion_max": 0.005,
    },
    dp_required=True,
    dp_max_epsilon=5.0,
    audit_required=True,
    data_retention_days=2555,  # 7 years minimum for financial records
    encryption_at_rest=True,
    access_control="rbac_with_mfa",
    additional_rules={
        "internal_controls": "Maintain documented internal controls for data processing",
        "audit_trail": "Complete, immutable audit trail for all data operations",
        "segregation_of_duties": "Separate roles for data creation, approval, and audit",
        "change_management": "Document all pipeline configuration changes",
        "material_weakness": "Report any material weakness in data processing controls",
    },
)

# LFPDPPP — Ley Federal de Protección de Datos Personales (Mexico)
LFPDPPP_PROFILE = ComplianceProfile(
    name="LFPDPPP Compliance",
    regulation="LFPDPPP",
    description="Mexico's federal data protection law for private sector entities.",
    jurisdictions=("MX",),
    pii_categories=(
        "PERSON",
        "DATE_TIME",
        "PHONE_NUMBER",
        "EMAIL_ADDRESS",
        "LOCATION",
        "NRP",
        "CURP",
        "RFC",
        "CREDIT_CARD",
        "IP_ADDRESS",
    ),
    quality_thresholds={
        "rouge_l_min": 0.65,
        "fidelidad_min": 0.90,
        "diversidad_lexica_min": 0.55,
        "coherencia_dialogica_min": 0.85,
        "privacy_score": 0.00,
        "memorizacion_max": 0.01,
    },
    dp_required=False,
    dp_max_epsilon=8.0,
    audit_required=True,
    data_retention_days=365,
    encryption_at_rest=True,
    access_control="rbac",
    additional_rules={
        "aviso_privacidad": "Publish privacy notice (aviso de privacidad) before data collection",
        "consentimiento": "Obtain explicit consent for processing sensitive personal data",
        "derechos_arco": "Support ARCO rights (Access, Rectification, Cancellation, Opposition)",
        "transferencias": "Document all international data transfers with recipient safeguards",
    },
)

# AI Act — EU Artificial Intelligence Act
AI_ACT_PROFILE = ComplianceProfile(
    name="EU AI Act Compliance",
    regulation="AI_ACT",
    description="EU regulation for artificial intelligence systems based on risk classification.",
    jurisdictions=("EU", "EEA"),
    pii_categories=(
        "PERSON",
        "DATE_TIME",
        "PHONE_NUMBER",
        "EMAIL_ADDRESS",
        "LOCATION",
        "BIOMETRIC_DATA",
        "GENETIC_DATA",
    ),
    quality_thresholds={
        "rouge_l_min": 0.70,
        "fidelidad_min": 0.92,
        "diversidad_lexica_min": 0.60,  # Higher diversity to reduce bias
        "coherencia_dialogica_min": 0.88,
        "privacy_score": 0.00,
        "memorizacion_max": 0.008,
    },
    dp_required=True,
    dp_max_epsilon=5.0,
    audit_required=True,
    data_retention_days=365,
    encryption_at_rest=True,
    access_control="rbac",
    additional_rules={
        "risk_classification": "Classify AI system risk level (minimal, limited, high, unacceptable)",
        "transparency": "Document training data sources, quality metrics, and known limitations",
        "human_oversight": "Ensure human oversight mechanisms for high-risk applications",
        "bias_testing": "Test for and mitigate demographic bias in training data",
        "technical_documentation": "Maintain comprehensive technical documentation per Article 11",
        "conformity_assessment": "Complete conformity assessment before deployment",
    },
)

# Consolidated registry
COMPLIANCE_PROFILES: dict[str, ComplianceProfile] = {
    "hipaa": HIPAA_PROFILE,
    "gdpr": GDPR_PROFILE,
    "sox": SOX_PROFILE,
    "lfpdppp": LFPDPPP_PROFILE,
    "ai_act": AI_ACT_PROFILE,
}


def get_profile(regulation: str) -> ComplianceProfile | None:
    """Get a compliance profile by regulation identifier.

    Args:
        regulation: Case-insensitive regulation ID (hipaa, gdpr, sox, lfpdppp, ai_act).

    Returns:
        ComplianceProfile or None if not found.
    """
    return COMPLIANCE_PROFILES.get(regulation.lower())
