"""Education tutoring scenario pack — 8 curated conversation archetypes.

Covers tutoring interactions from concept explanation to assessment review,
including edge cases like student frustration and learning style mismatch.

All data is synthetic. No real PII is present.
"""

from __future__ import annotations

from uncase.schemas.scenario import ScenarioPack, ScenarioTemplate

_DOMAIN = "education.tutoring"

EDUCATION_SCENARIOS: list[ScenarioTemplate] = [
    ScenarioTemplate(
        name="concept_explanation",
        description="Tutor explains a new concept with examples and checks understanding.",
        domain=_DOMAIN,
        intent=(
            "Student needs help understanding a new concept and the tutor provides "
            "structured explanation with examples."
        ),
        skill_level="basic",
        expected_tool_sequence=["buscar_curriculo"],
        flow_steps=[
            "Identify topic and prior knowledge level",
            "Explain concept in simple terms",
            "Provide concrete examples",
            "Check understanding with questions",
            "Clarify misconceptions",
            "Summarize key takeaways",
        ],
        weight=10.0,
        tags=["explanation", "concept", "teaching"],
    ),
    ScenarioTemplate(
        name="homework_help",
        description="Student brings specific homework problems for guided assistance.",
        domain=_DOMAIN,
        intent="Student needs help with specific homework problems and the tutor guides them toward solutions.",
        skill_level="intermediate",
        expected_tool_sequence=["generar_ejercicio", "buscar_curriculo"],
        flow_steps=[
            "Student presents homework problem",
            "Tutor assesses where student is stuck",
            "Guide through problem-solving approach",
            "Student attempts with guidance",
            "Provide feedback and corrections",
            "Practice with similar problem",
            "Confirm understanding",
        ],
        weight=10.0,
        tags=["homework", "problem_solving", "guided_practice"],
    ),
    ScenarioTemplate(
        name="exam_preparation",
        description="Structured exam review and preparation session.",
        domain=_DOMAIN,
        intent=(
            "Student is preparing for an exam and the tutor helps with review, practice "
            "questions, and study strategies."
        ),
        skill_level="intermediate",
        expected_tool_sequence=["buscar_curriculo", "generar_ejercicio"],
        flow_steps=[
            "Identify exam scope and format",
            "Assess student's current preparedness",
            "Review weak areas",
            "Practice with sample questions",
            "Discuss strategies for difficult question types",
            "Study plan for remaining time",
            "Encouragement and confidence building",
        ],
        weight=8.0,
        tags=["exam", "preparation", "review"],
    ),
    ScenarioTemplate(
        name="progress_assessment",
        description="Tutor evaluates student progress and adjusts learning plan.",
        domain=_DOMAIN,
        intent=(
            "Tutor reviews the student's recent progress, identifies strengths and "
            "areas for improvement, and adjusts the plan."
        ),
        skill_level="intermediate",
        expected_tool_sequence=["consultar_progreso"],
        flow_steps=[
            "Review recent work and scores",
            "Celebrate achievements",
            "Identify areas needing improvement",
            "Discuss learning strategies",
            "Set goals for next period",
            "Update learning plan",
        ],
        weight=6.0,
        tags=["assessment", "progress", "planning"],
    ),
    ScenarioTemplate(
        name="research_guidance",
        description="Student needs help with a research project or essay.",
        domain=_DOMAIN,
        intent="Student is working on a research project and needs guidance on methodology, sources, and structure.",
        skill_level="advanced",
        expected_tool_sequence=["buscar_recurso", "buscar_curriculo"],
        flow_steps=[
            "Discuss research topic and thesis",
            "Evaluate current research approach",
            "Suggest sources and methodology",
            "Help with outline and structure",
            "Review draft sections",
            "Provide feedback on argumentation",
            "Next steps and timeline",
        ],
        weight=4.0,
        tags=["research", "writing", "methodology"],
    ),
    # -- Edge cases --
    ScenarioTemplate(
        name="frustrated_student",
        description="Student is frustrated and considering giving up on the subject.",
        domain=_DOMAIN,
        intent=(
            "Student is frustrated with the material and the tutor must re-engage them "
            "through empathy and adjusted approach."
        ),
        skill_level="advanced",
        expected_tool_sequence=[],
        flow_steps=[
            "Student expresses frustration or defeat",
            "Tutor acknowledges feelings without dismissing",
            "Identify specific source of frustration",
            "Break problem into manageable pieces",
            "Achieve a small win to rebuild confidence",
            "Discuss learning strategies that might help",
            "Set realistic, achievable near-term goals",
        ],
        edge_case=True,
        weight=4.0,
        tags=["frustration", "motivation", "emotional_support"],
    ),
    ScenarioTemplate(
        name="learning_style_mismatch",
        description="Current teaching approach doesn't match student's learning style.",
        domain=_DOMAIN,
        intent=(
            "Tutor realizes the current explanation approach isn't working and pivots "
            "to a different learning modality."
        ),
        skill_level="intermediate",
        expected_tool_sequence=["buscar_recurso"],
        flow_steps=[
            "Explanation attempt not landing",
            "Recognize the disconnect",
            "Ask about preferred learning style",
            "Pivot to alternative approach (visual, hands-on, analogy)",
            "Check if new approach works better",
            "Note learning preference for future sessions",
        ],
        edge_case=True,
        weight=4.0,
        tags=["learning_style", "adaptation", "pedagogy"],
    ),
    ScenarioTemplate(
        name="parent_involvement",
        description="Parent joins the conversation to discuss their child's progress.",
        domain=_DOMAIN,
        intent="A parent wants to understand their child's academic progress and how to support learning at home.",
        skill_level="intermediate",
        expected_tool_sequence=["consultar_progreso"],
        flow_steps=[
            "Parent introduces their concern",
            "Review student progress objectively",
            "Highlight strengths and areas for growth",
            "Suggest home support strategies",
            "Discuss realistic expectations",
            "Agree on communication plan",
        ],
        edge_case=True,
        weight=4.0,
        tags=["parent", "communication", "home_support"],
    ),
]

EDUCATION_SCENARIO_PACK = ScenarioPack(
    id="education-tutoring-scenarios",
    name="Education Tutoring Scenarios",
    description=(
        "8 curated conversation archetypes for educational tutoring sessions. "
        "Covers concept explanation through research guidance, "
        "with 3 edge-case scenarios for student engagement challenges."
    ),
    domain=_DOMAIN,
    version="1.0.0",
    scenarios=EDUCATION_SCENARIOS,
)
