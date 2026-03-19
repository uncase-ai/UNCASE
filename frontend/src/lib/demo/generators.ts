import type { Conversation, ConversationTurn, QualityReport, SeedSchema } from '@/types/api'

// ─── Domain-specific mock conversation turns (English) ───
export const MOCK_TURNS: Record<string, { user: string[]; assistant: string[] }> = {
  'automotive.sales': {
    user: [
      'Good morning, I\'m looking for a family vehicle. What options do you have?',
      'I\'m interested in something with good fuel economy and space for 5. Ideally an SUV.',
      'The XR5 sounds great. What\'s the all-in price with everything included?',
      'Do you have financing options? My budget is around $20,000 down.',
      'That monthly payment works for me. Can I trade in my current car?',
      'It\'s a 2020 sedan with about 45,000 miles, in good condition.',
      'I\'d like to schedule a test drive for this Saturday if possible.',
      'What warranty coverage does the XR5 include?',
      'That\'s very thorough. What documents do I need to start the credit process?',
      'Perfect, I\'ll bring everything Saturday. Thanks for your help!',
    ],
    assistant: [
      'Welcome! I\'d be happy to help you find the right vehicle. We have excellent options in SUVs and family sedans. Do you have a budget range in mind?',
      'For your needs, I\'d recommend the XR5 2025 model. It seats 7 with a third row, gets 14 km/l in the city, and has top safety ratings. It starts at $689,900.',
      'The final price with tax, plates, and inspection is $864,084 MXN. That includes the advanced safety package and a 5-year/100K km comprehensive warranty.',
      'Absolutely. We offer financing from 12 to 72 months. With $20,000 down, your monthly payment would be approximately $15,800 at 48 months with our preferred rate of 9.9% APR.',
      'Yes, our trade-in program lets you apply your current vehicle\'s value toward the down payment. We can appraise it on the spot or within 24 hours.',
      'A 2020 sedan in good condition with that mileage should appraise well. We\'ll give you a competitive market-based valuation when you bring it in.',
      'Saturday at 10:00 AM works perfectly. The test drive takes about 30 minutes on a route that includes city and highway driving. Just bring your valid license.',
      'The XR5 includes a factory warranty of 5 years or 100,000 km, whichever comes first. It covers engine, transmission, electronics, and roadside assistance for the first 3 years.',
      'For credit pre-approval you\'ll need: official government ID, proof of address (less than 3 months old), your last 3 pay stubs, and your last bank statement. We can start the process in about 20 minutes.',
      'You\'re welcome! I\'ll have everything ready for your Saturday visit. Here\'s my card — feel free to call or text if any questions come up before then.',
    ],
  },
  'medical.consultation': {
    user: [
      'Doctor, I\'ve been having frequent headaches for the last two weeks, mostly in the afternoon.',
      'The pain is usually on both sides, like a tight band around my head. It lasts a few hours.',
      'Could it be something serious? I\'m a little worried because they\'ve been so persistent.',
      'I haven\'t taken any medication yet, just tried resting and drinking more water.',
      'Yes, I\'ve been under a lot of stress at work and spending 10+ hours on the computer daily.',
      'My mother has a history of migraines. Could this be hereditary?',
      'What tests would you recommend to make sure nothing else is going on?',
      'What treatment do you suggest in the meantime?',
      'Are there lifestyle changes I should make to prevent these from recurring?',
      'Thank you doctor, I\'ll follow the treatment plan and come back in two weeks.',
    ],
    assistant: [
      'I understand your concern. Let\'s go through your symptoms carefully. Can you describe the location and character of the pain — is it throbbing, pressing, or sharp?',
      'That pattern is very consistent with tension-type headaches, which are the most common form. The bilateral pressing quality and afternoon onset are typical. Have you noticed any visual disturbances or nausea along with the pain?',
      'Based on your description, I\'m confident this is a tension-type headache. The bilateral distribution and pressing quality make serious causes very unlikely. However, we\'ll do a thorough evaluation to be certain.',
      'It\'s good you haven\'t self-medicated. Hydration helps, but we should start a targeted treatment. First, let me ask — have you had any changes in your daily routine, sleep, or stress levels recently?',
      'That\'s very likely the primary trigger. Prolonged screen time causes eye strain and sustained neck tension, both of which commonly produce this type of headache. We call this cervicogenic component.',
      'Family history of migraine is relevant. While your current presentation fits tension-type, we\'ll monitor for any migraine features — such as one-sided pain, light sensitivity, or nausea — and adjust the diagnosis if needed.',
      'I\'ll order a complete blood count, metabolic panel, and thyroid function tests to rule out systemic causes. If your headaches don\'t improve within 3 weeks, we\'ll consider a CT scan for additional reassurance.',
      'I recommend acetaminophen 500mg every 8 hours as needed for 5 days, plus a daily 20-minute stretching routine for your neck and shoulders. Maintain at least 2 liters of water daily and take 5-minute screen breaks every hour.',
      'Absolutely. Aim for 7-8 hours of sleep on a regular schedule, limit caffeine to 2 cups before noon, and consider a brief daily walk or exercise. Managing work stress through breaks and boundaries will also make a significant difference.',
      'You\'re welcome. Follow the full treatment course even if you start feeling better. If the pain worsens suddenly, you develop new symptoms like vision changes or fever, come back immediately. Otherwise I\'ll see you in two weeks.',
    ],
  },
  'finance.advisory': {
    user: [
      'I\'m looking to review my retirement portfolio. I\'m 5 years from retirement.',
      'My current allocation is about 70% stocks and 30% bonds. Is that too aggressive?',
      'What would you recommend given my timeline?',
      'Are there tax implications if we rebalance now?',
      'What about inflation protection? I\'m worried about purchasing power.',
      'How often should we review and adjust the allocation going forward?',
      'Can you summarize the proposed changes and estimated returns?',
      'I\'d like to proceed. What are the next steps?',
    ],
    assistant: [
      'Welcome! Let\'s start by reviewing your current portfolio performance. Based on our records, your portfolio has returned 8.2% annually over the past 3 years. With a 5-year horizon, we should discuss adjusting your risk profile.',
      'For a 5-year retirement timeline, 70/30 is indeed on the aggressive side. Most financial planning models suggest gradually shifting toward a 50/50 or 60/40 allocation as you approach retirement to protect against sequence-of-returns risk.',
      'I recommend a phased rebalancing: move to 60/40 this year, then 55/45 next year, reaching 50/50 by year 3. This reduces volatility while maintaining growth potential. We should also add 10% allocation to TIPS for inflation protection.',
      'Yes, there are important considerations. Selling appreciated positions in taxable accounts triggers capital gains. I recommend tax-loss harvesting on underperforming positions to offset gains, and making changes within your IRA first where there\'s no tax impact.',
      'Excellent concern. TIPS (Treasury Inflation-Protected Securities) and I-Bonds provide direct inflation hedging. We can also maintain 15-20% in dividend-growth stocks, which historically outpace inflation over 5-year periods.',
      'I recommend quarterly reviews with small adjustments, and a comprehensive annual review. We\'ll set up automatic rebalancing alerts when any allocation drifts more than 5% from target.',
      'Here\'s the summary: Shift from 70/30 to 50/50 over 3 years, add 10% TIPS allocation, implement tax-loss harvesting to minimize tax impact, and set up quarterly monitoring. Historical modeling suggests a 5-6% annual return with 40% less volatility than your current allocation.',
      'I\'ll prepare the rebalancing trades for your review by end of this week. We\'ll start with the IRA accounts to avoid tax events, then address the taxable accounts using the harvesting strategy we discussed. I\'ll send you the detailed proposal to review before executing.',
    ],
  },
  'legal.advisory': {
    user: [
      'I need legal advice. My former business partner breached our partnership agreement.',
      'We had a written agreement that he would not compete within 50 miles for 2 years. He opened a competing business 3 months after leaving.',
      'I have the signed agreement, email correspondence where he acknowledged the non-compete, and customer records showing clients he took.',
      'What are my legal options? Can I get an injunction to stop him?',
      'What would litigation cost and how long would it take?',
      'Is mediation a viable alternative?',
      'What do you need from me to get started?',
      'Let\'s proceed with the demand letter first and prepare for litigation if needed.',
    ],
    assistant: [
      'I understand your concern. Let me gather some details. When did your partner leave the business, and when did you first become aware of the competing operation? These timelines are critical for establishing the breach and any statute of limitations considerations.',
      'That\'s a clear factual basis for a non-compete violation. The 50-mile, 2-year restriction is reasonable in most jurisdictions. The fact that he opened within 3 months strengthens your case considerably, as courts view early violations as willful.',
      'Your evidence position is strong. The signed agreement establishes the contractual obligation, the emails demonstrate awareness and intent, and the customer records prove actual damages. I\'d recommend we also document any revenue loss attributable to the diverted clients.',
      'You have two primary options: First, we can seek a temporary restraining order (TRO) and preliminary injunction to immediately halt his competing activities. Given your evidence, I believe we have a strong likelihood of success. Second, we can pursue damages for breach of contract — lost profits, client diversion, and potentially punitive damages if we can show willful and malicious breach.',
      'For the injunction process: filing through resolution typically takes 30-60 days. If we need to go to full trial, expect 8-12 months. Cost estimates: the injunction phase would be approximately $15,000-$25,000 in legal fees. Full litigation through trial could range from $50,000-$100,000, depending on complexity and whether he contests vigorously.',
      'Mediation is absolutely worth considering. It\'s faster (typically 1-3 months), less expensive ($5,000-$15,000), and confidential. However, I\'d recommend sending a formal demand letter first. In my experience, about 40% of non-compete cases settle after a strong demand letter without needing formal proceedings.',
      'I\'ll need: the original partnership agreement, all email correspondence with your former partner, financial records showing revenue before and after his departure, a list of clients who moved to his new business, and any evidence of solicitation. I\'ll also need you to sign an engagement letter and we\'ll run a standard conflicts check.',
      'Good strategy. I\'ll draft the demand letter within 5 business days for your review. It will outline the breach, demand immediate cessation of competing activities, and propose a settlement discussion with a 14-day response deadline. Simultaneously, I\'ll begin preparing the injunction filing so we can move quickly if he doesn\'t respond favorably.',
    ],
  },
  'industrial.support': {
    user: [
      'This is Operator 7 at Line 3. We\'re getting error code E-47 on the CNC milling station. Production is halted.',
      'The error appeared during a cutting cycle on aluminum stock. The spindle stopped mid-operation and the control panel shows E-47 with a red warning light.',
      'Yes, the machine is in emergency stop. I\'ve followed lockout procedure and the area is secured.',
      'Temperature reading shows 87°C on the spindle motor. Normal operating range is 45-65°C.',
      'I checked the coolant — the reservoir level is low, about 20% capacity. The flow indicator shows intermittent flow.',
      'The coolant filter looks clogged. There\'s significant aluminum shavings buildup.',
      'Understood. I\'ve replaced the filter from our spare parts stock. Coolant flow is restored and reading normal.',
      'The spindle temperature is dropping — currently at 62°C and falling. Ready to attempt restart when you give the go-ahead.',
    ],
    assistant: [
      'Acknowledged, Operator 7. E-47 is a spindle overtemperature protection fault. This is a safety-critical alert. First priority: confirm the machine is in emergency stop and lockout/tagout is complete. Are you and the area safe?',
      'Good, the mid-cycle stop is consistent with E-47. The protection system triggered correctly. I\'m pulling up the diagnostic data remotely. Can you check the spindle motor temperature reading on the control panel — it should be under the DIAGNOSTICS > THERMAL menu?',
      'That\'s significantly above the 65°C threshold — the protection system was right to halt. This is almost certainly a cooling system issue. Before we investigate further, I need you to check two things: First, the coolant reservoir level. Second, the coolant flow indicator on the supply line to the spindle.',
      'That confirms our diagnosis. Low coolant level plus intermittent flow means the spindle wasn\'t getting adequate cooling. The most common cause is either a clogged coolant filter or a failing pump. Can you visually inspect the coolant filter housing?',
      'That\'s the root cause. Aluminum chip buildup in the filter restricted coolant flow, causing the spindle to overheat. We need to: 1) Replace the coolant filter immediately. 2) Flush and refill the coolant reservoir. 3) Check the filter replacement schedule in CMMS — it may need to be shortened for aluminum jobs.',
      'Once the new filter is in and coolant is flowing normally, let the spindle cool below 50°C before attempting restart. I\'m logging this incident in CMMS as ticket MT-2847. I\'m also updating the PM schedule to increase filter inspection frequency for aluminum machining operations.',
      'Temperature recovery looks good. Once you hit 50°C, you can clear the E-47 fault by pressing RESET on the control panel, then run a 2-minute spindle warm-up at 2000 RPM before resuming production. Monitor the temperature for the first 15 minutes of operation and report if it rises above 60°C.',
    ],
  },
  'education.tutoring': {
    user: [
      'I have a math test tomorrow on quadratic equations and I don\'t understand how to solve them at all.',
      'I know the standard form is ax² + bx + c = 0, but I don\'t know what to do with it after that.',
      'I think I\'ve heard of factoring but I\'m not sure how it works with quadratics.',
      'So for x² + 5x + 6 = 0, I need to find two numbers that multiply to 6 and add to 5... would that be 2 and 3?',
      'So it becomes (x + 2)(x + 3) = 0, and then x = -2 or x = -3?',
      'What if I can\'t find numbers that work for factoring?',
      'Can you give me one to try with the quadratic formula? Maybe x² + 2x - 5 = 0?',
      'I feel much better about this now. Can you give me a few practice problems to try on my own?',
    ],
    assistant: [
      'Don\'t worry — quadratic equations look intimidating but there are clear, step-by-step methods. There are three main approaches: factoring, completing the square, and the quadratic formula. Let\'s start with the simplest one. First, remind me — do you know the standard form of a quadratic equation?',
      'That\'s the starting point. Now, the goal is always to find the values of x that make the equation true — these are called the "roots" or "solutions." The simplest method is factoring. Think of it like this: we\'re trying to rewrite the equation as a product of two simpler expressions. Have you seen factoring before?',
      'Great! Here\'s how factoring works with quadratics. If we have x² + 5x + 6 = 0, we need to find two numbers that: 1) Multiply together to give us 6 (the "c" value), and 2) Add together to give us 5 (the "b" value). Can you think of two numbers that multiply to 6 and add to 5?',
      'Exactly right! 2 × 3 = 6 and 2 + 3 = 5. Now we rewrite the equation using these numbers: x² + 5x + 6 = (x + 2)(x + 3) = 0. Now here\'s the key insight — if two things multiplied together equal zero, at least one of them MUST be zero. So what are the solutions?',
      'You got it! x = -2 or x = -3. You can verify: plug -2 back in → (-2)² + 5(-2) + 6 = 4 - 10 + 6 = 0. That\'s the beauty of factoring — quick and clean when it works. Now, you asked a very smart question...',
      'That\'s exactly where the quadratic formula comes in. It works for ANY quadratic equation: x = (-b ± √(b²-4ac)) / 2a. The ± means you get two answers — one with plus, one with minus. The part under the square root (b²-4ac) is called the discriminant — it tells you how many solutions exist. Let\'s try one together.',
      'Perfect choice. Here a=1, b=2, c=-5. Let\'s plug in: x = (-2 ± √(4-4(1)(-5))) / 2(1) = (-2 ± √(4+20)) / 2 = (-2 ± √24) / 2 = (-2 ± 2√6) / 2 = -1 ± √6. So x ≈ 1.449 or x ≈ -3.449. Notice how these aren\'t nice whole numbers — that\'s why factoring wouldn\'t have worked here. The formula always gives you the answer.',
      'Here are 5 practice problems in order of difficulty: 1) x² - 7x + 12 = 0 (factoring), 2) x² + 4x - 21 = 0 (factoring), 3) 2x² - 8x + 6 = 0 (factor out 2 first), 4) x² + 6x + 2 = 0 (quadratic formula), 5) 3x² - 5x - 1 = 0 (quadratic formula). Try them and check: the answer to #1 is x = 3 or x = 4. You\'ve got this!',
    ],
  },
}

export const DEFAULT_MOCK_TURNS = {
  user: ['Hello, I need help with a question.', 'Could you give me more details?', 'Thanks, that\'s very helpful.', 'Is there anything else I should consider?'],
  assistant: ['I\'d be happy to help. How can I assist you?', 'Of course, let me explain in detail.', 'That\'s an excellent question. Here\'s the information.', 'I recommend keeping these additional points in mind.'],
}

export function generateDemoConversation(seed: SeedSchema): Conversation {
  const minTurns = seed.pasos_turnos?.turnos_min ?? 4
  const maxTurns = seed.pasos_turnos?.turnos_max ?? 8
  const numTurns = minTurns + Math.floor(Math.random() * (maxTurns - minTurns + 1))
  const roles = (seed.roles?.length ?? 0) >= 2 ? seed.roles : ['user', 'assistant']
  const pool = MOCK_TURNS[seed.dominio] ?? DEFAULT_MOCK_TURNS

  const turnos: ConversationTurn[] = Array.from({ length: numTurns }, (_, i) => {
    const isUser = i % 2 === 0
    const bank = isUser ? pool.user : pool.assistant
    const bankIdx = Math.floor(i / 2) % bank.length

    return {
      turno: i + 1,
      rol: roles[i % roles.length],
      contenido: bank[bankIdx],
      herramientas_usadas: [],
      metadata: {},
    }
  })

  return {
    conversation_id: crypto.randomUUID(),
    seed_id: seed.seed_id,
    dominio: seed.dominio,
    idioma: seed.idioma,
    turnos,
    es_sintetica: true,
    created_at: new Date().toISOString(),
    metadata: { generated_by: 'uncase-demo', source_seed: seed.seed_id },
  }
}

export function generateDemoQualityReport(conv: Conversation, seed: SeedSchema): QualityReport {
  const r = () => 0.85 + Math.random() * 0.13

  const metrics = {
    rouge_l: r(),
    fidelidad_factual: r(),
    diversidad_lexica: 0.60 + Math.random() * 0.25,
    coherencia_dialogica: r(),
    tool_call_validity: 1.0,
    privacy_score: 0.0,
    memorizacion: 0.001 + Math.random() * 0.005,
    semantic_fidelity: r(),
    embedding_drift: 0.65 + Math.random() * 0.25,
  }

  const composite = Math.min(
    metrics.rouge_l, metrics.fidelidad_factual, metrics.diversidad_lexica,
    metrics.coherencia_dialogica, metrics.tool_call_validity,
    metrics.semantic_fidelity, metrics.embedding_drift
  )

  return {
    conversation_id: conv.conversation_id,
    seed_id: seed.seed_id,
    metrics,
    composite_score: Math.round(composite * 1000) / 1000,
    passed: true,
    failures: [],
    evaluated_at: new Date().toISOString(),
  }
}
