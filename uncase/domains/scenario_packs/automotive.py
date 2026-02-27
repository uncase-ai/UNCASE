"""Automotive sales scenario pack — 12 curated conversation archetypes.

Derived from real-world patterns in dealership interactions. Covers the
full spectrum from simple greetings to complex multi-tool purchase flows,
including edge cases like frustrated customers and off-topic deflection.

All data is synthetic. No real PII is present.
"""

from __future__ import annotations

from uncase.schemas.scenario import ScenarioPack, ScenarioTemplate

_DOMAIN = "automotive.sales"

AUTOMOTIVE_SCENARIOS: list[ScenarioTemplate] = [
    # -- Happy-path scenarios (high weight) --
    ScenarioTemplate(
        name="greeting_and_needs_assessment",
        description="Initial contact: warm greeting followed by structured needs identification.",
        domain=_DOMAIN,
        intent=(
            "Customer initiates contact and the sales agent identifies their vehicle "
            "preferences through open-ended questions."
        ),
        skill_level="basic",
        expected_tool_sequence=[],
        flow_steps=[
            "Warm greeting and welcome",
            "Open-ended needs assessment",
            "Summarize customer requirements",
            "Propose next steps",
        ],
        weight=6.0,
        tags=["greeting", "needs_assessment", "initial_contact"],
    ),
    ScenarioTemplate(
        name="brand_search",
        description="Customer searches for vehicles by brand, agent uses inventory tool.",
        domain=_DOMAIN,
        intent="Customer asks about a specific brand and the agent searches inventory to present available options.",
        skill_level="intermediate",
        expected_tool_sequence=["buscar_inventario"],
        flow_steps=[
            "Greeting",
            "Customer specifies brand preference",
            "Agent searches inventory",
            "Present matching vehicles with key specs",
            "Customer asks follow-up questions",
            "Closure with next steps",
        ],
        weight=10.0,
        tags=["brand_search", "inventory", "tool_usage"],
    ),
    ScenarioTemplate(
        name="budget_search",
        description="Customer has a budget constraint, agent filters by price range.",
        domain=_DOMAIN,
        intent="Customer specifies a budget and the agent searches for vehicles within that price range.",
        skill_level="intermediate",
        expected_tool_sequence=["buscar_inventario"],
        flow_steps=[
            "Greeting",
            "Customer states budget range",
            "Agent searches by price filter",
            "Present affordable options",
            "Discuss value propositions within budget",
            "Financing options mention",
        ],
        weight=8.0,
        tags=["budget", "price_filter", "financing"],
    ),
    ScenarioTemplate(
        name="vehicle_detail_expansion",
        description="Customer interested in a specific vehicle, agent provides detailed specs.",
        domain=_DOMAIN,
        intent=(
            "Customer asks for detailed information about a specific vehicle and the "
            "agent retrieves comprehensive specifications."
        ),
        skill_level="intermediate",
        expected_tool_sequence=["buscar_inventario", "cotizar_vehiculo"],
        flow_steps=[
            "Greeting",
            "Customer identifies vehicle of interest",
            "Agent retrieves vehicle details",
            "Present comprehensive specifications",
            "Customer asks about specific features",
            "Agent provides pricing quote",
            "Next steps discussion",
        ],
        weight=8.0,
        tags=["vehicle_details", "specifications", "quote"],
    ),
    ScenarioTemplate(
        name="financing_calculation",
        description="Customer explores financing options for a vehicle.",
        domain=_DOMAIN,
        intent="Customer wants to understand monthly payments and financing terms for a specific vehicle.",
        skill_level="intermediate",
        expected_tool_sequence=["cotizar_vehiculo"],
        flow_steps=[
            "Context establishment",
            "Customer asks about financing",
            "Agent gathers financing parameters (down payment, term)",
            "Agent calculates financing options",
            "Present payment breakdown",
            "Discuss terms and conditions",
            "Closure with application next steps",
        ],
        weight=8.0,
        tags=["financing", "payment_calculation", "credit"],
    ),
    ScenarioTemplate(
        name="full_purchase_flow",
        description="Complete end-to-end purchase journey from greeting through financing to contact collection.",
        domain=_DOMAIN,
        intent=(
            "Customer goes through the full purchase journey: initial inquiry, vehicle search, "
            "detail review, financing calculation, and contact information exchange."
        ),
        skill_level="advanced",
        expected_tool_sequence=["buscar_inventario", "cotizar_vehiculo"],
        flow_steps=[
            "Warm greeting and needs assessment",
            "Vehicle search based on preferences",
            "Present options and narrow down",
            "Detailed review of preferred vehicle",
            "Financing options calculation",
            "Payment plan discussion",
            "Contact information exchange for follow-up",
            "Closure with clear next steps and timeline",
        ],
        weight=10.0,
        tags=["full_flow", "end_to_end", "purchase_journey"],
    ),
    ScenarioTemplate(
        name="vehicle_comparison",
        description="Customer wants to compare two or more vehicles side by side.",
        domain=_DOMAIN,
        intent="Customer is deciding between multiple vehicles and needs a comparative analysis.",
        skill_level="advanced",
        expected_tool_sequence=["buscar_inventario", "cotizar_vehiculo"],
        flow_steps=[
            "Greeting",
            "Customer describes comparison criteria",
            "Agent retrieves details for each candidate",
            "Present side-by-side comparison",
            "Discuss trade-offs and recommendations",
            "Customer narrows selection",
            "Next steps for preferred vehicle",
        ],
        weight=6.0,
        tags=["comparison", "decision_support", "multiple_vehicles"],
    ),
    # -- Edge-case scenarios (lower weight but important for diversity) --
    ScenarioTemplate(
        name="not_available_fallback",
        description="Requested vehicle is not in stock, agent suggests alternatives.",
        domain=_DOMAIN,
        intent=(
            "Customer asks for a vehicle that is not available and the agent gracefully "
            "pivots to suitable alternatives."
        ),
        skill_level="intermediate",
        expected_tool_sequence=["buscar_inventario"],
        flow_steps=[
            "Greeting",
            "Customer requests specific vehicle",
            "Agent searches and finds no results",
            "Acknowledge unavailability empathetically",
            "Suggest alternative vehicles",
            "Present alternatives with reasoning",
            "Customer evaluates alternatives",
        ],
        edge_case=True,
        weight=6.0,
        tags=["not_available", "alternatives", "fallback"],
    ),
    ScenarioTemplate(
        name="frustrated_customer",
        description="Customer is frustrated or impatient, agent de-escalates while staying helpful.",
        domain=_DOMAIN,
        intent=(
            "Customer expresses frustration and the agent must de-escalate the situation "
            "while still providing value."
        ),
        skill_level="advanced",
        expected_tool_sequence=[],
        flow_steps=[
            "Customer expresses frustration or impatience",
            "Agent acknowledges feelings empathetically",
            "Reframe the situation positively",
            "Offer concrete solutions or alternatives",
            "Customer begins to engage constructively",
            "Resolution and commitment to follow-up",
        ],
        edge_case=True,
        weight=4.0,
        tags=["frustrated", "de_escalation", "emotional_intelligence"],
    ),
    ScenarioTemplate(
        name="price_negotiation_refusal",
        description="Customer attempts to negotiate price, agent maintains firm pricing policy.",
        domain=_DOMAIN,
        intent=(
            "Customer tries to negotiate the listed price and the agent politely but "
            "firmly enforces the no-negotiation policy."
        ),
        skill_level="intermediate",
        expected_tool_sequence=[],
        flow_steps=[
            "Context establishment",
            "Customer requests discount or price negotiation",
            "Agent explains pricing policy firmly but politely",
            "Redirect to value: financing, promotions, trade-in",
            "Customer accepts or asks alternative",
            "Constructive closure",
        ],
        edge_case=True,
        weight=4.0,
        tags=["negotiation", "price_policy", "boundary"],
    ),
    ScenarioTemplate(
        name="off_topic_redirect",
        description="Customer asks about unrelated topics, agent redirects to automotive services.",
        domain=_DOMAIN,
        intent=(
            "Customer asks questions outside the dealership's scope and the agent "
            "politely redirects to relevant services."
        ),
        skill_level="basic",
        expected_tool_sequence=[],
        flow_steps=[
            "Greeting",
            "Customer asks off-topic question",
            "Agent acknowledges and politely redirects",
            "Offer relevant automotive assistance",
        ],
        edge_case=True,
        weight=4.0,
        tags=["off_topic", "redirect", "scope_boundary"],
    ),
    ScenarioTemplate(
        name="bot_identity_disclosure",
        description="Customer asks if they are talking to a bot, agent handles transparency.",
        domain=_DOMAIN,
        intent=(
            "Customer directly asks whether the agent is a bot or human, and the agent "
            "responds with appropriate transparency."
        ),
        skill_level="basic",
        expected_tool_sequence=[],
        flow_steps=[
            "Conversation in progress",
            "Customer asks 'Are you a bot?'",
            "Agent responds transparently",
            "Reassure about service quality",
            "Continue with original conversation thread",
        ],
        edge_case=True,
        weight=4.0,
        tags=["identity", "transparency", "bot_disclosure"],
    ),
]

AUTOMOTIVE_SCENARIO_PACK = ScenarioPack(
    id="automotive-sales-scenarios",
    name="Automotive Sales Scenarios",
    description=(
        "12 curated conversation archetypes for automotive dealership interactions. "
        "Covers the full spectrum from simple greetings to complex multi-tool purchase "
        "flows, including 5 edge-case scenarios for training robust agents."
    ),
    domain=_DOMAIN,
    version="1.0.0",
    scenarios=AUTOMOTIVE_SCENARIOS,
)
