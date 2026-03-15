// ─── Tool Scanner ───
// Analyzes imported conversations to identify required tools and generates
// complete ToolDefinition objects. In demo mode (no API) it uses pattern-matching
// heuristics. When the API is available it delegates to the backend's LLM scanner.

import type { Conversation, ConversationTurn } from '@/types/api'

// ─── Types ───

export interface ToolScanResult {
  conversation_id: string
  requires_tools: boolean
  reasoning: string
  identified_tools: ScannedTool[]
  confidence: number // 0-1
}

export interface ScannedTool {
  name: string
  description: string
  category: 'query' | 'action' | 'validation' | 'calculation' | 'retrieval' | 'notification' | 'integration'
  domains: string[]
  method: 'GET' | 'POST' | 'PUT' | 'DELETE'
  endpoint_url: string
  auth_type: 'none' | 'bearer' | 'api_key' | 'basic'
  input_schema: {
    type: 'object'
    properties: Record<string, { type: string; description: string; enum?: string[] }>
    required: string[]
  }
  output_schema: {
    type: 'object'
    properties: Record<string, { type: string; description: string }>
  }
  execution_mode: 'simulated' | 'live' | 'mock'
  fallback_strategy: string
  error_handling: string
  rate_limit?: number
  version: string
  visibility: 'private' | 'organization' | 'public'
  mcp_compatible: boolean
}

// ─── Content Patterns ───
// Regex patterns that suggest tool usage in conversation content

const CONTENT_HINT_PATTERNS: Array<{ pattern: RegExp; tool_hint: string; confidence_boost: number }> = [
  // Generic action patterns
  { pattern: /let me (check|look up|search|verify|calculate|find)/i, tool_hint: 'lookup', confidence_boost: 0.2 },
  { pattern: /i'?ll (look that up|check|consult|pull up|verify)/i, tool_hint: 'lookup', confidence_boost: 0.2 },
  { pattern: /checking (the |our )?(system|database|records|inventory)/i, tool_hint: 'query', confidence_boost: 0.25 },
  { pattern: /consulting (the |our )?(database|system|catalog|records)/i, tool_hint: 'query', confidence_boost: 0.25 },
  { pattern: /according to (our|the) (system|records|database)/i, tool_hint: 'query', confidence_boost: 0.15 },
  { pattern: /i can see (in|from) (the|our) (system|records)/i, tool_hint: 'query', confidence_boost: 0.15 },
  { pattern: /scheduling|book(ing)? (an |your )?appointment/i, tool_hint: 'appointment_scheduler', confidence_boost: 0.3 },
  { pattern: /calculat(e|ing) (the |your )?(price|cost|total|payment|quote|premium)/i, tool_hint: 'calculator', confidence_boost: 0.3 },

  // Automotive patterns
  { pattern: /inventory|stock|available (vehicles|cars|units)/i, tool_hint: 'inventory_lookup', confidence_boost: 0.3 },
  { pattern: /trade.?in (value|valuation|appraisal)/i, tool_hint: 'trade_in_valuator', confidence_boost: 0.35 },
  { pattern: /financ(e|ing) (option|rate|term|payment)/i, tool_hint: 'financing_calculator', confidence_boost: 0.3 },
  { pattern: /insurance (quote|premium|coverage)/i, tool_hint: 'insurance_quoter', confidence_boost: 0.3 },
  { pattern: /compar(e|ing) (vehicles|models|options)/i, tool_hint: 'vehicle_comparator', confidence_boost: 0.3 },

  // Medical patterns
  { pattern: /medical (history|record|file)/i, tool_hint: 'medical_history_lookup', confidence_boost: 0.3 },
  { pattern: /medication|prescription|drug/i, tool_hint: 'medication_search', confidence_boost: 0.25 },
  { pattern: /lab (results?|test|work)/i, tool_hint: 'lab_results_checker', confidence_boost: 0.3 },
  { pattern: /symptom(s)?|diagnos(is|tic|e)/i, tool_hint: 'symptom_analyzer', confidence_boost: 0.25 },
  { pattern: /referral|specialist/i, tool_hint: 'referral_creator', confidence_boost: 0.25 },

  // Legal patterns
  { pattern: /case law|precedent|jurisprudenc/i, tool_hint: 'case_law_search', confidence_boost: 0.3 },
  { pattern: /statute|regulation|legal code/i, tool_hint: 'statute_lookup', confidence_boost: 0.3 },
  { pattern: /deadline|filing date|limitation period/i, tool_hint: 'deadline_calculator', confidence_boost: 0.3 },
  { pattern: /draft(ing)? (a |the )?(document|contract|agreement)/i, tool_hint: 'document_drafter', confidence_boost: 0.3 },
  { pattern: /conflict (of interest|check)/i, tool_hint: 'conflict_checker', confidence_boost: 0.35 },

  // Finance patterns
  { pattern: /portfolio|asset allocation|holdings/i, tool_hint: 'portfolio_analyzer', confidence_boost: 0.3 },
  { pattern: /risk (assessment|score|profil|tolerance)/i, tool_hint: 'risk_calculator', confidence_boost: 0.3 },
  { pattern: /market (data|price|quote)/i, tool_hint: 'market_data_fetcher', confidence_boost: 0.3 },
  { pattern: /compliance|regulat(ory|ion)/i, tool_hint: 'compliance_checker', confidence_boost: 0.25 },
  { pattern: /tax (calculation|implication|liability)/i, tool_hint: 'tax_calculator', confidence_boost: 0.3 },

  // Industrial patterns
  { pattern: /equipment (diagnostics?|status|health)/i, tool_hint: 'equipment_diagnostics', confidence_boost: 0.3 },
  { pattern: /parts? (inventory|availability|stock)/i, tool_hint: 'parts_inventory', confidence_boost: 0.3 },
  { pattern: /maintenance (schedule|plan|window)/i, tool_hint: 'maintenance_scheduler', confidence_boost: 0.3 },
  { pattern: /manual|documentation|spec sheet/i, tool_hint: 'manual_lookup', confidence_boost: 0.2 },
  { pattern: /sensor (data|reading|value)/i, tool_hint: 'sensor_data_reader', confidence_boost: 0.3 },
  { pattern: /incident (report|log)/i, tool_hint: 'incident_reporter', confidence_boost: 0.3 },
  { pattern: /calibration/i, tool_hint: 'calibration_checker', confidence_boost: 0.25 },

  // Education patterns
  { pattern: /curriculum|syllabus|course content/i, tool_hint: 'curriculum_browser', confidence_boost: 0.3 },
  { pattern: /progress|grade|score|performance/i, tool_hint: 'progress_tracker', confidence_boost: 0.2 },
  { pattern: /exercise|practice problem|worksheet/i, tool_hint: 'exercise_generator', confidence_boost: 0.3 },
  { pattern: /resource|reference material|textbook/i, tool_hint: 'resource_finder', confidence_boost: 0.2 },
  { pattern: /quiz|assessment|exam/i, tool_hint: 'quiz_generator', confidence_boost: 0.3 },
  { pattern: /learning path|study plan/i, tool_hint: 'learning_path_builder', confidence_boost: 0.3 },
]

// ─── Tool Pattern Templates ───
// Complete ScannedTool templates for every recognized tool across all 6 domains

const TOOL_PATTERNS: Record<string, ScannedTool> = {
  // ────────────────────────────────────────────────────────
  // automotive.sales
  // ────────────────────────────────────────────────────────
  inventory_lookup: {
    name: 'inventory_lookup',
    description: 'Search the dealership vehicle inventory by make, model, year, price range, and features',
    category: 'query',
    domains: ['automotive.sales'],
    method: 'GET',
    endpoint_url: '/api/v1/tools/automotive/inventory',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        make: { type: 'string', description: 'Vehicle manufacturer (e.g. Toyota, Ford, BMW)' },
        model: { type: 'string', description: 'Vehicle model name (e.g. Camry, F-150, X5)' },
        year_min: { type: 'integer', description: 'Minimum model year to filter by' },
        year_max: { type: 'integer', description: 'Maximum model year to filter by' },
        price_min: { type: 'number', description: 'Minimum price in USD' },
        price_max: { type: 'number', description: 'Maximum price in USD' },
        body_type: {
          type: 'string',
          description: 'Vehicle body type',
          enum: ['sedan', 'suv', 'truck', 'coupe', 'convertible', 'van', 'wagon', 'hatchback'],
        },
        is_new: { type: 'boolean', description: 'Filter for new (true) or pre-owned (false) vehicles' },
      },
      required: ['make'],
    },
    output_schema: {
      type: 'object',
      properties: {
        vehicles: { type: 'array', description: 'List of matching vehicles with details' },
        total_count: { type: 'integer', description: 'Total number of matches found' },
        filters_applied: { type: 'object', description: 'Echo of the filters that were applied' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Return cached inventory snapshot from the last 24 hours',
    error_handling: 'Log the error, return empty results with a user-friendly message indicating temporary unavailability',
    rate_limit: 60,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  quote_calculator: {
    name: 'quote_calculator',
    description: 'Generate a detailed price quote for a vehicle including taxes, fees, accessories, and applicable discounts',
    category: 'calculation',
    domains: ['automotive.sales'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/automotive/quote',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        vehicle_id: { type: 'string', description: 'Unique identifier of the vehicle from inventory' },
        accessories: { type: 'array', description: 'List of accessory package codes to include' },
        discount_code: { type: 'string', description: 'Promotional or loyalty discount code' },
        state: { type: 'string', description: 'US state abbreviation for tax calculation' },
        include_fees: { type: 'boolean', description: 'Whether to include dealer and registration fees' },
      },
      required: ['vehicle_id', 'state'],
    },
    output_schema: {
      type: 'object',
      properties: {
        base_price: { type: 'number', description: 'MSRP or listed price of the vehicle' },
        accessories_total: { type: 'number', description: 'Total cost of selected accessories' },
        discount_amount: { type: 'number', description: 'Total discount applied' },
        tax_amount: { type: 'number', description: 'Calculated tax based on state' },
        fees_total: { type: 'number', description: 'Sum of all applicable fees' },
        grand_total: { type: 'number', description: 'Final out-the-door price' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Calculate with default tax rates if state tax API is unreachable',
    error_handling: 'Return partial quote with missing fields marked as "pending" and notify the agent',
    rate_limit: 30,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  financing_calculator: {
    name: 'financing_calculator',
    description: 'Calculate monthly payments, interest totals, and loan terms for vehicle financing options',
    category: 'calculation',
    domains: ['automotive.sales'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/automotive/financing',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        vehicle_price: { type: 'number', description: 'Total vehicle price in USD' },
        down_payment: { type: 'number', description: 'Down payment amount in USD' },
        trade_in_value: { type: 'number', description: 'Trade-in credit to apply' },
        term_months: { type: 'integer', description: 'Loan term in months', enum: ['24', '36', '48', '60', '72', '84'] },
        credit_score_range: {
          type: 'string',
          description: 'Approximate credit score tier',
          enum: ['excellent', 'good', 'fair', 'poor'],
        },
        include_gap_insurance: { type: 'boolean', description: 'Include GAP insurance in the monthly payment' },
      },
      required: ['vehicle_price', 'term_months'],
    },
    output_schema: {
      type: 'object',
      properties: {
        monthly_payment: { type: 'number', description: 'Estimated monthly payment' },
        apr: { type: 'number', description: 'Annual percentage rate offered' },
        total_interest: { type: 'number', description: 'Total interest over the loan term' },
        total_cost: { type: 'number', description: 'Total amount paid over the loan term' },
        amount_financed: { type: 'number', description: 'Net amount financed after down payment and trade-in' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Use default APR table based on credit tier if lender API is offline',
    error_handling: 'Return estimate with a disclaimer that rates are subject to lender approval',
    rate_limit: 30,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  appointment_scheduler: {
    name: 'appointment_scheduler',
    description: 'Check availability and book test drive or service appointments at the dealership',
    category: 'action',
    domains: ['automotive.sales', 'medical.consultation'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/scheduling/appointments',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        appointment_type: {
          type: 'string',
          description: 'Type of appointment to schedule',
          enum: ['test_drive', 'service', 'consultation', 'follow_up'],
        },
        preferred_date: { type: 'string', description: 'Preferred date in ISO 8601 format (YYYY-MM-DD)' },
        preferred_time: { type: 'string', description: 'Preferred time slot (e.g. 09:00, 14:30)' },
        customer_name: { type: 'string', description: 'Full name of the customer' },
        customer_phone: { type: 'string', description: 'Contact phone number' },
        customer_email: { type: 'string', description: 'Contact email address' },
        notes: { type: 'string', description: 'Additional notes or special requests' },
      },
      required: ['appointment_type', 'preferred_date', 'preferred_time', 'customer_name'],
    },
    output_schema: {
      type: 'object',
      properties: {
        appointment_id: { type: 'string', description: 'Unique confirmation ID for the appointment' },
        confirmed_datetime: { type: 'string', description: 'Confirmed date and time in ISO 8601' },
        location: { type: 'string', description: 'Address or room where the appointment is scheduled' },
        status: { type: 'string', description: 'Appointment status (confirmed, pending, waitlisted)' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Queue the appointment request and confirm within 2 hours via email',
    error_handling: 'If scheduling system is down, collect details and create a callback request',
    rate_limit: 20,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  vehicle_comparator: {
    name: 'vehicle_comparator',
    description: 'Compare two or more vehicles side-by-side on specs, features, pricing, and ratings',
    category: 'query',
    domains: ['automotive.sales'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/automotive/compare',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        vehicle_ids: { type: 'array', description: 'List of vehicle IDs to compare (2-5)' },
        comparison_aspects: {
          type: 'array',
          description: 'Aspects to compare',
          enum: ['price', 'fuel_economy', 'safety', 'features', 'warranty', 'performance', 'all'],
        },
      },
      required: ['vehicle_ids'],
    },
    output_schema: {
      type: 'object',
      properties: {
        comparison_table: { type: 'object', description: 'Side-by-side comparison data for all requested aspects' },
        recommendation: { type: 'string', description: 'Brief recommendation based on the comparison' },
        winner_by_aspect: { type: 'object', description: 'Which vehicle wins in each comparison category' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Use cached vehicle spec sheets for comparison if live data is unavailable',
    error_handling: 'Compare available vehicles, note any missing data points in the response',
    rate_limit: 30,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  trade_in_valuator: {
    name: 'trade_in_valuator',
    description: 'Estimate the trade-in value of a vehicle based on make, model, year, mileage, and condition',
    category: 'calculation',
    domains: ['automotive.sales'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/automotive/trade-in',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        make: { type: 'string', description: 'Vehicle manufacturer' },
        model: { type: 'string', description: 'Vehicle model' },
        year: { type: 'integer', description: 'Model year' },
        mileage: { type: 'integer', description: 'Current odometer reading in miles' },
        condition: { type: 'string', description: 'Overall condition', enum: ['excellent', 'good', 'fair', 'poor'] },
        zip_code: { type: 'string', description: 'ZIP code for regional market adjustment' },
      },
      required: ['make', 'model', 'year', 'mileage', 'condition'],
    },
    output_schema: {
      type: 'object',
      properties: {
        estimated_value: { type: 'number', description: 'Estimated trade-in value in USD' },
        value_range_low: { type: 'number', description: 'Low end of the value range' },
        value_range_high: { type: 'number', description: 'High end of the value range' },
        market_trend: { type: 'string', description: 'Current market trend for this vehicle (rising, stable, falling)' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Use internal depreciation model if third-party valuation API is unavailable',
    error_handling: 'Return a range estimate with wider margins and flag as approximate',
    rate_limit: 20,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  insurance_quoter: {
    name: 'insurance_quoter',
    description: 'Generate an estimated insurance premium quote for a vehicle and driver profile',
    category: 'calculation',
    domains: ['automotive.sales'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/automotive/insurance-quote',
    auth_type: 'api_key',
    input_schema: {
      type: 'object',
      properties: {
        vehicle_id: { type: 'string', description: 'Vehicle identifier from inventory' },
        driver_age: { type: 'integer', description: 'Primary driver age' },
        driving_record: {
          type: 'string',
          description: 'Driving record summary',
          enum: ['clean', 'minor_violations', 'major_violations', 'accidents'],
        },
        coverage_level: { type: 'string', description: 'Coverage tier', enum: ['liability', 'standard', 'full', 'premium'] },
        state: { type: 'string', description: 'US state abbreviation' },
      },
      required: ['vehicle_id', 'driver_age', 'coverage_level', 'state'],
    },
    output_schema: {
      type: 'object',
      properties: {
        monthly_premium: { type: 'number', description: 'Estimated monthly insurance premium' },
        annual_premium: { type: 'number', description: 'Estimated annual insurance premium' },
        coverage_details: { type: 'object', description: 'Breakdown of coverage components and limits' },
        deductible: { type: 'number', description: 'Deductible amount for the selected plan' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Use average regional rates for the vehicle class if insurer API is unavailable',
    error_handling: 'Return estimate with disclaimer that actual rates require formal application',
    rate_limit: 15,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  document_verifier: {
    name: 'document_verifier',
    description: 'Verify the validity and completeness of customer-submitted documents (ID, proof of income, etc.)',
    category: 'validation',
    domains: ['automotive.sales'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/automotive/verify-document',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        document_type: {
          type: 'string',
          description: 'Type of document',
          enum: ['drivers_license', 'proof_of_income', 'proof_of_insurance', 'proof_of_residence', 'credit_report'],
        },
        document_id: { type: 'string', description: 'Internal document reference ID' },
        customer_id: { type: 'string', description: 'Customer profile ID' },
      },
      required: ['document_type', 'document_id'],
    },
    output_schema: {
      type: 'object',
      properties: {
        is_valid: { type: 'boolean', description: 'Whether the document passed validation' },
        issues: { type: 'array', description: 'List of issues found, if any' },
        expiration_date: { type: 'string', description: 'Document expiration date if applicable' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Flag for manual review if automated verification is unavailable',
    error_handling: 'Mark document as pending review and notify compliance team',
    rate_limit: 10,
    version: '1.0.0',
    visibility: 'private',
    mcp_compatible: false,
  },

  // ────────────────────────────────────────────────────────
  // medical.consultation
  // ────────────────────────────────────────────────────────
  medical_history_lookup: {
    name: 'medical_history_lookup',
    description: 'Retrieve a patient medical history summary including conditions, allergies, and prior treatments',
    category: 'retrieval',
    domains: ['medical.consultation'],
    method: 'GET',
    endpoint_url: '/api/v1/tools/medical/history',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        patient_id: { type: 'string', description: 'Anonymized patient identifier' },
        history_type: {
          type: 'string',
          description: 'Section of history to retrieve',
          enum: ['full', 'conditions', 'allergies', 'medications', 'surgeries', 'family'],
        },
        date_from: { type: 'string', description: 'Start date filter in ISO 8601' },
        date_to: { type: 'string', description: 'End date filter in ISO 8601' },
      },
      required: ['patient_id'],
    },
    output_schema: {
      type: 'object',
      properties: {
        patient_id: { type: 'string', description: 'Anonymized patient identifier' },
        conditions: { type: 'array', description: 'List of active and resolved conditions' },
        allergies: { type: 'array', description: 'Known allergies and severity' },
        current_medications: { type: 'array', description: 'Active prescriptions' },
        last_visit: { type: 'string', description: 'Date of most recent visit' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Return partial history from local cache with staleness warning',
    error_handling: 'Log access attempt, return error indicating EHR system is temporarily unavailable',
    rate_limit: 30,
    version: '1.0.0',
    visibility: 'private',
    mcp_compatible: false,
  },

  medication_search: {
    name: 'medication_search',
    description: 'Search the medication database for drug information, interactions, dosages, and contraindications',
    category: 'query',
    domains: ['medical.consultation'],
    method: 'GET',
    endpoint_url: '/api/v1/tools/medical/medications',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        drug_name: { type: 'string', description: 'Generic or brand name of the medication' },
        check_interactions_with: { type: 'array', description: 'List of other drug names to check interactions against' },
        include_generics: { type: 'boolean', description: 'Include generic alternatives in results' },
      },
      required: ['drug_name'],
    },
    output_schema: {
      type: 'object',
      properties: {
        drug_info: { type: 'object', description: 'Complete drug monograph summary' },
        interactions: { type: 'array', description: 'Potential interactions with specified medications' },
        contraindications: { type: 'array', description: 'Known contraindications' },
        generic_alternatives: { type: 'array', description: 'Available generic equivalents and pricing' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Query local formulary database if external drug API is unavailable',
    error_handling: 'Return cached drug info with warning that interaction data may not be current',
    rate_limit: 60,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  lab_results_checker: {
    name: 'lab_results_checker',
    description: 'Retrieve and interpret patient lab results with reference range comparison',
    category: 'retrieval',
    domains: ['medical.consultation'],
    method: 'GET',
    endpoint_url: '/api/v1/tools/medical/lab-results',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        patient_id: { type: 'string', description: 'Anonymized patient identifier' },
        test_type: {
          type: 'string',
          description: 'Type of lab test',
          enum: ['blood_panel', 'metabolic', 'lipid', 'thyroid', 'urinalysis', 'imaging', 'all'],
        },
        date_from: { type: 'string', description: 'Start date filter in ISO 8601' },
        include_trends: { type: 'boolean', description: 'Include historical trend data for each marker' },
      },
      required: ['patient_id'],
    },
    output_schema: {
      type: 'object',
      properties: {
        results: { type: 'array', description: 'Lab results with values and reference ranges' },
        abnormal_flags: { type: 'array', description: 'List of out-of-range results with severity' },
        trends: { type: 'object', description: 'Historical trends for key markers if requested' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Return most recent cached results with timestamp of last sync',
    error_handling: 'Log access, notify patient that results are temporarily unavailable, suggest callback',
    rate_limit: 30,
    version: '1.0.0',
    visibility: 'private',
    mcp_compatible: false,
  },

  insurance_verifier: {
    name: 'insurance_verifier',
    description: 'Verify patient insurance coverage, copay amounts, and pre-authorization requirements',
    category: 'validation',
    domains: ['medical.consultation'],
    method: 'GET',
    endpoint_url: '/api/v1/tools/medical/insurance-verify',
    auth_type: 'api_key',
    input_schema: {
      type: 'object',
      properties: {
        patient_id: { type: 'string', description: 'Patient identifier' },
        insurance_id: { type: 'string', description: 'Insurance policy number' },
        procedure_code: { type: 'string', description: 'CPT or ICD code for the procedure' },
        provider_npi: { type: 'string', description: 'Provider NPI number for network verification' },
      },
      required: ['patient_id', 'insurance_id'],
    },
    output_schema: {
      type: 'object',
      properties: {
        is_covered: { type: 'boolean', description: 'Whether the procedure is covered' },
        copay_amount: { type: 'number', description: 'Patient copay amount' },
        requires_preauth: { type: 'boolean', description: 'Whether pre-authorization is needed' },
        in_network: { type: 'boolean', description: 'Whether the provider is in-network' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Advise patient to contact their insurer directly for verification',
    error_handling: 'Flag as unverified and proceed with a disclaimer about potential out-of-pocket costs',
    rate_limit: 20,
    version: '1.0.0',
    visibility: 'private',
    mcp_compatible: false,
  },

  prescription_generator: {
    name: 'prescription_generator',
    description: 'Generate a structured prescription with dosage, frequency, duration, and pharmacy routing',
    category: 'action',
    domains: ['medical.consultation'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/medical/prescriptions',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        patient_id: { type: 'string', description: 'Anonymized patient identifier' },
        medication_name: { type: 'string', description: 'Drug name (generic or brand)' },
        dosage: { type: 'string', description: 'Dosage amount and unit (e.g. 500mg)' },
        frequency: { type: 'string', description: 'Dosing frequency (e.g. twice daily, every 8 hours)' },
        duration_days: { type: 'integer', description: 'Prescription duration in days' },
        refills: { type: 'integer', description: 'Number of refills authorized' },
        pharmacy_id: { type: 'string', description: 'Target pharmacy identifier for e-prescribing' },
      },
      required: ['patient_id', 'medication_name', 'dosage', 'frequency', 'duration_days'],
    },
    output_schema: {
      type: 'object',
      properties: {
        prescription_id: { type: 'string', description: 'Unique prescription identifier' },
        status: { type: 'string', description: 'Prescription status (sent, queued, requires_review)' },
        interaction_warnings: { type: 'array', description: 'Any drug interaction warnings detected' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Queue prescription for manual review by prescribing physician',
    error_handling: 'Block if critical interactions detected, otherwise queue with warnings for review',
    rate_limit: 10,
    version: '1.0.0',
    visibility: 'private',
    mcp_compatible: false,
  },

  symptom_analyzer: {
    name: 'symptom_analyzer',
    description: 'Analyze reported symptoms and suggest possible conditions with confidence scores',
    category: 'calculation',
    domains: ['medical.consultation'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/medical/symptoms',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        symptoms: { type: 'array', description: 'List of reported symptoms' },
        duration_days: { type: 'integer', description: 'How long symptoms have been present' },
        severity: { type: 'string', description: 'Overall severity', enum: ['mild', 'moderate', 'severe'] },
        patient_age: { type: 'integer', description: 'Patient age for demographic filtering' },
        patient_sex: { type: 'string', description: 'Biological sex for condition filtering', enum: ['male', 'female'] },
      },
      required: ['symptoms'],
    },
    output_schema: {
      type: 'object',
      properties: {
        possible_conditions: { type: 'array', description: 'Ranked list of possible conditions with confidence' },
        recommended_tests: { type: 'array', description: 'Suggested diagnostic tests' },
        urgency_level: { type: 'string', description: 'Recommended urgency (routine, urgent, emergency)' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Use rule-based symptom checker if ML model is unavailable',
    error_handling: 'Return disclaimer that this is not a diagnosis, recommend in-person consultation',
    rate_limit: 30,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  referral_creator: {
    name: 'referral_creator',
    description: 'Create a specialist referral with clinical summary, urgency, and preferred provider',
    category: 'action',
    domains: ['medical.consultation'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/medical/referrals',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        patient_id: { type: 'string', description: 'Anonymized patient identifier' },
        specialty: { type: 'string', description: 'Medical specialty for referral (e.g. cardiology, orthopedics)' },
        reason: { type: 'string', description: 'Clinical reason for referral' },
        urgency: { type: 'string', description: 'Referral urgency', enum: ['routine', 'urgent', 'stat'] },
        preferred_provider_id: { type: 'string', description: 'Preferred specialist provider ID if any' },
      },
      required: ['patient_id', 'specialty', 'reason'],
    },
    output_schema: {
      type: 'object',
      properties: {
        referral_id: { type: 'string', description: 'Unique referral tracking number' },
        status: { type: 'string', description: 'Referral status (submitted, pending_auth, approved)' },
        estimated_wait_days: { type: 'integer', description: 'Estimated wait time for specialist appointment' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Create paper referral and fax to specialist office',
    error_handling: 'Queue referral and notify both referring and receiving providers of system delay',
    rate_limit: 15,
    version: '1.0.0',
    visibility: 'private',
    mcp_compatible: false,
  },

  // ────────────────────────────────────────────────────────
  // legal.advisory
  // ────────────────────────────────────────────────────────
  case_law_search: {
    name: 'case_law_search',
    description: 'Search case law databases for relevant precedents, rulings, and judicial opinions',
    category: 'retrieval',
    domains: ['legal.advisory'],
    method: 'GET',
    endpoint_url: '/api/v1/tools/legal/case-law',
    auth_type: 'api_key',
    input_schema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Natural language search query or legal issue description' },
        jurisdiction: { type: 'string', description: 'Jurisdiction to search (e.g. federal, state name, EU)' },
        date_from: { type: 'string', description: 'Earliest decision date in ISO 8601' },
        date_to: { type: 'string', description: 'Latest decision date in ISO 8601' },
        court_level: { type: 'string', description: 'Court level filter', enum: ['supreme', 'appellate', 'district', 'all'] },
        max_results: { type: 'integer', description: 'Maximum number of results to return' },
      },
      required: ['query'],
    },
    output_schema: {
      type: 'object',
      properties: {
        cases: { type: 'array', description: 'List of matching cases with citations and summaries' },
        total_found: { type: 'integer', description: 'Total number of matching cases' },
        relevance_scores: { type: 'array', description: 'Relevance score for each returned case' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Search local case digest if external legal database is unreachable',
    error_handling: 'Return partial results with note about incomplete search scope',
    rate_limit: 30,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  statute_lookup: {
    name: 'statute_lookup',
    description: 'Look up statutes, regulations, and legal codes by citation or keyword',
    category: 'retrieval',
    domains: ['legal.advisory'],
    method: 'GET',
    endpoint_url: '/api/v1/tools/legal/statutes',
    auth_type: 'api_key',
    input_schema: {
      type: 'object',
      properties: {
        citation: { type: 'string', description: 'Specific statute citation (e.g. 26 USC 501(c)(3))' },
        keyword: { type: 'string', description: 'Keyword search within statute text' },
        jurisdiction: { type: 'string', description: 'Jurisdiction (federal, state name)' },
        include_amendments: { type: 'boolean', description: 'Include amendment history' },
      },
      required: [],
    },
    output_schema: {
      type: 'object',
      properties: {
        statute_text: { type: 'string', description: 'Full text of the statute section' },
        effective_date: { type: 'string', description: 'Date the current version became effective' },
        related_statutes: { type: 'array', description: 'Cross-referenced related statutes' },
        annotations: { type: 'array', description: 'Judicial annotations and interpretations' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Return cached version of statute with last-updated timestamp',
    error_handling: 'Provide citation link for manual lookup if electronic retrieval fails',
    rate_limit: 60,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  deadline_calculator: {
    name: 'deadline_calculator',
    description: 'Calculate legal deadlines, statutes of limitations, and filing due dates',
    category: 'calculation',
    domains: ['legal.advisory'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/legal/deadlines',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        event_date: { type: 'string', description: 'Date of the triggering event in ISO 8601' },
        deadline_type: {
          type: 'string',
          description: 'Type of deadline',
          enum: ['statute_of_limitations', 'filing', 'response', 'appeal', 'discovery', 'custom'],
        },
        jurisdiction: { type: 'string', description: 'Jurisdiction for deadline rules' },
        case_type: { type: 'string', description: 'Type of legal matter (e.g. personal_injury, contract, criminal)' },
        exclude_weekends: { type: 'boolean', description: 'Exclude weekends from calculation' },
        exclude_holidays: { type: 'boolean', description: 'Exclude court holidays from calculation' },
      },
      required: ['event_date', 'deadline_type', 'jurisdiction'],
    },
    output_schema: {
      type: 'object',
      properties: {
        deadline_date: { type: 'string', description: 'Calculated deadline date' },
        calendar_days: { type: 'integer', description: 'Number of calendar days from event' },
        business_days: { type: 'integer', description: 'Number of business days from event' },
        applicable_rule: { type: 'string', description: 'The rule or statute governing this deadline' },
        warnings: { type: 'array', description: 'Any tolling or extension considerations' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Calculate using general rules and flag for attorney verification',
    error_handling: 'Return conservative estimate (shortest applicable deadline) with verification notice',
    rate_limit: 30,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  document_drafter: {
    name: 'document_drafter',
    description: 'Generate a draft legal document from a template with populated client and case details',
    category: 'action',
    domains: ['legal.advisory'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/legal/draft',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        document_type: {
          type: 'string',
          description: 'Type of document to draft',
          enum: ['contract', 'motion', 'brief', 'letter', 'agreement', 'nda', 'complaint', 'response'],
        },
        template_id: { type: 'string', description: 'Template identifier to use as a base' },
        variables: { type: 'object', description: 'Key-value pairs to populate template fields' },
        jurisdiction: { type: 'string', description: 'Applicable jurisdiction' },
        language: { type: 'string', description: 'Document language', enum: ['en', 'es'] },
      },
      required: ['document_type', 'variables'],
    },
    output_schema: {
      type: 'object',
      properties: {
        draft_id: { type: 'string', description: 'Unique identifier for the generated draft' },
        content_preview: { type: 'string', description: 'First 500 characters of the draft' },
        word_count: { type: 'integer', description: 'Total word count of the draft' },
        review_required: { type: 'boolean', description: 'Whether attorney review is mandatory before use' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Provide blank template with instructions for manual completion',
    error_handling: 'Generate partial draft with clearly marked placeholder sections requiring input',
    rate_limit: 10,
    version: '1.0.0',
    visibility: 'private',
    mcp_compatible: false,
  },

  fee_calculator: {
    name: 'fee_calculator',
    description: 'Calculate legal fees, court costs, and estimated total cost for a case or transaction',
    category: 'calculation',
    domains: ['legal.advisory'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/legal/fees',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        case_type: { type: 'string', description: 'Type of legal matter' },
        billing_model: { type: 'string', description: 'Billing arrangement', enum: ['hourly', 'flat', 'contingency', 'retainer'] },
        estimated_hours: { type: 'number', description: 'Estimated hours for hourly billing' },
        court_filing: { type: 'boolean', description: 'Whether court filing fees apply' },
        jurisdiction: { type: 'string', description: 'Jurisdiction for fee schedules' },
      },
      required: ['case_type', 'billing_model'],
    },
    output_schema: {
      type: 'object',
      properties: {
        attorney_fees: { type: 'number', description: 'Estimated attorney fees' },
        court_costs: { type: 'number', description: 'Estimated court filing and service costs' },
        total_estimate: { type: 'number', description: 'Total estimated cost' },
        fee_schedule: { type: 'object', description: 'Breakdown of fee components' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Use standard fee schedule from firm rate card',
    error_handling: 'Return estimate range instead of point estimate if data is incomplete',
    rate_limit: 30,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  court_filing_tracker: {
    name: 'court_filing_tracker',
    description: 'Track the status of court filings, motions, and case proceedings',
    category: 'query',
    domains: ['legal.advisory'],
    method: 'GET',
    endpoint_url: '/api/v1/tools/legal/filings',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        case_number: { type: 'string', description: 'Court case number' },
        filing_id: { type: 'string', description: 'Specific filing identifier' },
        status_filter: { type: 'string', description: 'Filter by status', enum: ['pending', 'accepted', 'rejected', 'all'] },
      },
      required: ['case_number'],
    },
    output_schema: {
      type: 'object',
      properties: {
        filings: { type: 'array', description: 'List of filings with status and timestamps' },
        next_hearing: { type: 'string', description: 'Date of next scheduled hearing' },
        case_status: { type: 'string', description: 'Overall case status' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Return last known filing status from local records',
    error_handling: 'Note that court electronic systems may have delays and suggest checking the court portal',
    rate_limit: 30,
    version: '1.0.0',
    visibility: 'private',
    mcp_compatible: false,
  },

  client_record_lookup: {
    name: 'client_record_lookup',
    description: 'Look up client records including contact info, case history, and billing status',
    category: 'retrieval',
    domains: ['legal.advisory'],
    method: 'GET',
    endpoint_url: '/api/v1/tools/legal/clients',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        client_id: { type: 'string', description: 'Client identifier' },
        include_cases: { type: 'boolean', description: 'Include associated case summaries' },
        include_billing: { type: 'boolean', description: 'Include billing history' },
      },
      required: ['client_id'],
    },
    output_schema: {
      type: 'object',
      properties: {
        client_info: { type: 'object', description: 'Client contact and demographic information' },
        active_cases: { type: 'array', description: 'List of active cases' },
        billing_summary: { type: 'object', description: 'Outstanding balance and payment history' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Return cached client profile from local CRM',
    error_handling: 'Return partial record with indication of which sections could not be loaded',
    rate_limit: 30,
    version: '1.0.0',
    visibility: 'private',
    mcp_compatible: false,
  },

  conflict_checker: {
    name: 'conflict_checker',
    description: 'Check for conflicts of interest against the firm client and matter database',
    category: 'validation',
    domains: ['legal.advisory'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/legal/conflict-check',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        party_names: { type: 'array', description: 'Names of all parties to check' },
        matter_description: { type: 'string', description: 'Brief description of the legal matter' },
        check_related_entities: { type: 'boolean', description: 'Also check known related entities and affiliates' },
      },
      required: ['party_names'],
    },
    output_schema: {
      type: 'object',
      properties: {
        has_conflict: { type: 'boolean', description: 'Whether any conflicts were found' },
        conflicts: { type: 'array', description: 'Details of each conflict found' },
        cleared_parties: { type: 'array', description: 'Parties that passed the conflict check' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Flag as uncleared and require manual review by ethics committee',
    error_handling: 'Treat as potentially conflicted until manual verification is completed',
    rate_limit: 15,
    version: '1.0.0',
    visibility: 'private',
    mcp_compatible: false,
  },

  // ────────────────────────────────────────────────────────
  // finance.advisory
  // ────────────────────────────────────────────────────────
  portfolio_analyzer: {
    name: 'portfolio_analyzer',
    description: 'Analyze an investment portfolio for allocation, performance, risk exposure, and diversification',
    category: 'calculation',
    domains: ['finance.advisory'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/finance/portfolio',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        portfolio_id: { type: 'string', description: 'Portfolio identifier' },
        analysis_type: {
          type: 'string',
          description: 'Type of analysis',
          enum: ['allocation', 'performance', 'risk', 'diversification', 'comprehensive'],
        },
        benchmark: { type: 'string', description: 'Benchmark index for comparison (e.g. SP500, NASDAQ)' },
        period: { type: 'string', description: 'Analysis period', enum: ['1m', '3m', '6m', '1y', '3y', '5y', 'ytd'] },
      },
      required: ['portfolio_id'],
    },
    output_schema: {
      type: 'object',
      properties: {
        allocation: { type: 'object', description: 'Current asset allocation breakdown by class' },
        performance: { type: 'object', description: 'Returns, alpha, beta, and Sharpe ratio' },
        risk_metrics: { type: 'object', description: 'VaR, max drawdown, volatility measures' },
        recommendations: { type: 'array', description: 'Rebalancing suggestions based on analysis' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Use end-of-day data if real-time market feed is unavailable',
    error_handling: 'Return analysis with last available data and timestamp indicating data freshness',
    rate_limit: 20,
    version: '1.0.0',
    visibility: 'private',
    mcp_compatible: false,
  },

  risk_calculator: {
    name: 'risk_calculator',
    description: 'Calculate risk scores and profiles for investments, loans, or client suitability assessments',
    category: 'calculation',
    domains: ['finance.advisory'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/finance/risk',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        assessment_type: {
          type: 'string',
          description: 'Type of risk assessment',
          enum: ['investment', 'credit', 'suitability', 'market'],
        },
        client_profile: { type: 'object', description: 'Client demographic and financial profile data' },
        investment_horizon: { type: 'string', description: 'Investment time horizon', enum: ['short', 'medium', 'long'] },
        risk_tolerance: { type: 'string', description: 'Stated risk tolerance', enum: ['conservative', 'moderate', 'aggressive'] },
      },
      required: ['assessment_type'],
    },
    output_schema: {
      type: 'object',
      properties: {
        risk_score: { type: 'number', description: 'Numerical risk score (0-100)' },
        risk_category: { type: 'string', description: 'Risk category classification' },
        factors: { type: 'array', description: 'Contributing risk factors with weights' },
        suitable_products: { type: 'array', description: 'Product types suitable for this risk profile' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Use questionnaire-based risk profiling if quantitative model is unavailable',
    error_handling: 'Return conservative risk assessment with note about limited data inputs',
    rate_limit: 20,
    version: '1.0.0',
    visibility: 'private',
    mcp_compatible: false,
  },

  market_data_fetcher: {
    name: 'market_data_fetcher',
    description: 'Fetch real-time or historical market data for securities, indices, and commodities',
    category: 'retrieval',
    domains: ['finance.advisory'],
    method: 'GET',
    endpoint_url: '/api/v1/tools/finance/market-data',
    auth_type: 'api_key',
    input_schema: {
      type: 'object',
      properties: {
        symbols: { type: 'array', description: 'List of ticker symbols to fetch' },
        data_type: { type: 'string', description: 'Type of data', enum: ['quote', 'historical', 'intraday', 'fundamentals'] },
        interval: { type: 'string', description: 'Data interval for historical/intraday', enum: ['1min', '5min', '15min', '1h', '1d', '1w'] },
        date_from: { type: 'string', description: 'Start date for historical data' },
        date_to: { type: 'string', description: 'End date for historical data' },
      },
      required: ['symbols', 'data_type'],
    },
    output_schema: {
      type: 'object',
      properties: {
        quotes: { type: 'array', description: 'Price quotes with bid, ask, last, volume' },
        timestamp: { type: 'string', description: 'Data timestamp' },
        market_status: { type: 'string', description: 'Market open/closed status' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Return last cached quote with staleness indicator',
    error_handling: 'Return available data with note about which symbols could not be fetched',
    rate_limit: 120,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  compliance_checker: {
    name: 'compliance_checker',
    description: 'Check a proposed transaction or recommendation against regulatory compliance rules',
    category: 'validation',
    domains: ['finance.advisory'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/finance/compliance',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        transaction_type: { type: 'string', description: 'Type of transaction to check' },
        client_id: { type: 'string', description: 'Client identifier' },
        amount: { type: 'number', description: 'Transaction amount in USD' },
        security_id: { type: 'string', description: 'Security identifier if applicable' },
        regulation_set: {
          type: 'string',
          description: 'Regulation framework to check against',
          enum: ['sec', 'finra', 'mifid2', 'dodd_frank', 'all'],
        },
      },
      required: ['transaction_type', 'client_id'],
    },
    output_schema: {
      type: 'object',
      properties: {
        is_compliant: { type: 'boolean', description: 'Whether the transaction passes compliance' },
        violations: { type: 'array', description: 'List of compliance violations found' },
        required_disclosures: { type: 'array', description: 'Mandatory disclosures for this transaction' },
        approval_required: { type: 'boolean', description: 'Whether supervisor approval is needed' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Flag for manual compliance officer review',
    error_handling: 'Block transaction and escalate to compliance team for manual review',
    rate_limit: 30,
    version: '1.0.0',
    visibility: 'private',
    mcp_compatible: false,
  },

  investment_simulator: {
    name: 'investment_simulator',
    description: 'Run Monte Carlo or scenario-based simulations on investment strategies',
    category: 'calculation',
    domains: ['finance.advisory'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/finance/simulate',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        initial_investment: { type: 'number', description: 'Initial investment amount' },
        monthly_contribution: { type: 'number', description: 'Monthly contribution amount' },
        allocation: { type: 'object', description: 'Asset allocation percentages by class' },
        horizon_years: { type: 'integer', description: 'Investment horizon in years' },
        simulations: { type: 'integer', description: 'Number of Monte Carlo simulations to run' },
        inflation_adjusted: { type: 'boolean', description: 'Whether to adjust returns for inflation' },
      },
      required: ['initial_investment', 'allocation', 'horizon_years'],
    },
    output_schema: {
      type: 'object',
      properties: {
        median_outcome: { type: 'number', description: 'Median portfolio value at end of horizon' },
        percentile_10: { type: 'number', description: '10th percentile (pessimistic) outcome' },
        percentile_90: { type: 'number', description: '90th percentile (optimistic) outcome' },
        probability_of_target: { type: 'number', description: 'Probability of reaching target if specified' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Use simplified compound growth model instead of Monte Carlo',
    error_handling: 'Return simplified projection with disclaimer about model limitations',
    rate_limit: 10,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  tax_calculator: {
    name: 'tax_calculator',
    description: 'Calculate tax implications of financial transactions including capital gains and deductions',
    category: 'calculation',
    domains: ['finance.advisory'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/finance/tax',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        transaction_type: {
          type: 'string',
          description: 'Type of taxable event',
          enum: ['capital_gain', 'dividend', 'interest', 'distribution', 'conversion'],
        },
        amount: { type: 'number', description: 'Transaction amount' },
        cost_basis: { type: 'number', description: 'Cost basis for gain/loss calculation' },
        holding_period_days: { type: 'integer', description: 'Number of days the asset was held' },
        tax_bracket: { type: 'string', description: 'Federal tax bracket', enum: ['10', '12', '22', '24', '32', '35', '37'] },
        state: { type: 'string', description: 'US state for state tax calculation' },
      },
      required: ['transaction_type', 'amount'],
    },
    output_schema: {
      type: 'object',
      properties: {
        federal_tax: { type: 'number', description: 'Estimated federal tax liability' },
        state_tax: { type: 'number', description: 'Estimated state tax liability' },
        net_after_tax: { type: 'number', description: 'Net amount after taxes' },
        tax_rate_effective: { type: 'number', description: 'Effective tax rate applied' },
        holding_type: { type: 'string', description: 'Short-term or long-term classification' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Calculate using current year federal rates only, omit state calculation',
    error_handling: 'Return estimate with disclaimer to consult a tax professional for actual filing',
    rate_limit: 30,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  account_lookup: {
    name: 'account_lookup',
    description: 'Look up client account details including balances, positions, and recent activity',
    category: 'retrieval',
    domains: ['finance.advisory'],
    method: 'GET',
    endpoint_url: '/api/v1/tools/finance/accounts',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        account_id: { type: 'string', description: 'Account identifier' },
        include_positions: { type: 'boolean', description: 'Include current position details' },
        include_activity: { type: 'boolean', description: 'Include recent transaction activity' },
        activity_days: { type: 'integer', description: 'Number of days of activity to include' },
      },
      required: ['account_id'],
    },
    output_schema: {
      type: 'object',
      properties: {
        account_summary: { type: 'object', description: 'Account type, balance, and status' },
        positions: { type: 'array', description: 'Current holdings with market values' },
        recent_activity: { type: 'array', description: 'Recent transactions' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Return last known account snapshot with timestamp',
    error_handling: 'Return cached data with staleness warning if live system is unavailable',
    rate_limit: 30,
    version: '1.0.0',
    visibility: 'private',
    mcp_compatible: false,
  },

  transaction_history: {
    name: 'transaction_history',
    description: 'Retrieve detailed transaction history for an account with filtering and export options',
    category: 'retrieval',
    domains: ['finance.advisory'],
    method: 'GET',
    endpoint_url: '/api/v1/tools/finance/transactions',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        account_id: { type: 'string', description: 'Account identifier' },
        date_from: { type: 'string', description: 'Start date in ISO 8601' },
        date_to: { type: 'string', description: 'End date in ISO 8601' },
        transaction_type: { type: 'string', description: 'Filter by type', enum: ['buy', 'sell', 'dividend', 'transfer', 'fee', 'all'] },
        min_amount: { type: 'number', description: 'Minimum transaction amount filter' },
      },
      required: ['account_id'],
    },
    output_schema: {
      type: 'object',
      properties: {
        transactions: { type: 'array', description: 'List of transactions with full details' },
        total_count: { type: 'integer', description: 'Total number of matching transactions' },
        summary: { type: 'object', description: 'Aggregate summary (total buys, sells, dividends, fees)' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Return statement-based summary if detailed transaction log is unavailable',
    error_handling: 'Return partial results with note about date range limitations',
    rate_limit: 20,
    version: '1.0.0',
    visibility: 'private',
    mcp_compatible: false,
  },

  // ────────────────────────────────────────────────────────
  // industrial.support
  // ────────────────────────────────────────────────────────
  equipment_diagnostics: {
    name: 'equipment_diagnostics',
    description: 'Run diagnostic checks on industrial equipment and return health status and fault codes',
    category: 'query',
    domains: ['industrial.support'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/industrial/diagnostics',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        equipment_id: { type: 'string', description: 'Unique equipment or asset identifier' },
        diagnostic_type: {
          type: 'string',
          description: 'Type of diagnostic to run',
          enum: ['quick', 'full', 'specific_system', 'predictive'],
        },
        system_filter: { type: 'string', description: 'Specific subsystem to diagnose (e.g. hydraulic, electrical, pneumatic)' },
        include_history: { type: 'boolean', description: 'Include previous diagnostic results for comparison' },
      },
      required: ['equipment_id'],
    },
    output_schema: {
      type: 'object',
      properties: {
        health_score: { type: 'number', description: 'Overall health score (0-100)' },
        fault_codes: { type: 'array', description: 'Active fault codes with descriptions' },
        warnings: { type: 'array', description: 'Predictive maintenance warnings' },
        recommended_actions: { type: 'array', description: 'Suggested maintenance or repair actions' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Return last known diagnostic snapshot and recommend on-site inspection',
    error_handling: 'Log connectivity issue, advise manual inspection, create maintenance ticket',
    rate_limit: 15,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  parts_inventory: {
    name: 'parts_inventory',
    description: 'Check availability, pricing, and delivery estimates for replacement parts',
    category: 'query',
    domains: ['industrial.support'],
    method: 'GET',
    endpoint_url: '/api/v1/tools/industrial/parts',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        part_number: { type: 'string', description: 'Manufacturer part number' },
        equipment_id: { type: 'string', description: 'Equipment ID to find compatible parts' },
        keyword: { type: 'string', description: 'Keyword search for part description' },
        warehouse_id: { type: 'string', description: 'Specific warehouse to check stock' },
        include_alternatives: { type: 'boolean', description: 'Include compatible alternative parts' },
      },
      required: [],
    },
    output_schema: {
      type: 'object',
      properties: {
        parts: { type: 'array', description: 'Matching parts with stock levels and pricing' },
        in_stock: { type: 'boolean', description: 'Whether primary part is in stock' },
        estimated_delivery: { type: 'string', description: 'Estimated delivery date if not in stock' },
        alternatives: { type: 'array', description: 'Compatible alternative parts if requested' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Check backup supplier catalog if primary inventory system is down',
    error_handling: 'Return cached stock levels with timestamp and recommend direct warehouse contact',
    rate_limit: 60,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  maintenance_scheduler: {
    name: 'maintenance_scheduler',
    description: 'Schedule preventive or corrective maintenance windows for equipment',
    category: 'action',
    domains: ['industrial.support'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/industrial/maintenance',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        equipment_id: { type: 'string', description: 'Equipment identifier' },
        maintenance_type: {
          type: 'string',
          description: 'Type of maintenance',
          enum: ['preventive', 'corrective', 'predictive', 'emergency'],
        },
        priority: { type: 'string', description: 'Priority level', enum: ['low', 'medium', 'high', 'critical'] },
        preferred_window: { type: 'string', description: 'Preferred maintenance window (e.g. weekend, night_shift)' },
        estimated_duration_hours: { type: 'number', description: 'Estimated maintenance duration in hours' },
        required_parts: { type: 'array', description: 'List of part numbers needed' },
      },
      required: ['equipment_id', 'maintenance_type', 'priority'],
    },
    output_schema: {
      type: 'object',
      properties: {
        work_order_id: { type: 'string', description: 'Generated work order ID' },
        scheduled_datetime: { type: 'string', description: 'Scheduled maintenance start time' },
        assigned_technician: { type: 'string', description: 'Assigned maintenance technician' },
        parts_status: { type: 'string', description: 'Whether all required parts are available' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Create offline work order and sync when CMMS is back online',
    error_handling: 'Queue the request and send email notification to maintenance supervisor',
    rate_limit: 15,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  manual_lookup: {
    name: 'manual_lookup',
    description: 'Search equipment manuals, technical documentation, and spec sheets',
    category: 'retrieval',
    domains: ['industrial.support'],
    method: 'GET',
    endpoint_url: '/api/v1/tools/industrial/manuals',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        equipment_id: { type: 'string', description: 'Equipment identifier' },
        query: { type: 'string', description: 'Search query within the documentation' },
        document_type: {
          type: 'string',
          description: 'Type of document',
          enum: ['user_manual', 'service_manual', 'spec_sheet', 'safety_bulletin', 'all'],
        },
        section: { type: 'string', description: 'Specific manual section (e.g. troubleshooting, installation)' },
      },
      required: ['equipment_id'],
    },
    output_schema: {
      type: 'object',
      properties: {
        results: { type: 'array', description: 'Matching documentation sections with content' },
        document_title: { type: 'string', description: 'Title of the source document' },
        page_references: { type: 'array', description: 'Page numbers for physical manual cross-reference' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Search offline PDF index of equipment manuals',
    error_handling: 'Return document metadata with download link for manual review',
    rate_limit: 60,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  incident_reporter: {
    name: 'incident_reporter',
    description: 'File an incident report for equipment failures, safety events, or quality issues',
    category: 'action',
    domains: ['industrial.support'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/industrial/incidents',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        equipment_id: { type: 'string', description: 'Equipment involved in the incident' },
        incident_type: {
          type: 'string',
          description: 'Type of incident',
          enum: ['equipment_failure', 'safety_event', 'quality_issue', 'near_miss', 'environmental'],
        },
        severity: { type: 'string', description: 'Incident severity', enum: ['minor', 'moderate', 'major', 'critical'] },
        description: { type: 'string', description: 'Detailed description of the incident' },
        reporter_id: { type: 'string', description: 'ID of the person reporting' },
        immediate_actions: { type: 'string', description: 'Immediate actions taken' },
      },
      required: ['equipment_id', 'incident_type', 'severity', 'description'],
    },
    output_schema: {
      type: 'object',
      properties: {
        incident_id: { type: 'string', description: 'Generated incident report ID' },
        status: { type: 'string', description: 'Report status (filed, escalated, under_investigation)' },
        notifications_sent: { type: 'array', description: 'List of stakeholders notified' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Create paper-based incident report form and queue for digital entry',
    error_handling: 'Store locally and retry submission, escalate to safety manager via direct notification',
    rate_limit: 10,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  sensor_data_reader: {
    name: 'sensor_data_reader',
    description: 'Read real-time or historical sensor data from IoT-connected industrial equipment',
    category: 'retrieval',
    domains: ['industrial.support'],
    method: 'GET',
    endpoint_url: '/api/v1/tools/industrial/sensors',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        equipment_id: { type: 'string', description: 'Equipment identifier' },
        sensor_type: {
          type: 'string',
          description: 'Type of sensor',
          enum: ['temperature', 'pressure', 'vibration', 'flow', 'humidity', 'current', 'all'],
        },
        time_range: { type: 'string', description: 'Time range for data', enum: ['live', '1h', '6h', '24h', '7d', '30d'] },
        aggregation: { type: 'string', description: 'Data aggregation', enum: ['raw', 'avg', 'min', 'max', 'p95'] },
      },
      required: ['equipment_id', 'sensor_type'],
    },
    output_schema: {
      type: 'object',
      properties: {
        readings: { type: 'array', description: 'Sensor readings with timestamps and values' },
        current_value: { type: 'number', description: 'Most recent reading' },
        normal_range: { type: 'object', description: 'Expected normal range for this sensor' },
        is_in_range: { type: 'boolean', description: 'Whether current value is within normal range' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Return last cached readings with timestamp indicating data age',
    error_handling: 'Note sensor connectivity issue and recommend manual gauge reading',
    rate_limit: 120,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  calibration_checker: {
    name: 'calibration_checker',
    description: 'Check calibration status and history of instruments and measuring equipment',
    category: 'validation',
    domains: ['industrial.support'],
    method: 'GET',
    endpoint_url: '/api/v1/tools/industrial/calibration',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        instrument_id: { type: 'string', description: 'Instrument or gauge identifier' },
        include_history: { type: 'boolean', description: 'Include calibration history records' },
        check_certificate: { type: 'boolean', description: 'Verify calibration certificate validity' },
      },
      required: ['instrument_id'],
    },
    output_schema: {
      type: 'object',
      properties: {
        is_calibrated: { type: 'boolean', description: 'Whether instrument is currently calibrated' },
        last_calibration: { type: 'string', description: 'Date of last calibration' },
        next_due: { type: 'string', description: 'Next calibration due date' },
        certificate_valid: { type: 'boolean', description: 'Whether calibration certificate is valid' },
        drift_detected: { type: 'boolean', description: 'Whether any drift has been detected since last calibration' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Return last known calibration record from local database',
    error_handling: 'Flag instrument as "calibration status unknown" and schedule recalibration',
    rate_limit: 30,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  safety_validator: {
    name: 'safety_validator',
    description: 'Validate that safety protocols, lockout/tagout procedures, and PPE requirements are met',
    category: 'validation',
    domains: ['industrial.support'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/industrial/safety-check',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        work_order_id: { type: 'string', description: 'Work order to validate safety for' },
        procedure_type: {
          type: 'string',
          description: 'Type of safety procedure',
          enum: ['lockout_tagout', 'confined_space', 'hot_work', 'electrical', 'chemical', 'general'],
        },
        personnel_ids: { type: 'array', description: 'IDs of personnel involved to verify certifications' },
        equipment_id: { type: 'string', description: 'Equipment identifier for hazard assessment' },
      },
      required: ['work_order_id', 'procedure_type'],
    },
    output_schema: {
      type: 'object',
      properties: {
        is_safe_to_proceed: { type: 'boolean', description: 'Whether all safety requirements are met' },
        checklist_items: { type: 'array', description: 'Safety checklist with pass/fail status for each item' },
        missing_requirements: { type: 'array', description: 'Unmet safety requirements that must be addressed' },
        ppe_required: { type: 'array', description: 'Required PPE for this procedure' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Require full manual safety checklist completion before proceeding',
    error_handling: 'Block work authorization and require in-person safety supervisor sign-off',
    rate_limit: 15,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  // ────────────────────────────────────────────────────────
  // education.tutoring
  // ────────────────────────────────────────────────────────
  curriculum_browser: {
    name: 'curriculum_browser',
    description: 'Browse and search curriculum content, learning objectives, and course structures',
    category: 'retrieval',
    domains: ['education.tutoring'],
    method: 'GET',
    endpoint_url: '/api/v1/tools/education/curriculum',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        subject: { type: 'string', description: 'Academic subject (e.g. mathematics, physics, history)' },
        grade_level: { type: 'string', description: 'Grade or education level', enum: ['elementary', 'middle', 'high', 'undergraduate', 'graduate'] },
        topic: { type: 'string', description: 'Specific topic within the subject' },
        standard: { type: 'string', description: 'Educational standard framework (e.g. common_core, ib, ap)' },
      },
      required: ['subject'],
    },
    output_schema: {
      type: 'object',
      properties: {
        units: { type: 'array', description: 'Curriculum units with learning objectives' },
        prerequisites: { type: 'array', description: 'Required prerequisite knowledge' },
        estimated_hours: { type: 'number', description: 'Estimated hours to complete the topic' },
        resources: { type: 'array', description: 'Recommended learning resources' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Return cached curriculum outline for the subject area',
    error_handling: 'Provide general topic outline with note about limited curriculum data availability',
    rate_limit: 60,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  progress_tracker: {
    name: 'progress_tracker',
    description: 'Track and report student learning progress, mastery levels, and completion status',
    category: 'query',
    domains: ['education.tutoring'],
    method: 'GET',
    endpoint_url: '/api/v1/tools/education/progress',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        student_id: { type: 'string', description: 'Student identifier' },
        subject: { type: 'string', description: 'Subject to check progress for' },
        date_from: { type: 'string', description: 'Start date for progress period' },
        include_details: { type: 'boolean', description: 'Include per-topic mastery breakdown' },
      },
      required: ['student_id'],
    },
    output_schema: {
      type: 'object',
      properties: {
        overall_progress: { type: 'number', description: 'Overall completion percentage' },
        mastery_level: { type: 'string', description: 'Current mastery classification' },
        topics_completed: { type: 'array', description: 'List of completed topics' },
        topics_in_progress: { type: 'array', description: 'Topics currently being studied' },
        weak_areas: { type: 'array', description: 'Areas needing additional practice' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Return last synced progress snapshot from local student profile',
    error_handling: 'Return available data with note about last sync timestamp',
    rate_limit: 30,
    version: '1.0.0',
    visibility: 'private',
    mcp_compatible: false,
  },

  exercise_generator: {
    name: 'exercise_generator',
    description: 'Generate practice exercises, problems, and worked examples for a given topic and difficulty',
    category: 'action',
    domains: ['education.tutoring'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/education/exercises',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        topic: { type: 'string', description: 'Topic for the exercises' },
        difficulty: { type: 'string', description: 'Difficulty level', enum: ['beginner', 'intermediate', 'advanced'] },
        count: { type: 'integer', description: 'Number of exercises to generate' },
        exercise_type: {
          type: 'string',
          description: 'Type of exercise',
          enum: ['multiple_choice', 'short_answer', 'worked_example', 'problem_set', 'fill_in_blank'],
        },
        include_solutions: { type: 'boolean', description: 'Include solutions and explanations' },
        student_id: { type: 'string', description: 'Student ID for personalized difficulty adjustment' },
      },
      required: ['topic', 'difficulty', 'count'],
    },
    output_schema: {
      type: 'object',
      properties: {
        exercises: { type: 'array', description: 'Generated exercises with prompts' },
        solutions: { type: 'array', description: 'Solutions and step-by-step explanations' },
        estimated_time_minutes: { type: 'number', description: 'Estimated time to complete all exercises' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Draw from pre-generated exercise bank for the topic',
    error_handling: 'Return exercises from the cached pool with note about limited variety',
    rate_limit: 20,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  resource_finder: {
    name: 'resource_finder',
    description: 'Find learning resources including videos, articles, textbooks, and interactive content',
    category: 'retrieval',
    domains: ['education.tutoring'],
    method: 'GET',
    endpoint_url: '/api/v1/tools/education/resources',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        topic: { type: 'string', description: 'Topic to find resources for' },
        resource_type: {
          type: 'string',
          description: 'Type of resource',
          enum: ['video', 'article', 'textbook', 'interactive', 'worksheet', 'all'],
        },
        difficulty: { type: 'string', description: 'Difficulty level', enum: ['beginner', 'intermediate', 'advanced'] },
        language: { type: 'string', description: 'Preferred content language', enum: ['en', 'es'] },
        max_results: { type: 'integer', description: 'Maximum resources to return' },
      },
      required: ['topic'],
    },
    output_schema: {
      type: 'object',
      properties: {
        resources: { type: 'array', description: 'List of resources with titles, URLs, and descriptions' },
        total_found: { type: 'integer', description: 'Total matching resources' },
        recommended: { type: 'string', description: 'Top recommended resource with rationale' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Return curated list of high-quality open educational resources',
    error_handling: 'Return cached resource list with note about possibly outdated availability',
    rate_limit: 60,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  session_scheduler: {
    name: 'session_scheduler',
    description: 'Schedule tutoring sessions with availability checking and calendar integration',
    category: 'action',
    domains: ['education.tutoring'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/education/sessions',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        student_id: { type: 'string', description: 'Student identifier' },
        tutor_id: { type: 'string', description: 'Preferred tutor identifier' },
        subject: { type: 'string', description: 'Subject for the session' },
        preferred_date: { type: 'string', description: 'Preferred date in ISO 8601' },
        preferred_time: { type: 'string', description: 'Preferred time slot' },
        duration_minutes: { type: 'integer', description: 'Session duration', enum: ['30', '45', '60', '90'] },
        session_type: { type: 'string', description: 'Session format', enum: ['one_on_one', 'group', 'review', 'exam_prep'] },
      },
      required: ['student_id', 'subject', 'preferred_date'],
    },
    output_schema: {
      type: 'object',
      properties: {
        session_id: { type: 'string', description: 'Unique session booking ID' },
        confirmed_datetime: { type: 'string', description: 'Confirmed date and time' },
        tutor_assigned: { type: 'string', description: 'Name of assigned tutor' },
        meeting_link: { type: 'string', description: 'Video call link if online session' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Add to waitlist and confirm when schedule is available',
    error_handling: 'Suggest alternative available time slots if preferred time is taken',
    rate_limit: 15,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  grade_calculator: {
    name: 'grade_calculator',
    description: 'Calculate grades, weighted averages, and GPA based on assignment and exam scores',
    category: 'calculation',
    domains: ['education.tutoring'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/education/grades',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        student_id: { type: 'string', description: 'Student identifier' },
        subject: { type: 'string', description: 'Subject for grade calculation' },
        scores: { type: 'array', description: 'List of score objects with category, weight, and value' },
        grading_scale: { type: 'string', description: 'Grading scale to use', enum: ['letter', 'percentage', 'gpa_4', 'gpa_10'] },
        include_projection: { type: 'boolean', description: 'Project final grade based on current trajectory' },
      },
      required: ['student_id', 'subject', 'scores'],
    },
    output_schema: {
      type: 'object',
      properties: {
        current_grade: { type: 'string', description: 'Current grade in the selected scale' },
        weighted_average: { type: 'number', description: 'Weighted average score' },
        projected_final: { type: 'string', description: 'Projected final grade if requested' },
        needed_for_target: { type: 'object', description: 'Scores needed on remaining work to achieve target grade' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Calculate using simple average if weighted configuration is unavailable',
    error_handling: 'Return partial calculation with note about missing score entries',
    rate_limit: 30,
    version: '1.0.0',
    visibility: 'private',
    mcp_compatible: false,
  },

  learning_path_builder: {
    name: 'learning_path_builder',
    description: 'Build a personalized learning path with sequenced topics, milestones, and time estimates',
    category: 'action',
    domains: ['education.tutoring'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/education/learning-paths',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        student_id: { type: 'string', description: 'Student identifier for personalization' },
        target_topic: { type: 'string', description: 'Ultimate learning goal or topic' },
        current_level: { type: 'string', description: 'Current proficiency level', enum: ['none', 'beginner', 'intermediate', 'advanced'] },
        target_level: { type: 'string', description: 'Target proficiency level', enum: ['beginner', 'intermediate', 'advanced', 'expert'] },
        hours_per_week: { type: 'number', description: 'Available study hours per week' },
        learning_style: { type: 'string', description: 'Preferred learning style', enum: ['visual', 'reading', 'hands_on', 'mixed'] },
      },
      required: ['target_topic', 'current_level', 'target_level'],
    },
    output_schema: {
      type: 'object',
      properties: {
        path_id: { type: 'string', description: 'Learning path identifier' },
        steps: { type: 'array', description: 'Ordered learning steps with topics, resources, and milestones' },
        total_hours: { type: 'number', description: 'Estimated total hours to complete' },
        estimated_weeks: { type: 'number', description: 'Estimated weeks based on available hours' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Generate generic learning path for the topic without personalization',
    error_handling: 'Return template path with note about limited personalization data',
    rate_limit: 10,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },

  quiz_generator: {
    name: 'quiz_generator',
    description: 'Generate quizzes and assessments with automatic grading rubrics and answer keys',
    category: 'action',
    domains: ['education.tutoring'],
    method: 'POST',
    endpoint_url: '/api/v1/tools/education/quizzes',
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        topic: { type: 'string', description: 'Topic for the quiz' },
        question_count: { type: 'integer', description: 'Number of questions to generate' },
        difficulty: { type: 'string', description: 'Difficulty level', enum: ['easy', 'medium', 'hard', 'mixed'] },
        question_types: {
          type: 'array',
          description: 'Types of questions to include',
          enum: ['multiple_choice', 'true_false', 'short_answer', 'essay', 'matching'],
        },
        time_limit_minutes: { type: 'integer', description: 'Time limit for the quiz in minutes' },
        include_explanations: { type: 'boolean', description: 'Include explanations with answer key' },
      },
      required: ['topic', 'question_count'],
    },
    output_schema: {
      type: 'object',
      properties: {
        quiz_id: { type: 'string', description: 'Unique quiz identifier' },
        questions: { type: 'array', description: 'Quiz questions with options' },
        answer_key: { type: 'object', description: 'Answer key with correct responses and explanations' },
        grading_rubric: { type: 'object', description: 'Scoring rubric and point distribution' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Draw questions from pre-built question bank for the topic',
    error_handling: 'Return available questions with note if fewer than requested could be generated',
    rate_limit: 15,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  },
}

// ─── Domain mapping for tool hint resolution ───

const DOMAIN_TOOL_MAP: Record<string, string[]> = {
  'automotive.sales': [
    'inventory_lookup', 'quote_calculator', 'financing_calculator', 'appointment_scheduler',
    'vehicle_comparator', 'trade_in_valuator', 'insurance_quoter', 'document_verifier',
  ],
  'medical.consultation': [
    'medical_history_lookup', 'medication_search', 'lab_results_checker', 'appointment_scheduler',
    'insurance_verifier', 'prescription_generator', 'symptom_analyzer', 'referral_creator',
  ],
  'legal.advisory': [
    'case_law_search', 'statute_lookup', 'deadline_calculator', 'document_drafter',
    'fee_calculator', 'court_filing_tracker', 'client_record_lookup', 'conflict_checker',
  ],
  'finance.advisory': [
    'portfolio_analyzer', 'risk_calculator', 'market_data_fetcher', 'compliance_checker',
    'investment_simulator', 'tax_calculator', 'account_lookup', 'transaction_history',
  ],
  'industrial.support': [
    'equipment_diagnostics', 'parts_inventory', 'maintenance_scheduler', 'manual_lookup',
    'incident_reporter', 'sensor_data_reader', 'calibration_checker', 'safety_validator',
  ],
  'education.tutoring': [
    'curriculum_browser', 'progress_tracker', 'exercise_generator', 'resource_finder',
    'session_scheduler', 'grade_calculator', 'learning_path_builder', 'quiz_generator',
  ],
}

// ─── Helpers ───

function toSnakeCase(str: string): string {
  return str
    .replace(/[^a-zA-Z0-9\s_]/g, '')
    .trim()
    .replace(/\s+/g, '_')
    .toLowerCase()
}

function resolveToolHintToName(hint: string, domain: string): string | null {
  // Direct match in TOOL_PATTERNS
  if (TOOL_PATTERNS[hint]) return hint

  // Check domain-specific tools for partial matches
  const domainTools = DOMAIN_TOOL_MAP[domain] ?? []
  const match = domainTools.find((t) => t.includes(hint) || hint.includes(t))

  if (match) return match

  // Fuzzy match: check if any known tool contains the hint keyword
  const allToolNames = Object.keys(TOOL_PATTERNS)

  const fuzzy = allToolNames.find((name) => {
    const keywords = name.split('_')

    return keywords.some((kw) => hint.includes(kw) && kw.length > 3)
  })

  return fuzzy ?? null
}

function buildToolFromExplicitName(name: string, domain: string): ScannedTool {
  const snakeName = toSnakeCase(name)

  // Check if we have a template for this tool
  const template = TOOL_PATTERNS[snakeName]

  if (template) {
    // Ensure domain is included
    const domains = template.domains.includes(domain) ? template.domains : [...template.domains, domain]

    return { ...template, domains }
  }

  // Generate a reasonable default tool definition
  return {
    name: snakeName,
    description: `Execute the ${name} operation for the ${domain} domain`,
    category: 'query',
    domains: [domain],
    method: 'POST',
    endpoint_url: `/api/v1/tools/${domain.split('.')[0]}/${snakeName.replace(/_/g, '-')}`,
    auth_type: 'bearer',
    input_schema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Input query or parameters for the operation' },
        context: { type: 'object', description: 'Additional context for the operation' },
      },
      required: ['query'],
    },
    output_schema: {
      type: 'object',
      properties: {
        result: { type: 'object', description: 'Operation result data' },
        status: { type: 'string', description: 'Operation status' },
      },
    },
    execution_mode: 'simulated',
    fallback_strategy: 'Return a descriptive error message and suggest manual alternatives',
    error_handling: 'Log the error and return a structured error response to the caller',
    rate_limit: 30,
    version: '1.0.0',
    visibility: 'organization',
    mcp_compatible: true,
  }
}

function extractToolsFromTurn(turn: ConversationTurn, domain: string): ScannedTool[] {
  const tools: ScannedTool[] = []
  const seen = new Set<string>()

  // 1. Explicit herramientas_usadas
  if (turn.herramientas_usadas?.length) {
    for (const toolName of turn.herramientas_usadas) {
      const snakeName = toSnakeCase(toolName)

      if (!seen.has(snakeName)) {
        seen.add(snakeName)
        tools.push(buildToolFromExplicitName(toolName, domain))
      }
    }
  }

  // 2. tool_calls with structured data
  if (turn.tool_calls?.length) {
    for (const tc of turn.tool_calls) {
      const snakeName = toSnakeCase(tc.tool_name)

      if (!seen.has(snakeName)) {
        seen.add(snakeName)
        const base = buildToolFromExplicitName(tc.tool_name, domain)


        // Enrich input schema from actual arguments
        if (tc.arguments && typeof tc.arguments === 'object') {
          const enrichedProperties: Record<string, { type: string; description: string }> = {}

          for (const [key, value] of Object.entries(tc.arguments)) {
            const valueType = Array.isArray(value) ? 'array' : typeof value

            enrichedProperties[key] = {
              type: valueType === 'object' ? 'object' : valueType,
              description: `Parameter ${key} for ${tc.tool_name}`,
            }
          }

          base.input_schema = {
            type: 'object',
            properties: { ...base.input_schema.properties, ...enrichedProperties },
            required: [...new Set([...base.input_schema.required, ...Object.keys(tc.arguments)])],
          }
        }

        tools.push(base)
      }
    }
  }

  // 3. tool_results — capture output schema info
  if (turn.tool_results?.length) {
    for (const tr of turn.tool_results) {
      const snakeName = toSnakeCase(tr.tool_name)

      if (!seen.has(snakeName)) {
        seen.add(snakeName)
        const base = buildToolFromExplicitName(tr.tool_name, domain)


        // Enrich output schema from actual results
        if (tr.result && typeof tr.result === 'object' && !Array.isArray(tr.result)) {
          const enrichedOutput: Record<string, { type: string; description: string }> = {}

          for (const [key, value] of Object.entries(tr.result)) {
            const valueType = Array.isArray(value) ? 'array' : typeof value

            enrichedOutput[key] = {
              type: valueType === 'object' ? 'object' : valueType,
              description: `Output field ${key} from ${tr.tool_name}`,
            }
          }

          base.output_schema = {
            type: 'object',
            properties: { ...base.output_schema.properties, ...enrichedOutput },
          }
        }

        tools.push(base)
      }
    }
  }

  // 4. Content pattern matching — only for assistant turns
  if (turn.rol === 'asistente' || turn.rol === 'assistant' || turn.rol === 'agente') {
    for (const { pattern, tool_hint } of CONTENT_HINT_PATTERNS) {
      if (pattern.test(turn.contenido)) {
        const resolvedName = resolveToolHintToName(tool_hint, domain)

        if (resolvedName && !seen.has(resolvedName)) {
          seen.add(resolvedName)
          tools.push(buildToolFromExplicitName(resolvedName, domain))
        }
      }
    }
  }

  return tools
}

function computeConfidence(
  turnCount: number,
  explicitToolCount: number,
  patternMatchCount: number,
  hasToolCalls: boolean,
): number {
  let confidence = 0

  // Explicit tools in herramientas_usadas or tool_calls are high confidence
  if (hasToolCalls) confidence += 0.5
  if (explicitToolCount > 0) confidence += 0.3

  // Pattern matches add moderate confidence
  confidence += Math.min(patternMatchCount * 0.1, 0.3)

  // More turns generally means more data, slight boost
  if (turnCount > 4) confidence += 0.05
  if (turnCount > 8) confidence += 0.05

  return Math.min(confidence, 1.0)
}

function buildReasoning(
  explicitTools: string[],
  patternTools: string[],
  hasToolCalls: boolean,
): string {
  const parts: string[] = []

  if (hasToolCalls) {
    parts.push('Conversation contains structured tool_calls/tool_results')
  }

  if (explicitTools.length > 0) {
    parts.push(`Explicit tools declared in herramientas_usadas: ${explicitTools.join(', ')}`)
  }

  if (patternTools.length > 0) {
    parts.push(`Content patterns suggest usage of: ${patternTools.join(', ')}`)
  }

  if (parts.length === 0) {
    return 'No tool usage indicators found in conversation content or metadata'
  }

  return parts.join('. ') + '.'
}

// ─── Main Functions ───

/**
 * Scan an array of conversations to identify what tools are needed.
 * Uses pattern-matching heuristics in demo mode (no API call).
 * Returns a ToolScanResult per conversation.
 */
export async function scanConversationsForTools(conversations: Conversation[]): Promise<ToolScanResult[]> {
  const results: ToolScanResult[] = []

  for (const conversation of conversations) {
    const allTools: ScannedTool[] = []
    const seenNames = new Set<string>()
    const explicitToolNames: string[] = []
    const patternToolNames: string[] = []
    let hasToolCalls = false

    for (const turn of conversation.turnos) {
      // Track whether structured tool calls exist
      if (turn.tool_calls?.length || turn.tool_results?.length) {
        hasToolCalls = true
      }

      const turnTools = extractToolsFromTurn(turn, conversation.dominio)

      for (const tool of turnTools) {
        if (!seenNames.has(tool.name)) {
          seenNames.add(tool.name)
          allTools.push(tool)

          // Classify source for reasoning
          const wasExplicit =
            turn.herramientas_usadas?.some((h) => toSnakeCase(h) === tool.name) ||
            turn.tool_calls?.some((tc) => toSnakeCase(tc.tool_name) === tool.name) ||
            turn.tool_results?.some((tr) => toSnakeCase(tr.tool_name) === tool.name)

          if (wasExplicit) {
            explicitToolNames.push(tool.name)
          } else {
            patternToolNames.push(tool.name)
          }
        }
      }
    }

    const confidence = computeConfidence(
      conversation.turnos.length,
      explicitToolNames.length,
      patternToolNames.length,
      hasToolCalls,
    )

    results.push({
      conversation_id: conversation.conversation_id,
      requires_tools: allTools.length > 0,
      reasoning: buildReasoning(explicitToolNames, patternToolNames, hasToolCalls),
      identified_tools: allTools,
      confidence,
    })
  }

  return results
}

/**
 * Extract and flatten all unique ScannedTools from an array of scan results.
 * Automatically deduplicates by tool name.
 */
export function generateToolsFromScan(scanResults: ToolScanResult[]): ScannedTool[] {
  const toolMap = new Map<string, ScannedTool>()

  for (const result of scanResults) {
    for (const tool of result.identified_tools) {
      if (!toolMap.has(tool.name)) {
        toolMap.set(tool.name, { ...tool })
      } else {
        // Merge domains
        const existing = toolMap.get(tool.name)!
        const mergedDomains = [...new Set([...existing.domains, ...tool.domains])]

        toolMap.set(tool.name, { ...existing, domains: mergedDomains })
      }
    }
  }

  return Array.from(toolMap.values())
}

/**
 * Deduplicate tools by name, merging their schemas (union of properties)
 * and combining domain lists. When two tools share a name, the first
 * occurrence provides the base and subsequent occurrences contribute
 * additional properties and domains.
 */
export function deduplicateTools(tools: ScannedTool[]): ScannedTool[] {
  const toolMap = new Map<string, ScannedTool>()

  for (const tool of tools) {
    const existing = toolMap.get(tool.name)

    if (!existing) {
      // Deep clone to avoid mutation
      toolMap.set(tool.name, {
        ...tool,
        domains: [...tool.domains],
        input_schema: {
          type: 'object',
          properties: { ...tool.input_schema.properties },
          required: [...tool.input_schema.required],
        },
        output_schema: {
          type: 'object',
          properties: { ...tool.output_schema.properties },
        },
      })
      continue
    }

    // Merge domains (union)
    const mergedDomains = [...new Set([...existing.domains, ...tool.domains])]

    // Merge input schema properties (union)
    const mergedInputProps = { ...existing.input_schema.properties }

    for (const [key, value] of Object.entries(tool.input_schema.properties)) {
      if (!mergedInputProps[key]) {
        mergedInputProps[key] = value
      }
    }

    const mergedRequired = [...new Set([...existing.input_schema.required, ...tool.input_schema.required])]

    // Merge output schema properties (union)
    const mergedOutputProps = { ...existing.output_schema.properties }

    for (const [key, value] of Object.entries(tool.output_schema.properties)) {
      if (!mergedOutputProps[key]) {
        mergedOutputProps[key] = value
      }
    }

    toolMap.set(tool.name, {
      ...existing,
      domains: mergedDomains,
      input_schema: {
        type: 'object',
        properties: mergedInputProps,
        required: mergedRequired,
      },
      output_schema: {
        type: 'object',
        properties: mergedOutputProps,
      },
    })
  }

  return Array.from(toolMap.values())
}
