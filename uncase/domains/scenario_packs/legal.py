"""Legal advisory scenario pack — 8 curated conversation archetypes.

Covers legal consultation workflows from initial case intake to complex
strategy discussions, including edge cases like unrealistic expectations
and conflict of interest discovery.

All data is synthetic. No real PII is present.
"""

from __future__ import annotations

from uncase.schemas.scenario import ScenarioPack, ScenarioTemplate

_DOMAIN = "legal.advisory"

LEGAL_SCENARIOS: list[ScenarioTemplate] = [
    ScenarioTemplate(
        name="case_intake",
        description="Initial client consultation and case intake process.",
        domain=_DOMAIN,
        intent="New client meets with attorney for initial case assessment, fact gathering, and next steps.",
        skill_level="intermediate",
        expected_tool_sequence=["buscar_expediente"],
        flow_steps=[
            "Introduction and engagement letter review",
            "Client describes their situation",
            "Attorney asks clarifying questions",
            "Preliminary legal assessment",
            "Discuss potential strategies",
            "Fee structure and next steps",
        ],
        weight=10.0,
        tags=["intake", "new_client", "assessment"],
    ),
    ScenarioTemplate(
        name="case_strategy_discussion",
        description="Attorney and client discuss litigation or negotiation strategy.",
        domain=_DOMAIN,
        intent="Attorney presents strategic options for the client's case and they discuss pros, cons, and risks.",
        skill_level="advanced",
        expected_tool_sequence=["buscar_jurisprudencia", "buscar_expediente"],
        flow_steps=[
            "Case status update",
            "Present strategic options",
            "Risk assessment for each option",
            "Cost-benefit analysis",
            "Client preferences and priorities",
            "Agree on strategy",
            "Timeline and milestones",
            "Documentation requirements",
        ],
        weight=8.0,
        tags=["strategy", "litigation", "decision"],
    ),
    ScenarioTemplate(
        name="document_review",
        description="Attorney reviews legal documents with client for signing.",
        domain=_DOMAIN,
        intent="Attorney walks the client through important legal documents, explaining key clauses and implications.",
        skill_level="intermediate",
        expected_tool_sequence=["buscar_expediente"],
        flow_steps=[
            "Context for document review",
            "Overview of document structure",
            "Explain key clauses and obligations",
            "Highlight risks and protections",
            "Client questions on specific terms",
            "Revisions or acceptance",
        ],
        weight=6.0,
        tags=["documents", "review", "contracts"],
    ),
    ScenarioTemplate(
        name="deadline_and_filing",
        description="Discussion of upcoming legal deadlines and filing requirements.",
        domain=_DOMAIN,
        intent="Attorney reviews upcoming deadlines with client and discusses filing preparation and requirements.",
        skill_level="basic",
        expected_tool_sequence=["consultar_plazos", "buscar_expediente"],
        flow_steps=[
            "Review pending deadlines",
            "Filing requirements explanation",
            "Document preparation needs",
            "Client responsibilities",
            "Confirmation and calendar",
        ],
        weight=4.0,
        tags=["deadlines", "filing", "compliance"],
    ),
    ScenarioTemplate(
        name="settlement_negotiation_prep",
        description="Preparing client for settlement negotiation.",
        domain=_DOMAIN,
        intent=(
            "Attorney prepares the client for an upcoming settlement negotiation, "
            "discussing range, tactics, and expectations."
        ),
        skill_level="advanced",
        expected_tool_sequence=["buscar_jurisprudencia", "calcular_honorarios"],
        flow_steps=[
            "Case position summary",
            "Opposing party's likely position",
            "Settlement range discussion",
            "Negotiation tactics and approach",
            "Bottom line and walk-away point",
            "Preparation for different outcomes",
            "Role-play key scenarios",
        ],
        weight=6.0,
        tags=["settlement", "negotiation", "preparation"],
    ),
    # -- Edge cases --
    ScenarioTemplate(
        name="unrealistic_legal_expectations",
        description="Client has unrealistic expectations about case outcome or timeline.",
        domain=_DOMAIN,
        intent=(
            "Client expects a guaranteed favorable outcome or impossibly fast "
            "resolution; attorney manages expectations."
        ),
        skill_level="intermediate",
        expected_tool_sequence=[],
        flow_steps=[
            "Client states expectations",
            "Attorney acknowledges desired outcome",
            "Explain realistic possibilities and precedents",
            "Address timeline constraints",
            "Recalibrate expectations constructively",
            "Agree on realistic goals",
        ],
        edge_case=True,
        weight=4.0,
        tags=["expectations", "reality_check", "client_management"],
    ),
    ScenarioTemplate(
        name="conflict_of_interest_discovery",
        description="Potential conflict of interest is discovered during consultation.",
        domain=_DOMAIN,
        intent="Attorney discovers a potential conflict of interest and must handle the situation ethically.",
        skill_level="advanced",
        expected_tool_sequence=[],
        flow_steps=[
            "Initial consultation proceeds normally",
            "Attorney identifies potential conflict",
            "Disclose the situation transparently",
            "Explain ethical obligations",
            "Discuss options (waiver, referral)",
            "Client decision and next steps",
        ],
        edge_case=True,
        weight=4.0,
        tags=["conflict", "ethics", "disclosure"],
    ),
    ScenarioTemplate(
        name="scope_limitation",
        description="Client requests legal advice outside the attorney's practice area.",
        domain=_DOMAIN,
        intent=(
            "Client asks for advice on a legal matter outside the attorney's expertise; "
            "attorney redirects appropriately."
        ),
        skill_level="basic",
        expected_tool_sequence=[],
        flow_steps=[
            "Client presents out-of-scope question",
            "Attorney explains scope limitations",
            "Recommend appropriate specialist",
            "Offer to facilitate referral",
            "Return to in-scope matters",
        ],
        edge_case=True,
        weight=4.0,
        tags=["scope", "referral", "limitations"],
    ),
]

LEGAL_SCENARIO_PACK = ScenarioPack(
    id="legal-advisory-scenarios",
    name="Legal Advisory Scenarios",
    description=(
        "8 curated conversation archetypes for legal advisory consultations. "
        "Covers case intake through settlement preparation, "
        "with 3 edge-case scenarios for ethical and scope-related situations."
    ),
    domain=_DOMAIN,
    version="1.0.0",
    scenarios=LEGAL_SCENARIOS,
)
