"""Medical consultation scenario pack — 10 curated conversation archetypes.

Covers clinical workflows from routine check-ups to complex diagnostic
discussions, including edge cases like patient anxiety and referrals.

All data is synthetic. No real PII is present.
"""

from __future__ import annotations

from uncase.schemas.scenario import ScenarioPack, ScenarioTemplate

_DOMAIN = "medical.consultation"

MEDICAL_SCENARIOS: list[ScenarioTemplate] = [
    ScenarioTemplate(
        name="routine_checkup",
        description="Standard well-visit: intake, review, assessment, and follow-up scheduling.",
        domain=_DOMAIN,
        intent="Patient visits for a routine health checkup and the physician conducts a standard assessment.",
        skill_level="basic",
        expected_tool_sequence=["consultar_historial"],
        flow_steps=[
            "Greeting and identity verification",
            "Review medical history",
            "Current symptoms or concerns",
            "Physical assessment discussion",
            "Results and recommendations",
            "Schedule follow-up",
        ],
        weight=8.0,
        tags=["routine", "checkup", "wellness"],
    ),
    ScenarioTemplate(
        name="symptom_assessment",
        description="Patient presents with symptoms, physician conducts structured assessment.",
        domain=_DOMAIN,
        intent="Patient describes symptoms and the physician systematically evaluates to narrow potential diagnoses.",
        skill_level="intermediate",
        expected_tool_sequence=["consultar_historial", "buscar_medicamentos"],
        flow_steps=[
            "Patient describes chief complaint",
            "History of present illness (onset, duration, severity)",
            "Review of relevant systems",
            "Physician assessment and differential",
            "Diagnostic plan (labs, imaging)",
            "Treatment recommendations",
            "Follow-up instructions",
        ],
        weight=10.0,
        tags=["symptoms", "assessment", "diagnosis"],
    ),
    ScenarioTemplate(
        name="medication_review",
        description="Review and adjustment of patient's current medication regimen.",
        domain=_DOMAIN,
        intent="Physician reviews patient's current medications for efficacy, side effects, and interactions.",
        skill_level="intermediate",
        expected_tool_sequence=["consultar_historial", "buscar_medicamentos"],
        flow_steps=[
            "Greeting and context",
            "Review current medication list",
            "Assess efficacy and side effects",
            "Check for interactions",
            "Propose adjustments",
            "Patient questions and concerns",
            "Updated prescription plan",
        ],
        weight=6.0,
        tags=["medication", "review", "prescription"],
    ),
    ScenarioTemplate(
        name="lab_results_discussion",
        description="Physician explains laboratory results to the patient.",
        domain=_DOMAIN,
        intent="Physician walks the patient through their lab results, explaining abnormal values and next steps.",
        skill_level="intermediate",
        expected_tool_sequence=["consultar_resultados"],
        flow_steps=[
            "Context and greeting",
            "Present lab results overview",
            "Explain key findings",
            "Address abnormal values",
            "Treatment or lifestyle recommendations",
            "Patient questions",
            "Follow-up plan",
        ],
        weight=6.0,
        tags=["lab_results", "explanation", "patient_education"],
    ),
    ScenarioTemplate(
        name="chronic_disease_management",
        description="Ongoing management consultation for a chronic condition.",
        domain=_DOMAIN,
        intent="Patient with a chronic condition (diabetes, hypertension, etc.) has a management consultation.",
        skill_level="advanced",
        expected_tool_sequence=["consultar_historial", "buscar_medicamentos", "consultar_resultados"],
        flow_steps=[
            "Greeting and review since last visit",
            "Symptom and lifestyle update",
            "Review relevant lab trends",
            "Medication adjustment discussion",
            "Lifestyle modification counseling",
            "Goal setting for next period",
            "Schedule monitoring appointments",
            "Closure with encouragement",
        ],
        weight=8.0,
        tags=["chronic", "management", "long_term"],
    ),
    ScenarioTemplate(
        name="specialist_referral",
        description="Primary care physician refers patient to a specialist.",
        domain=_DOMAIN,
        intent="Physician determines the patient needs specialist care and explains the referral process.",
        skill_level="intermediate",
        expected_tool_sequence=["consultar_historial", "agendar_cita"],
        flow_steps=[
            "Review of presenting issue",
            "Explain need for specialist consultation",
            "Describe what to expect",
            "Referral logistics (scheduling, preparation)",
            "Patient concerns and questions",
            "Provide referral documentation",
        ],
        weight=4.0,
        tags=["referral", "specialist", "coordination"],
    ),
    ScenarioTemplate(
        name="preventive_counseling",
        description="Physician provides preventive health counseling based on risk factors.",
        domain=_DOMAIN,
        intent="Physician counsels the patient on preventive measures based on age, history, and risk factors.",
        skill_level="basic",
        expected_tool_sequence=["consultar_historial"],
        flow_steps=[
            "Greeting and context",
            "Review risk factors",
            "Recommended screenings and vaccines",
            "Lifestyle recommendations",
            "Patient questions",
            "Scheduling preventive appointments",
        ],
        weight=4.0,
        tags=["prevention", "counseling", "screenings"],
    ),
    # -- Edge cases --
    ScenarioTemplate(
        name="anxious_patient",
        description="Patient is anxious about their health; physician provides emotional support.",
        domain=_DOMAIN,
        intent=(
            "Patient shows significant anxiety about a health concern and the physician "
            "balances empathy with clinical assessment."
        ),
        skill_level="advanced",
        expected_tool_sequence=[],
        flow_steps=[
            "Patient expresses worry or fear",
            "Physician acknowledges emotions empathetically",
            "Structured assessment to address concerns",
            "Clear, reassuring explanation of findings",
            "Concrete plan to address anxiety source",
            "Emotional support and resources",
        ],
        edge_case=True,
        weight=4.0,
        tags=["anxiety", "emotional_support", "patient_centered"],
    ),
    ScenarioTemplate(
        name="conflicting_information",
        description="Patient has found conflicting health information online.",
        domain=_DOMAIN,
        intent=(
            "Patient cites information from the internet that conflicts with medical "
            "guidance and the physician addresses misconceptions."
        ),
        skill_level="intermediate",
        expected_tool_sequence=[],
        flow_steps=[
            "Patient shares information they found online",
            "Physician listens without dismissing",
            "Address specific claims with evidence",
            "Explain reliable information sources",
            "Align on treatment approach",
        ],
        edge_case=True,
        weight=4.0,
        tags=["misinformation", "patient_education", "internet_research"],
    ),
    ScenarioTemplate(
        name="insurance_coverage_issue",
        description="Recommended treatment may not be covered by patient's insurance.",
        domain=_DOMAIN,
        intent="Physician needs to discuss treatment options considering the patient's insurance limitations.",
        skill_level="intermediate",
        expected_tool_sequence=["verificar_cobertura"],
        flow_steps=[
            "Context: treatment recommendation",
            "Insurance coverage check",
            "Explain coverage limitations",
            "Discuss alternative covered options",
            "Patient questions about costs",
            "Agree on approach and appeal options",
        ],
        edge_case=True,
        weight=4.0,
        tags=["insurance", "coverage", "cost_discussion"],
    ),
]

MEDICAL_SCENARIO_PACK = ScenarioPack(
    id="medical-consultation-scenarios",
    name="Medical Consultation Scenarios",
    description=(
        "10 curated conversation archetypes for medical consultations. "
        "Covers routine checkups through complex chronic disease management, "
        "with 3 edge-case scenarios for robust clinical dialogue training."
    ),
    domain=_DOMAIN,
    version="1.0.0",
    scenarios=MEDICAL_SCENARIOS,
)
