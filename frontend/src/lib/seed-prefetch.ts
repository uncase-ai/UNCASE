// ─── Seed Creation Prefetch Data ───
// Modular catalog of roles, conversation flow templates, restrictions,
// tags, and objectives for rapid seed creation across all domains.

// ─── Role Catalog ───

export interface RolePreset {
  id: string
  label: string
  description: string

  /** Domains where this role is most relevant. Empty = universal. */
  domains: string[]

  /** Category for grouping in search results */
  category: 'customer' | 'professional' | 'support' | 'specialist' | 'authority' | 'other'
}

export const ROLE_CATALOG: RolePreset[] = [
  // ── Universal / Cross-domain ──
  { id: 'client', label: 'Client', description: 'Individual or business seeking professional services or advice', domains: [], category: 'customer' },
  { id: 'customer', label: 'Customer', description: 'End consumer interested in purchasing products or services', domains: [], category: 'customer' },
  { id: 'user', label: 'User', description: 'General end-user interacting with a system or service', domains: [], category: 'customer' },
  { id: 'assistant', label: 'Assistant', description: 'AI or human assistant providing help and information', domains: [], category: 'support' },
  { id: 'support_agent', label: 'Support Agent', description: 'Customer support representative handling inquiries and resolving issues', domains: [], category: 'support' },
  { id: 'supervisor', label: 'Supervisor', description: 'Manager or supervisor overseeing operations and approving decisions', domains: [], category: 'authority' },
  { id: 'receptionist', label: 'Receptionist', description: 'Front desk staff handling scheduling, intake, and routing', domains: [], category: 'support' },

  // ── Automotive ──
  { id: 'cliente', label: 'Cliente', description: 'Cliente interesado en adquirir un vehículo nuevo o seminuevo', domains: ['automotive.sales'], category: 'customer' },
  { id: 'asesor_ventas', label: 'Asesor de Ventas', description: 'Asesor de ventas certificado con acceso a inventario y opciones de financiamiento', domains: ['automotive.sales'], category: 'professional' },
  { id: 'asesor_financiero', label: 'Asesor Financiero', description: 'Especialista en crédito automotriz con acceso a simuladores de crédito y tasas', domains: ['automotive.sales'], category: 'specialist' },
  { id: 'valuador', label: 'Valuador', description: 'Valuador certificado con acceso a bases de datos de precios de mercado para trade-in', domains: ['automotive.sales'], category: 'specialist' },
  { id: 'coordinador_pruebas', label: 'Coordinador de Pruebas', description: 'Coordinador de pruebas de manejo con acceso a agenda y disponibilidad de unidades', domains: ['automotive.sales'], category: 'support' },
  { id: 'asesor_servicio', label: 'Asesor de Servicio', description: 'Asesor de servicio post-venta con acceso al sistema de citas y historial de mantenimiento', domains: ['automotive.sales'], category: 'professional' },

  // ── Medical ──
  { id: 'patient', label: 'Patient', description: 'Patient seeking medical evaluation, treatment, or health guidance', domains: ['medical.consultation'], category: 'customer' },
  { id: 'physician', label: 'Physician', description: 'Board-certified physician with access to patient records and diagnostic tools', domains: ['medical.consultation'], category: 'professional' },
  { id: 'nurse', label: 'Nurse', description: 'Registered nurse providing clinical support, triage, and patient education', domains: ['medical.consultation'], category: 'professional' },
  { id: 'therapist', label: 'Therapist', description: 'Licensed therapist or counselor conducting mental health assessments and treatment', domains: ['medical.consultation'], category: 'specialist' },
  { id: 'pharmacist', label: 'Pharmacist', description: 'Licensed pharmacist providing medication counseling and interaction checks', domains: ['medical.consultation'], category: 'specialist' },
  { id: 'specialist_doctor', label: 'Specialist Doctor', description: 'Sub-specialist physician (cardiologist, dermatologist, etc.) with advanced diagnostic capabilities', domains: ['medical.consultation'], category: 'specialist' },
  { id: 'caregiver', label: 'Caregiver / Guardian', description: 'Family member or legal guardian making decisions on behalf of a patient', domains: ['medical.consultation'], category: 'customer' },

  // ── Legal ──
  { id: 'attorney', label: 'Attorney', description: 'Licensed attorney with expertise in the relevant area of law', domains: ['legal.advisory'], category: 'professional' },
  { id: 'abogado_laboral', label: 'Abogado Laboral', description: 'Abogado especialista en derecho laboral con acceso a legislación y jurisprudencia', domains: ['legal.advisory'], category: 'specialist' },
  { id: 'paralegal', label: 'Paralegal', description: 'Legal assistant managing documentation, research, and case file preparation', domains: ['legal.advisory'], category: 'support' },
  { id: 'mediator', label: 'Mediator', description: 'Neutral mediator facilitating dispute resolution between parties', domains: ['legal.advisory'], category: 'authority' },
  { id: 'notary', label: 'Notary', description: 'Public notary authenticating documents and certifying legal proceedings', domains: ['legal.advisory'], category: 'authority' },
  { id: 'victim', label: 'Victim / Complainant', description: 'Individual who has suffered harm and is seeking legal recourse', domains: ['legal.advisory'], category: 'customer' },
  { id: 'defendant', label: 'Defendant', description: 'Individual or entity responding to legal claims or charges', domains: ['legal.advisory'], category: 'customer' },

  // ── Finance ──
  { id: 'financial_advisor', label: 'Financial Advisor', description: 'Certified financial advisor with access to market data and portfolio tools', domains: ['finance.advisory'], category: 'professional' },
  { id: 'asesor_hipotecario', label: 'Asesor Hipotecario', description: 'Asesor hipotecario certificado con acceso a simuladores de crédito', domains: ['finance.advisory'], category: 'specialist' },
  { id: 'bank_teller', label: 'Bank Teller', description: 'Bank representative handling account operations and basic financial services', domains: ['finance.advisory'], category: 'support' },
  { id: 'risk_analyst', label: 'Risk Analyst', description: 'Risk assessment specialist evaluating credit, investment, or insurance risk', domains: ['finance.advisory'], category: 'specialist' },
  { id: 'compliance_officer', label: 'Compliance Officer', description: 'Regulatory compliance specialist ensuring adherence to financial regulations', domains: ['finance.advisory'], category: 'authority' },
  { id: 'investor', label: 'Investor', description: 'Individual or institutional investor managing assets and portfolio allocation', domains: ['finance.advisory'], category: 'customer' },

  // ── Industrial ──
  { id: 'operator', label: 'Operator', description: 'Plant operator running machinery and reporting equipment issues', domains: ['industrial.support'], category: 'customer' },
  { id: 'technician', label: 'Technician', description: 'Certified maintenance technician with access to diagnostic systems and manuals', domains: ['industrial.support'], category: 'professional' },
  { id: 'supervisor_planta', label: 'Supervisor de Planta', description: 'Supervisor de planta coordinando producción y mantenimiento', domains: ['industrial.support'], category: 'authority' },
  { id: 'coordinador_mantenimiento', label: 'Coordinador de Mantenimiento', description: 'Coordinador de mantenimiento con acceso al sistema CMMS y calendario de intervenciones', domains: ['industrial.support'], category: 'professional' },
  { id: 'safety_officer', label: 'Safety Officer', description: 'Occupational health and safety specialist enforcing safety protocols', domains: ['industrial.support'], category: 'authority' },
  { id: 'quality_inspector', label: 'Quality Inspector', description: 'Quality assurance inspector verifying product specifications and standards', domains: ['industrial.support'], category: 'specialist' },

  // ── Education ──
  { id: 'student', label: 'Student', description: 'Student seeking help understanding a specific topic or solving problems', domains: ['education.tutoring'], category: 'customer' },
  { id: 'estudiante', label: 'Estudiante', description: 'Estudiante buscando ayuda para entender un tema o resolver ejercicios', domains: ['education.tutoring'], category: 'customer' },
  { id: 'tutor', label: 'Tutor', description: 'Qualified tutor with expertise in the subject area and adaptive teaching methods', domains: ['education.tutoring'], category: 'professional' },
  { id: 'instructor', label: 'Instructor', description: 'Course instructor providing structured lessons and assessments', domains: ['education.tutoring'], category: 'professional' },
  { id: 'parent', label: 'Parent / Guardian', description: 'Parent or guardian involved in the student\'s learning process', domains: ['education.tutoring'], category: 'customer' },
  { id: 'academic_advisor', label: 'Academic Advisor', description: 'Academic advisor guiding course selection and academic planning', domains: ['education.tutoring'], category: 'specialist' },
]

/** Search roles by query string — matches id, label, description. Domain-relevant first. */
export function searchRoles(query: string, domain?: string): RolePreset[] {
  const q = query.toLowerCase().trim()

  if (!q) {
    // No query: show domain-specific first, then universal
    const domainRoles = domain
      ? ROLE_CATALOG.filter(r => r.domains.includes(domain) || r.domains.length === 0)
      : ROLE_CATALOG

    return domainRoles.slice(0, 20)
  }

  const scored = ROLE_CATALOG.map(role => {
    let score = 0
    const labelLower = role.label.toLowerCase()
    const descLower = role.description.toLowerCase()
    const idLower = role.id.toLowerCase()

    if (labelLower === q) score += 100
    else if (labelLower.startsWith(q)) score += 80
    else if (idLower.startsWith(q)) score += 70
    else if (labelLower.includes(q)) score += 50
    else if (descLower.includes(q)) score += 30
    else if (idLower.includes(q)) score += 20
    else return { role, score: 0 }

    // Boost domain-relevant roles
    if (domain && role.domains.includes(domain)) score += 25
    if (role.domains.length === 0) score += 5 // universal is mildly boosted

    return { role, score }
  })

  return scored
    .filter(s => s.score > 0)
    .sort((a, b) => b.score - a.score)
    .map(s => s.role)
    .slice(0, 15)
}

// ─── Conversation Flow Templates ───

export interface FlowTemplate {
  id: string
  label: string
  description: string
  steps: string[]
  domains: string[]

  /** Suggested turn range */
  turnRange: [number, number]
}

export const FLOW_TEMPLATES: FlowTemplate[] = [
  // ── Universal ──
  {
    id: 'general_inquiry',
    label: 'General Inquiry',
    description: 'Standard question-and-answer exchange',
    steps: ['Greeting and inquiry', 'Clarifying questions', 'Detailed response', 'Follow-up questions', 'Summary and next steps'],
    domains: [],
    turnRange: [4, 8]
  },
  {
    id: 'complaint_resolution',
    label: 'Complaint Resolution',
    description: 'Handle a customer complaint from intake to resolution',
    steps: ['Complaint intake and acknowledgment', 'Issue investigation and details', 'Root cause identification', 'Resolution proposal', 'Confirmation and follow-up'],
    domains: [],
    turnRange: [5, 10]
  },
  {
    id: 'onboarding',
    label: 'Onboarding / Intake',
    description: 'Guide a new user through initial setup or registration',
    steps: ['Welcome and purpose explanation', 'Information collection', 'Verification and validation', 'Options and preferences setup', 'Confirmation and next steps'],
    domains: [],
    turnRange: [4, 8]
  },
  {
    id: 'consultation',
    label: 'Professional Consultation',
    description: 'Structured professional advice session',
    steps: ['Needs assessment', 'Situation analysis', 'Options presentation', 'Recommendation and rationale', 'Action plan and follow-up'],
    domains: [],
    turnRange: [5, 10]
  },
  {
    id: 'escalation',
    label: 'Escalation Flow',
    description: 'Handle an issue that requires escalation to a higher authority',
    steps: ['Initial issue report', 'First-level troubleshooting', 'Escalation decision and handoff', 'Specialist assessment', 'Resolution and documentation'],
    domains: [],
    turnRange: [5, 8]
  },

  // ── Automotive ──
  {
    id: 'auto_sales_new',
    label: 'New Vehicle Sale',
    description: 'Full sales cycle for a new vehicle',
    steps: ['Saludo y detección de necesidad', 'Presentación de opciones disponibles', 'Comparativa de modelos y características', 'Cotización y opciones de financiamiento', 'Siguiente paso (prueba de manejo o cierre)'],
    domains: ['automotive.sales'],
    turnRange: [4, 8]
  },
  {
    id: 'auto_test_drive',
    label: 'Test Drive Scheduling',
    description: 'Coordinate a test drive appointment',
    steps: ['Confirmación de interés en modelo', 'Verificación de disponibilidad', 'Selección de fecha y hora', 'Documentos requeridos', 'Confirmación de cita'],
    domains: ['automotive.sales'],
    turnRange: [4, 6]
  },
  {
    id: 'auto_trade_in',
    label: 'Trade-In Evaluation',
    description: 'Evaluate a vehicle for trade-in',
    steps: ['Datos del vehículo actual', 'Verificación de condición', 'Estimación de valor de mercado', 'Propuesta de trade-in', 'Siguiente paso'],
    domains: ['automotive.sales'],
    turnRange: [5, 8]
  },
  {
    id: 'auto_financing',
    label: 'Financing Consultation',
    description: 'Evaluate and present financing options',
    steps: ['Exploración de necesidades financieras', 'Datos para pre-aprobación', 'Simulación de crédito', 'Comparativa de planes', 'Documentos requeridos'],
    domains: ['automotive.sales'],
    turnRange: [5, 8]
  },

  // ── Medical ──
  {
    id: 'med_initial',
    label: 'Initial Consultation',
    description: 'First visit with history, exam, and plan',
    steps: ['Chief complaint and HPI', 'Review of medical history and medications', 'Risk factor assessment', 'Physical examination findings', 'Diagnostic plan and orders', 'Patient education and follow-up'],
    domains: ['medical.consultation'],
    turnRange: [6, 10]
  },
  {
    id: 'med_followup',
    label: 'Follow-Up Visit',
    description: 'Treatment response review and adjustment',
    steps: ['Treatment response assessment', 'Symptom progression review', 'Medication adherence check', 'Lab results review', 'Treatment plan adjustment', 'Follow-up scheduling'],
    domains: ['medical.consultation'],
    turnRange: [5, 8]
  },
  {
    id: 'med_mental_health',
    label: 'Mental Health Intake',
    description: 'Comprehensive mental health assessment',
    steps: ['Presenting concerns and symptom onset', 'Symptom inventory and severity', 'Psychosocial and family history', 'Current coping and support system', 'Safety screening', 'Treatment recommendations'],
    domains: ['medical.consultation'],
    turnRange: [6, 10]
  },
  {
    id: 'med_triage',
    label: 'Triage & Urgency Assessment',
    description: 'Rapid assessment to determine care priority',
    steps: ['Symptom report', 'Vital signs and severity assessment', 'Red flag screening', 'Care level recommendation', 'Routing or scheduling'],
    domains: ['medical.consultation'],
    turnRange: [4, 6]
  },

  // ── Legal ──
  {
    id: 'legal_case_intake',
    label: 'Case Intake',
    description: 'Initial client consultation and case assessment',
    steps: ['Case intake and factual background', 'Evidence and documentation review', 'Legal analysis and merit assessment', 'Strategy options and recommendations', 'Timeline, costs, and engagement terms'],
    domains: ['legal.advisory'],
    turnRange: [5, 8]
  },
  {
    id: 'legal_labor',
    label: 'Labor Dispute',
    description: 'Worker consultation about employment rights',
    steps: ['Relato de hechos y circunstancias', 'Revisión de contrato y antigüedad', 'Determinación del tipo de situación', 'Cálculo de derechos e indemnización', 'Opciones legales y próximos pasos'],
    domains: ['legal.advisory'],
    turnRange: [5, 8]
  },

  // ── Finance ──
  {
    id: 'fin_portfolio_review',
    label: 'Portfolio Review',
    description: 'Investment portfolio analysis and rebalancing',
    steps: ['Current portfolio review', 'Risk tolerance reassessment', 'Market outlook and analysis', 'Rebalancing recommendations', 'Implementation plan'],
    domains: ['finance.advisory'],
    turnRange: [5, 8]
  },
  {
    id: 'fin_mortgage',
    label: 'Mortgage Consultation',
    description: 'Home loan evaluation and pre-approval',
    steps: ['Detección de necesidad y perfil', 'Evaluación de capacidad de pago', 'Comparativa de productos', 'Simulación personalizada', 'Documentos para pre-aprobación'],
    domains: ['finance.advisory'],
    turnRange: [5, 8]
  },

  // ── Industrial ──
  {
    id: 'ind_error_diagnosis',
    label: 'Equipment Error Diagnosis',
    description: 'Remote troubleshooting of machine error',
    steps: ['Error code report and machine status', 'Safety verification', 'Remote diagnostic data review', 'Guided troubleshooting steps', 'Resolution or dispatch decision'],
    domains: ['industrial.support'],
    turnRange: [5, 8]
  },
  {
    id: 'ind_preventive_maint',
    label: 'Preventive Maintenance',
    description: 'Schedule and coordinate preventive maintenance',
    steps: ['Equipos y programa de mantenimiento', 'Historial y últimas intervenciones', 'Coordinación de ventana de paro', 'Asignación de técnicos y refacciones', 'Confirmación y notificaciones'],
    domains: ['industrial.support'],
    turnRange: [4, 7]
  },

  // ── Education ──
  {
    id: 'edu_concept_tutorial',
    label: 'Concept Tutorial',
    description: 'Step-by-step explanation of a topic',
    steps: ['Topic identification and prior knowledge check', 'Concept explanation with examples', 'Guided practice with scaffolding', 'Independent problem solving', 'Summary and next study steps'],
    domains: ['education.tutoring'],
    turnRange: [5, 8]
  },
  {
    id: 'edu_exam_prep',
    label: 'Exam Preparation',
    description: 'Focused review session for upcoming exam',
    steps: ['Topic and exam format review', 'Key concepts recap', 'Practice problems walkthrough', 'Common mistakes and tips', 'Study plan and resources'],
    domains: ['education.tutoring'],
    turnRange: [5, 8]
  },
  {
    id: 'edu_homework_help',
    label: 'Homework Help',
    description: 'Guide student through specific assignment',
    steps: ['Problem identification', 'Relevant concept review', 'Step-by-step guided solution', 'Verification and explanation', 'Related practice suggestions'],
    domains: ['education.tutoring'],
    turnRange: [4, 7]
  },
]

/** Search flow templates. Domain-relevant first. */
export function searchFlows(query: string, domain?: string): FlowTemplate[] {
  const q = query.toLowerCase().trim()

  const relevant = domain
    ? FLOW_TEMPLATES.filter(f => f.domains.includes(domain) || f.domains.length === 0)
    : FLOW_TEMPLATES

  if (!q) return relevant.slice(0, 15)

  return relevant
    .map(f => {
      let score = 0

      if (f.label.toLowerCase().includes(q)) score += 50
      if (f.description.toLowerCase().includes(q)) score += 30
      if (f.steps.some(s => s.toLowerCase().includes(q))) score += 20
      if (domain && f.domains.includes(domain)) score += 25

      return { flow: f, score }
    })
    .filter(s => s.score > 0)
    .sort((a, b) => b.score - a.score)
    .map(s => s.flow)
    .slice(0, 15)
}

// ─── Restriction Presets ───

export interface RestrictionPreset {
  id: string
  text: string
  domains: string[]
  category: 'compliance' | 'safety' | 'privacy' | 'quality' | 'boundary' | 'operational'
}

export const RESTRICTION_CATALOG: RestrictionPreset[] = [
  // Universal
  { id: 'no_pii', text: 'Never collect, store, or repeat personal identifying information', domains: [], category: 'privacy' },
  { id: 'no_guarantees', text: 'Cannot guarantee specific outcomes or results', domains: [], category: 'boundary' },
  { id: 'stay_scope', text: 'Stay within the defined area of expertise — do not advise on unrelated topics', domains: [], category: 'boundary' },
  { id: 'escalate_emergency', text: 'Emergency situations require immediate escalation to appropriate authorities', domains: [], category: 'safety' },
  { id: 'verify_identity', text: 'Verify user identity or credentials before sharing sensitive information', domains: [], category: 'privacy' },
  { id: 'log_interactions', text: 'All interactions must be logged and traceable for audit purposes', domains: [], category: 'compliance' },

  // Automotive
  { id: 'auto_inventory', text: 'Solo mencionar vehículos del inventario actual', domains: ['automotive.sales'], category: 'operational' },
  { id: 'auto_iva', text: 'Precios deben incluir IVA', domains: ['automotive.sales'], category: 'compliance' },
  { id: 'auto_discount', text: 'No prometer descuentos sin autorización del gerente', domains: ['automotive.sales'], category: 'boundary' },
  { id: 'auto_license', text: 'Requiere licencia de conducir vigente para prueba de manejo', domains: ['automotive.sales'], category: 'operational' },

  // Medical
  { id: 'med_history', text: 'Must review complete medical history before making recommendations', domains: ['medical.consultation'], category: 'safety' },
  { id: 'med_allergy', text: 'All medication changes require allergy verification', domains: ['medical.consultation'], category: 'safety' },
  { id: 'med_emergency', text: 'Emergency symptoms require immediate escalation protocol', domains: ['medical.consultation'], category: 'safety' },
  { id: 'med_hipaa', text: 'All patient information must be handled in compliance with HIPAA regulations', domains: ['medical.consultation'], category: 'compliance' },
  { id: 'med_no_diagnosis', text: 'Cannot provide definitive diagnosis without proper examination and testing', domains: ['medical.consultation'], category: 'boundary' },

  // Legal
  { id: 'legal_no_outcome', text: 'Cannot guarantee specific litigation outcomes', domains: ['legal.advisory'], category: 'boundary' },
  { id: 'legal_privilege', text: 'Attorney-client privilege must be established before disclosure', domains: ['legal.advisory'], category: 'privacy' },
  { id: 'legal_conflict', text: 'Conflict of interest check required before engagement', domains: ['legal.advisory'], category: 'compliance' },
  { id: 'legal_fees', text: 'Fee structure must be disclosed upfront', domains: ['legal.advisory'], category: 'compliance' },
  { id: 'legal_statute', text: 'Statute of limitations must be verified before proceeding', domains: ['legal.advisory'], category: 'operational' },

  // Finance
  { id: 'fin_past_perf', text: 'Past performance does not guarantee future results', domains: ['finance.advisory'], category: 'compliance' },
  { id: 'fin_fees', text: 'Must disclose all fees and commissions', domains: ['finance.advisory'], category: 'compliance' },
  { id: 'fin_risk', text: 'Recommendations must align with client risk profile', domains: ['finance.advisory'], category: 'quality' },
  { id: 'fin_regulatory', text: 'Regulatory compliance (SOX/FINRA) required for all advice', domains: ['finance.advisory'], category: 'compliance' },
  { id: 'fin_no_insider', text: 'Must not use or share insider or non-public information', domains: ['finance.advisory'], category: 'privacy' },

  // Industrial
  { id: 'ind_safety', text: 'Safety protocols must be followed at all times', domains: ['industrial.support'], category: 'safety' },
  { id: 'ind_lockout', text: 'Equipment lockout/tagout required before physical intervention', domains: ['industrial.support'], category: 'safety' },
  { id: 'ind_certified', text: 'Only certified personnel may perform electrical or high-risk work', domains: ['industrial.support'], category: 'safety' },
  { id: 'ind_log', text: 'All incidents must be logged in maintenance system (CMMS)', domains: ['industrial.support'], category: 'compliance' },

  // Education
  { id: 'edu_no_answers', text: 'Do not provide direct answers — guide through problem-solving process', domains: ['education.tutoring'], category: 'quality' },
  { id: 'edu_adapt', text: 'Adapt difficulty level to student comprehension', domains: ['education.tutoring'], category: 'quality' },
  { id: 'edu_age', text: 'Use age-appropriate language and examples', domains: ['education.tutoring'], category: 'quality' },
  { id: 'edu_encourage', text: 'Use positive reinforcement for effort, not just correct answers', domains: ['education.tutoring'], category: 'quality' },
]

export function getRestrictions(domain?: string): RestrictionPreset[] {
  if (!domain) return RESTRICTION_CATALOG.filter(r => r.domains.length === 0)

  return RESTRICTION_CATALOG.filter(r => r.domains.includes(domain) || r.domains.length === 0)
}

// ─── Tag Suggestions ───

export const TAG_SUGGESTIONS: Record<string, string[]> = {
  'automotive.sales': ['vehiculo-nuevo', 'seminuevo', 'suv', 'sedan', 'financiamiento', 'trade-in', 'prueba-manejo', 'postventa', 'mantenimiento', 'refacciones', 'seguro', 'flota', 'leasing'],
  'medical.consultation': ['initial-consultation', 'follow-up', 'emergency', 'chronic-condition', 'pediatrics', 'cardiology', 'dermatology', 'mental-health', 'immunization', 'telemedicine', 'prescription', 'lab-results'],
  'legal.advisory': ['contract', 'litigation', 'labor-law', 'corporate', 'family-law', 'criminal', 'immigration', 'real-estate', 'intellectual-property', 'compliance', 'mediation', 'due-diligence'],
  'finance.advisory': ['retirement', 'portfolio', 'mortgage', 'credit', 'insurance', 'tax-planning', 'estate-planning', 'budgeting', 'wealth-management', 'risk-assessment', 'cryptocurrency', 'bonds'],
  'industrial.support': ['error-code', 'preventive-maintenance', 'corrective-maintenance', 'safety-incident', 'calibration', 'spare-parts', 'downtime', 'quality-control', 'training', 'commissioning'],
  'education.tutoring': ['mathematics', 'science', 'language', 'history', 'programming', 'exam-prep', 'homework', 'essay-writing', 'reading-comprehension', 'study-skills', 'advanced-placement', 'remedial'],
  _universal: ['high-priority', 'edge-case', 'multilingual', 'complex-scenario', 'multi-turn', 'tool-calling', 'escalation', 'compliance-critical'],
}

export function getTagSuggestions(domain?: string, existing?: string[]): string[] {
  const domainTags = domain ? TAG_SUGGESTIONS[domain] ?? [] : []
  const universalTags = TAG_SUGGESTIONS._universal
  const all = [...domainTags, ...universalTags]
  const usedSet = new Set(existing ?? [])

  return all.filter(t => !usedSet.has(t))
}

// ─── Objective Templates ───

export interface ObjectiveTemplate {
  id: string
  text: string
  domain: string
}

export const OBJECTIVE_TEMPLATES: ObjectiveTemplate[] = [
  // Automotive
  { id: 'auto_1', text: 'Guide the customer through exploring available vehicle options, presenting features and price ranges', domain: 'automotive.sales' },
  { id: 'auto_2', text: 'Schedule a test drive, confirm availability, required documents, and time slot', domain: 'automotive.sales' },
  { id: 'auto_3', text: 'Evaluate the customer\'s current vehicle for trade-in, provide market value estimate, and explain the process', domain: 'automotive.sales' },
  { id: 'auto_4', text: 'Assess the customer\'s credit profile and present personalized financing options', domain: 'automotive.sales' },
  { id: 'auto_5', text: 'Schedule preventive maintenance, inform about service packages and estimated costs', domain: 'automotive.sales' },

  // Medical
  { id: 'med_1', text: 'Conduct thorough initial evaluation including history, risk assessment, and diagnostic workup', domain: 'medical.consultation' },
  { id: 'med_2', text: 'Evaluate treatment response, adjust therapy as needed, and plan ongoing management', domain: 'medical.consultation' },
  { id: 'med_3', text: 'Complete comprehensive mental health intake assessment including risk evaluation and treatment planning', domain: 'medical.consultation' },
  { id: 'med_4', text: 'Review immunization schedule, assess growth milestones, and provide anticipatory guidance', domain: 'medical.consultation' },
  { id: 'med_5', text: 'Triage patient symptoms, determine urgency level, and route to appropriate care', domain: 'medical.consultation' },

  // Legal
  { id: 'leg_1', text: 'Assess the merits of a contract dispute, review evidence, and outline litigation strategy', domain: 'legal.advisory' },
  { id: 'leg_2', text: 'Evaluate employment termination circumstances and calculate severance entitlements', domain: 'legal.advisory' },
  { id: 'leg_3', text: 'Guide client through business formation including structure selection and regulatory requirements', domain: 'legal.advisory' },
  { id: 'leg_4', text: 'Assess intellectual property rights and recommend protection strategy', domain: 'legal.advisory' },

  // Finance
  { id: 'fin_1', text: 'Review retirement portfolio allocation and recommend rebalancing strategy aligned with timeline', domain: 'finance.advisory' },
  { id: 'fin_2', text: 'Evaluate mortgage capacity, compare loan products, and guide toward pre-approval', domain: 'finance.advisory' },
  { id: 'fin_3', text: 'Develop personalized investment strategy based on risk tolerance and financial goals', domain: 'finance.advisory' },
  { id: 'fin_4', text: 'Analyze tax implications of proposed financial transactions and optimize tax efficiency', domain: 'finance.advisory' },

  // Industrial
  { id: 'ind_1', text: 'Diagnose equipment error code, guide operator through safe troubleshooting, and determine if on-site maintenance is required', domain: 'industrial.support' },
  { id: 'ind_2', text: 'Schedule preventive maintenance coordinating downtime windows with production plan', domain: 'industrial.support' },
  { id: 'ind_3', text: 'Investigate safety incident, document findings, and recommend corrective actions', domain: 'industrial.support' },

  // Education
  { id: 'edu_1', text: 'Guide the student through understanding and solving problems using step-by-step explanations', domain: 'education.tutoring' },
  { id: 'edu_2', text: 'Prepare student for exam by reviewing key concepts, common mistakes, and practice problems', domain: 'education.tutoring' },
  { id: 'edu_3', text: 'Help student develop essay writing skills through structured feedback and revision guidance', domain: 'education.tutoring' },
]

export function getObjectiveTemplates(domain?: string): ObjectiveTemplate[] {
  if (!domain) return OBJECTIVE_TEMPLATES

  return OBJECTIVE_TEMPLATES.filter(t => t.domain === domain)
}
