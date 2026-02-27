"""Industrial support scenario pack — 8 curated conversation archetypes.

Covers technical support workflows for industrial equipment and processes,
including edge cases like safety incidents and escalation to field service.

All data is synthetic. No real PII is present.
"""

from __future__ import annotations

from uncase.schemas.scenario import ScenarioPack, ScenarioTemplate

_DOMAIN = "industrial.support"

INDUSTRIAL_SCENARIOS: list[ScenarioTemplate] = [
    ScenarioTemplate(
        name="equipment_troubleshooting",
        description="Standard troubleshooting flow for malfunctioning industrial equipment.",
        domain=_DOMAIN,
        intent="Operator reports equipment malfunction and technician guides them through structured diagnostic steps.",
        skill_level="intermediate",
        expected_tool_sequence=["diagnosticar_equipo", "buscar_documentacion"],
        flow_steps=[
            "Issue identification and safety check",
            "Equipment and error code identification",
            "Guided diagnostic steps",
            "Root cause narrowing",
            "Corrective action instructions",
            "Verification and testing",
            "Documentation and ticket closure",
        ],
        weight=10.0,
        tags=["troubleshooting", "diagnostics", "equipment"],
    ),
    ScenarioTemplate(
        name="preventive_maintenance_scheduling",
        description="Scheduling and planning preventive maintenance for equipment.",
        domain=_DOMAIN,
        intent=(
            "Operator or manager schedules preventive maintenance based on equipment "
            "usage and maintenance schedule."
        ),
        skill_level="basic",
        expected_tool_sequence=["programar_mantenimiento", "buscar_inventario_partes"],
        flow_steps=[
            "Identify equipment due for maintenance",
            "Review maintenance schedule and history",
            "Check parts availability",
            "Schedule maintenance window",
            "Confirm resource allocation",
            "Issue work order",
        ],
        weight=8.0,
        tags=["maintenance", "preventive", "scheduling"],
    ),
    ScenarioTemplate(
        name="spare_parts_inquiry",
        description="Inquiry about spare parts availability and ordering.",
        domain=_DOMAIN,
        intent="Operator needs specific replacement parts and the technician helps identify, locate, and order them.",
        skill_level="basic",
        expected_tool_sequence=["buscar_inventario_partes"],
        flow_steps=[
            "Part identification (number, description, equipment)",
            "Inventory availability check",
            "Compatible alternatives if unavailable",
            "Pricing and lead time",
            "Order placement or reservation",
        ],
        weight=6.0,
        tags=["parts", "inventory", "ordering"],
    ),
    ScenarioTemplate(
        name="process_optimization",
        description="Discussion about optimizing an industrial process or production line.",
        domain=_DOMAIN,
        intent=(
            "Operator or engineer discusses process bottlenecks and the technician "
            "suggests optimization strategies."
        ),
        skill_level="advanced",
        expected_tool_sequence=["diagnosticar_equipo", "buscar_documentacion"],
        flow_steps=[
            "Current process description",
            "Identify bottlenecks and pain points",
            "Review equipment specifications",
            "Analyze operational parameters",
            "Suggest optimization strategies",
            "Implementation plan and expected improvements",
            "Monitoring and follow-up plan",
        ],
        weight=4.0,
        tags=["optimization", "process", "efficiency"],
    ),
    ScenarioTemplate(
        name="new_equipment_training",
        description="Training session for newly installed equipment.",
        domain=_DOMAIN,
        intent="Technician provides operational training for new equipment to plant operators.",
        skill_level="intermediate",
        expected_tool_sequence=["buscar_documentacion"],
        flow_steps=[
            "Equipment overview and capabilities",
            "Safety procedures and PPE requirements",
            "Basic operation walkthrough",
            "Common settings and configurations",
            "Troubleshooting basics",
            "Maintenance responsibilities",
            "Q&A and reference materials",
        ],
        weight=4.0,
        tags=["training", "new_equipment", "onboarding"],
    ),
    # -- Edge cases --
    ScenarioTemplate(
        name="safety_incident_report",
        description="Operator reports a safety incident or near-miss.",
        domain=_DOMAIN,
        intent=(
            "Operator reports a safety incident and technician follows incident "
            "reporting protocols while ensuring immediate safety."
        ),
        skill_level="advanced",
        expected_tool_sequence=["reportar_incidente"],
        flow_steps=[
            "Immediate safety assessment — is anyone injured?",
            "Secure the area if needed",
            "Incident description and timeline",
            "Gather witness information",
            "Root cause preliminary assessment",
            "File formal incident report",
            "Corrective actions and prevention",
        ],
        edge_case=True,
        weight=4.0,
        tags=["safety", "incident", "reporting"],
    ),
    ScenarioTemplate(
        name="escalation_to_field_service",
        description="Issue cannot be resolved remotely and requires field service dispatch.",
        domain=_DOMAIN,
        intent="Remote troubleshooting fails and the technician must escalate to on-site field service.",
        skill_level="intermediate",
        expected_tool_sequence=["diagnosticar_equipo", "programar_mantenimiento"],
        flow_steps=[
            "Review troubleshooting steps already taken",
            "Confirm issue requires on-site visit",
            "Gather detailed information for field tech",
            "Schedule field service visit",
            "Interim workaround instructions",
            "Expected timeline and contact details",
        ],
        edge_case=True,
        weight=4.0,
        tags=["escalation", "field_service", "on_site"],
    ),
    ScenarioTemplate(
        name="production_line_down",
        description="Critical production line stoppage requiring urgent response.",
        domain=_DOMAIN,
        intent="Production line is completely down and the operator needs urgent assistance to minimize downtime.",
        skill_level="advanced",
        expected_tool_sequence=["diagnosticar_equipo", "buscar_inventario_partes"],
        flow_steps=[
            "Urgency assessment and impact scope",
            "Rapid diagnostic triage",
            "Identify critical failure point",
            "Emergency repair procedure if possible",
            "Parts availability for immediate repair",
            "Parallel escalation if needed",
            "Estimated time to recovery",
            "Post-incident review scheduling",
        ],
        edge_case=True,
        weight=4.0,
        tags=["urgent", "downtime", "critical"],
    ),
]

INDUSTRIAL_SCENARIO_PACK = ScenarioPack(
    id="industrial-support-scenarios",
    name="Industrial Support Scenarios",
    description=(
        "8 curated conversation archetypes for industrial technical support. "
        "Covers routine troubleshooting through process optimization, "
        "with 3 edge-case scenarios for safety incidents and critical failures."
    ),
    domain=_DOMAIN,
    version="1.0.0",
    scenarios=INDUSTRIAL_SCENARIOS,
)
