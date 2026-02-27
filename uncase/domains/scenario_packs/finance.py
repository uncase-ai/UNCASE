"""Finance advisory scenario pack — 10 curated conversation archetypes.

Covers financial planning interactions from initial risk profiling to
complex portfolio rebalancing, including edge cases like market volatility
and regulatory compliance discussions.

All data is synthetic. No real PII is present.
"""

from __future__ import annotations

from uncase.schemas.scenario import ScenarioPack, ScenarioTemplate

_DOMAIN = "finance.advisory"

FINANCE_SCENARIOS: list[ScenarioTemplate] = [
    ScenarioTemplate(
        name="initial_risk_profiling",
        description="First-time client risk tolerance assessment and goal setting.",
        domain=_DOMAIN,
        intent="New client meets with financial advisor for initial risk profiling and investment goal identification.",
        skill_level="intermediate",
        expected_tool_sequence=["evaluar_perfil_riesgo"],
        flow_steps=[
            "Welcome and onboarding context",
            "Financial goals discussion",
            "Risk tolerance questionnaire",
            "Time horizon assessment",
            "Risk profile presentation",
            "Initial recommendations overview",
        ],
        weight=8.0,
        tags=["risk_profiling", "new_client", "onboarding"],
    ),
    ScenarioTemplate(
        name="portfolio_review",
        description="Periodic review of client's investment portfolio performance.",
        domain=_DOMAIN,
        intent="Advisor reviews the client's current portfolio allocation, performance, and suggests adjustments.",
        skill_level="intermediate",
        expected_tool_sequence=["consultar_portafolio", "consultar_mercado"],
        flow_steps=[
            "Greeting and context",
            "Portfolio performance summary",
            "Sector and asset allocation review",
            "Compare against benchmarks",
            "Discuss concerns or changes in goals",
            "Propose rebalancing if needed",
            "Action items and next review date",
        ],
        weight=10.0,
        tags=["portfolio", "review", "performance"],
    ),
    ScenarioTemplate(
        name="retirement_planning",
        description="Long-term retirement planning consultation.",
        domain=_DOMAIN,
        intent="Client seeks advice on retirement savings strategy, timeline, and projected income needs.",
        skill_level="advanced",
        expected_tool_sequence=["consultar_portafolio", "simular_inversion"],
        flow_steps=[
            "Current financial situation review",
            "Retirement goals and lifestyle expectations",
            "Income projection and gap analysis",
            "Investment strategy for retirement",
            "Tax-advantaged account discussion",
            "Simulation of different scenarios",
            "Action plan and contribution targets",
            "Schedule follow-up review",
        ],
        weight=8.0,
        tags=["retirement", "planning", "long_term"],
    ),
    ScenarioTemplate(
        name="investment_product_explanation",
        description="Advisor explains a specific investment product to a client.",
        domain=_DOMAIN,
        intent=(
            "Client asks about a specific investment product and the advisor explains "
            "features, risks, and suitability."
        ),
        skill_level="intermediate",
        expected_tool_sequence=["consultar_mercado"],
        flow_steps=[
            "Client asks about product",
            "Product overview and mechanics",
            "Risk factors and disclaimers",
            "Fees and cost structure",
            "Suitability for client's profile",
            "Comparison with alternatives",
            "Decision and next steps",
        ],
        weight=6.0,
        tags=["product", "explanation", "education"],
    ),
    ScenarioTemplate(
        name="tax_optimization",
        description="Discussion of tax-efficient investment strategies.",
        domain=_DOMAIN,
        intent="Advisor helps client understand tax implications of their investments and optimize for tax efficiency.",
        skill_level="advanced",
        expected_tool_sequence=["consultar_portafolio"],
        flow_steps=[
            "Review current tax situation",
            "Identify tax-loss harvesting opportunities",
            "Tax-advantaged account recommendations",
            "Asset location strategy",
            "Client questions on tax implications",
            "Action plan for tax year",
        ],
        weight=4.0,
        tags=["tax", "optimization", "strategy"],
    ),
    ScenarioTemplate(
        name="kyc_compliance_review",
        description="Know Your Customer compliance review and documentation.",
        domain=_DOMAIN,
        intent="Advisor conducts required KYC review, updating client information and verifying compliance status.",
        skill_level="basic",
        expected_tool_sequence=["verificar_cumplimiento"],
        flow_steps=[
            "Explain purpose of review",
            "Verify personal information",
            "Update financial situation",
            "Review investment objectives",
            "Compliance documentation",
            "Next review schedule",
        ],
        weight=4.0,
        tags=["kyc", "compliance", "regulatory"],
    ),
    # -- Edge cases --
    ScenarioTemplate(
        name="market_volatility_concern",
        description="Client panics during market downturn and considers selling.",
        domain=_DOMAIN,
        intent=(
            "Client is worried about market volatility and wants to sell everything; "
            "advisor counsels patience and perspective."
        ),
        skill_level="advanced",
        expected_tool_sequence=["consultar_portafolio", "consultar_mercado"],
        flow_steps=[
            "Client expresses panic about market drop",
            "Advisor acknowledges concern empathetically",
            "Put current situation in historical context",
            "Review portfolio resilience and diversification",
            "Discuss costs of emotional selling",
            "Agree on measured response if any",
            "Reassurance and follow-up plan",
        ],
        edge_case=True,
        weight=4.0,
        tags=["volatility", "panic", "behavioral_finance"],
    ),
    ScenarioTemplate(
        name="unrealistic_return_expectations",
        description="Client has unrealistic expectations about investment returns.",
        domain=_DOMAIN,
        intent="Client expects guaranteed high returns and the advisor must set realistic expectations.",
        skill_level="intermediate",
        expected_tool_sequence=[],
        flow_steps=[
            "Client states return expectations",
            "Advisor addresses expectations tactfully",
            "Explain risk-return relationship",
            "Show historical return data",
            "Recalibrate goals realistically",
            "Propose suitable strategy",
        ],
        edge_case=True,
        weight=4.0,
        tags=["expectations", "education", "reality_check"],
    ),
    ScenarioTemplate(
        name="suspicious_activity_flag",
        description="Advisor notices unusual transaction patterns and must follow compliance procedures.",
        domain=_DOMAIN,
        intent=(
            "Advisor identifies potential suspicious activity and navigates the "
            "conversation while following AML procedures."
        ),
        skill_level="advanced",
        expected_tool_sequence=["verificar_cumplimiento"],
        flow_steps=[
            "Routine transaction review",
            "Identify unusual pattern",
            "Ask clarifying questions professionally",
            "Document client explanations",
            "Follow internal compliance protocol",
            "Communicate next steps to client",
        ],
        edge_case=True,
        weight=4.0,
        tags=["aml", "compliance", "suspicious_activity"],
    ),
    ScenarioTemplate(
        name="inheritance_planning",
        description="Client seeks advice on managing a sudden inheritance.",
        domain=_DOMAIN,
        intent=(
            "Client has received an inheritance and needs guidance on investment, tax, "
            "and estate planning implications."
        ),
        skill_level="advanced",
        expected_tool_sequence=["evaluar_perfil_riesgo", "simular_inversion"],
        flow_steps=[
            "Client describes inheritance situation",
            "Emotional acknowledgment",
            "Tax implications overview",
            "Investment strategy for windfall",
            "Estate planning considerations",
            "Phased implementation plan",
            "Professional referrals if needed",
        ],
        weight=4.0,
        tags=["inheritance", "windfall", "estate_planning"],
    ),
]

FINANCE_SCENARIO_PACK = ScenarioPack(
    id="finance-advisory-scenarios",
    name="Finance Advisory Scenarios",
    description=(
        "10 curated conversation archetypes for financial advisory interactions. "
        "Covers initial onboarding through complex portfolio management, "
        "with 3 edge-case scenarios including market panic and compliance."
    ),
    domain=_DOMAIN,
    version="1.0.0",
    scenarios=FINANCE_SCENARIOS,
)
