'use client'

import { useCallback, useEffect, useState } from 'react'

import Link from 'next/link'
import {
  AlertTriangle,
  Clock,
  Cloud,
  CloudOff,
  HelpCircle,
  History,
  Info,
  Loader2,
  Rocket,
  Sparkles,
  StopCircle,
  X,
  Zap
} from 'lucide-react'

import type { SeedSchema, Conversation, ConversationTurn, QualityReport } from '@/types/api'
import { cn } from '@/lib/utils'
import { checkApiHealth } from '@/lib/api/client'
import { bulkCreateConversations } from '@/lib/api/conversations'
import { generateConversations } from '@/lib/api/generate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

import { EmptyState } from '../empty-state'
import { PageHeader } from '../page-header'

// ─── Local Storage Keys ───
const SEEDS_KEY = 'uncase-seeds'
const CONVERSATIONS_KEY = 'uncase-conversations'
const HISTORY_KEY = 'uncase-generation-history'

// ─── Types ───
interface GenerationRun {
  id: string
  timestamp: string
  seed_count: number
  conversations_per_seed: number
  conversation_count: number
  temperature: number
  language_override: string | null
  seed_ids: string[]
  mode: 'demo' | 'api'
}

// ─── Storage helpers ───
function loadSeeds(): SeedSchema[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(SEEDS_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function loadConversations(): Conversation[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(CONVERSATIONS_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveConversations(conversations: Conversation[]) {
  localStorage.setItem(CONVERSATIONS_KEY, JSON.stringify(conversations))
}

function loadHistory(): GenerationRun[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(HISTORY_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveHistory(history: GenerationRun[]) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history))
}

// ─── Mock generation ───

// Domain-specific turn content templates — the mock generator picks randomly
// to produce realistic-looking conversations for demo mode.
const MOCK_TURNS: Record<string, { user: string[]; assistant: string[] }> = {
  'automotive.sales': {
    user: [
      'Buenos días, estoy buscando un vehículo familiar. ¿Qué opciones tienen?',
      'Me interesa algo con buen rendimiento de combustible y espacio para 5 personas.',
      '¿Cuál es el precio con todo incluido?',
      '¿Tienen opciones de financiamiento? Mi presupuesto es limitado.',
      'Me gustaría agendar una prueba de manejo para el fin de semana.',
      '¿Qué garantía incluye el vehículo?',
      '¿Manejan programa de trade-in? Tengo un auto 2020 que me gustaría dejar.',
      'Perfecto, me interesa. ¿Cuáles son los siguientes pasos?',
      '¿Tienen el modelo en color blanco o gris?',
      '¿El seguro está incluido en la mensualidad?',
    ],
    assistant: [
      'Bienvenido, con gusto le ayudo. Tenemos excelentes opciones en SUVs y sedanes familiares. ¿Tiene algún rango de presupuesto en mente?',
      'Para sus necesidades, le recomiendo el Modelo XR5 2025. Tiene tercera fila de asientos, rendimiento de 14 km/l en ciudad y está disponible desde $689,900.',
      'El precio final con IVA, placas y verificación es de $864,084 MXN. Incluye paquete de seguridad y garantía de 5 años o 100,000 km.',
      'Contamos con financiamiento desde 12 hasta 72 meses. Con un enganche del 20%, su mensualidad quedaría en aproximadamente $15,800 a 48 meses con tasa preferencial.',
      'Perfecto, tenemos disponibilidad el sábado a las 10:00 AM. La prueba dura aproximadamente 30 minutos. Solo necesita traer su licencia vigente.',
      'El vehículo incluye garantía de fábrica de 5 años o 100,000 km, lo que ocurra primero. Cubre motor, transmisión y componentes electrónicos.',
      'Claro, nuestro programa de trade-in le permite usar su vehículo actual como enganche. Basado en las condiciones de mercado, podemos hacer una valuación en 24 horas.',
      'El siguiente paso sería la pre-aprobación de crédito. Necesitaría traer identificación oficial, comprobante de domicilio y últimos 3 recibos de nómina.',
      'Sí, tenemos 2 unidades en blanco y 1 en gris plata disponibles para entrega inmediata.',
      'El seguro se cotiza por separado, pero contamos con convenios con aseguradoras que ofrecen tarifas preferenciales para nuestros clientes.',
    ],
  },
  'medical.consultation': {
    user: [
      'Doctor, he tenido dolor de cabeza frecuente las últimas dos semanas.',
      '¿Podría ser algo serio? Me preocupa un poco.',
      'No he tomado ningún medicamento, solo descanso.',
      '¿Necesito hacerme algún estudio?',
      '¿Cuándo debo regresar a consulta?',
      'Tengo antecedentes de migraña en mi familia.',
      '¿Hay algo que deba evitar mientras tanto?',
      'Gracias doctor, seguiré sus indicaciones.',
    ],
    assistant: [
      'Entiendo su preocupación. Vamos a revisar sus síntomas en detalle. ¿El dolor es constante o viene por episodios? ¿En qué zona de la cabeza lo siente?',
      'Basado en lo que me describe, parece una cefalea tensional, que es la más común. Sin embargo, necesitamos descartar otras causas. ¿Ha tenido cambios en su visión o náuseas?',
      'Le recomiendo iniciar con paracetamol 500mg cada 8 horas durante 5 días. También es importante mantener una buena hidratación y descanso adecuado.',
      'Vamos a solicitar unos estudios de laboratorio básicos: biometría hemática, química sanguínea y perfil tiroideo. Si los síntomas persisten, consideraremos una tomografía.',
      'Le agendo cita de seguimiento en 2 semanas. Si el dolor empeora, aparecen síntomas nuevos o no cede con el tratamiento, regrese antes.',
      'Los antecedentes familiares son relevantes. Vamos a monitorear si el patrón de dolor es compatible con migraña y ajustar el tratamiento según sea necesario.',
      'Evite el exceso de pantallas, procure dormir entre 7 y 8 horas, y reduzca el consumo de cafeína. El estrés también puede ser un factor desencadenante.',
      'Quedo a sus órdenes. Recuerde seguir el tratamiento completo y no suspenderlo aunque se sienta mejor.',
    ],
  },
  'finance.advisory': {
    user: [
      'Quisiera invertir mis ahorros pero no sé por dónde empezar.',
      '¿Cuál es el rendimiento esperado de ese instrumento?',
      'Mi tolerancia al riesgo es moderada. No quiero perder mi capital.',
      '¿Cuánto necesito como mínimo para empezar?',
      '¿Qué comisiones cobran por el manejo de la cuenta?',
      '¿Puedo retirar mi dinero en cualquier momento?',
    ],
    assistant: [
      'Con gusto le asesoro. Primero necesitamos definir su perfil de inversión: horizonte temporal, tolerancia al riesgo y objetivos financieros. ¿Para cuándo necesitaría disponer de estos recursos?',
      'Para un perfil moderado con horizonte de 3 a 5 años, un portafolio diversificado en renta fija y variable podría generar entre 8% y 12% anual. El rendimiento pasado no garantiza rendimientos futuros.',
      'Excelente. Para su perfil recomiendo 60% renta fija (CETES, bonos gubernamentales) y 40% renta variable (ETFs diversificados). Esto equilibra seguridad con crecimiento.',
      'Puede iniciar desde $10,000 MXN. Sin embargo, para una diversificación adecuada recomiendo al menos $50,000. Podemos establecer aportaciones mensuales automáticas.',
      'Manejamos una comisión anual del 1.2% sobre el saldo administrado. No hay comisiones por apertura, depósito ni retiro. El cobro es mensual prorrateado.',
      'Sí, su capital está disponible en cualquier momento. Los instrumentos de renta fija tienen liquidez en 48 horas hábiles, y los de renta variable en 72 horas.',
    ],
  },
  'legal.advisory': {
    user: [
      'Necesito asesoría para constituir una empresa. ¿Qué tipo de sociedad me conviene?',
      'Seríamos 3 socios con inversión inicial de 500,000 pesos. El giro es tecnología.',
      '¿Cuánto tiempo toma el proceso completo?',
      '¿Cuáles son los requisitos fiscales iniciales?',
      '¿Necesito un apoderado legal?',
      '¿Qué obligaciones laborales tengo si voy a contratar empleados?',
      '¿Cómo protejo la propiedad intelectual del software que desarrollamos?',
      '¿Cuánto costarían sus servicios para todo este proceso?',
    ],
    assistant: [
      'Depende de varios factores: número de socios, capital inicial, y el giro del negocio. Para la mayoría de las PYMES tecnológicas, recomiendo una S.A.S. (Sociedad por Acciones Simplificada) por su flexibilidad y menores requisitos de gobierno corporativo.',
      'Con 3 socios y $500K de capital, la S.A.S. es ideal. No requiere capital mínimo, permite un solo administrador, y los socios limitan su responsabilidad a sus aportaciones. Para tecnología, también recomiendo incluir cláusulas de propiedad intelectual en el acta constitutiva.',
      'La constitución ante notario toma entre 5 y 10 días hábiles. El registro ante el SAT y la inscripción en el Registro Público se completan en 2-3 semanas adicionales. En total, puede estar operando formalmente en 4-6 semanas.',
      'Necesitará: alta en el SAT con RFC de persona moral, registro de e.firma, selección de régimen fiscal (recomiendo el de actividades empresariales), inscripción al IMSS como patrón, y apertura de cuenta bancaria empresarial.',
      'No es obligatorio pero sí recomendable. Un apoderado legal puede representar a la empresa en trámites, firmas y procedimientos sin necesidad de que todos los socios estén presentes. Generalmente se designa al administrador único.',
      'Al contratar, debe: registrarse como patrón ante IMSS e INFONAVIT, elaborar contratos laborales individuales, establecer reglamento interno de trabajo, crear un plan de previsión social, y cumplir con las obligaciones de nómina y retención de ISR.',
      'Para software, recomiendo tres capas de protección: 1) Registro de obras ante INDAUTOR como obra literaria, 2) Cláusulas de cesión de derechos en contratos laborales, y 3) Acuerdos de confidencialidad (NDA) con todos los colaboradores.',
      'El paquete completo de constitución, incluyendo acta constitutiva, trámites fiscales, registro de marca y revisión de contratos iniciales, tiene un costo de $45,000 + IVA. Incluye 3 meses de asesoría legal posterior a la constitución.',
    ],
  },
  'industrial.support': {
    user: [
      'La línea de producción 3 se detuvo. Muestra un código de error E-4521.',
      'El error apareció durante el ciclo de extrusión. La alarma sonó y el panel muestra luz roja.',
      'Sí, la máquina está en paro de emergencia. Ya seguí el procedimiento de bloqueo.',
      '¿Cuánto tiempo tomaría la reparación?',
      '¿Tienen la pieza en stock o hay que pedirla?',
      '¿Esto afecta la garantía del equipo?',
      'Ya se instaló el sensor nuevo. ¿Cómo procedo con la calibración?',
      'La lectura es estable. ¿Puedo reiniciar la producción?',
    ],
    assistant: [
      'El código E-4521 indica un fallo en el sensor de temperatura del módulo de extrusión. Necesitamos verificar si es el sensor o el cableado. Primero confirme: ¿la máquina está en paro de emergencia y el área está asegurada?',
      'Entendido. El fallo durante el ciclo de extrusión es consistente con E-4521. La protección térmica se activó correctamente. Estoy revisando los datos de diagnóstico remotos. ¿Puede verificar la lectura de temperatura en DIAGNÓSTICO > TÉRMICO del panel de control?',
      'Perfecto, el procedimiento de bloqueo es correcto. Ahora necesito que verifique: 1) La conexión del sensor TMP-4500 en el módulo de extrusión, y 2) El estado del cableado entre el sensor y la tarjeta de control. Busque signos de daño, desgaste o desconexión.',
      'Si es solo el sensor, la reparación toma aproximadamente 2 horas incluyendo calibración. Si hay daño en el cableado, podría extenderse a 4-6 horas. Le envío un técnico certificado para asistir con el reemplazo.',
      'Tenemos 3 unidades del sensor TMP-4500 en almacén de refacciones. Si necesitamos el módulo completo de control, el tiempo de entrega es de 48 horas desde fábrica. Para este caso, el sensor individual debería ser suficiente.',
      'No, la reparación está cubierta por el contrato de mantenimiento preventivo vigente. Solo aplican costos adicionales si se detecta mal uso o modificaciones no autorizadas al equipo. Estoy registrando el incidente como ticket MT-3291 en CMMS.',
      'Para calibrar: 1) Ingrese al menú SETUP > SENSOR CALIBRACIÓN en el panel, 2) Seleccione TMP-4500, 3) Ejecute la secuencia de auto-calibración, y 4) Verifique que la lectura estabilice entre 20-25°C a temperatura ambiente. El proceso toma aproximadamente 15 minutos.',
      'Si la lectura es estable y está dentro del rango, puede limpiar la alarma E-4521 presionando RESET en el panel. Ejecute un ciclo de calentamiento a baja velocidad durante 5 minutos antes de reanudar producción normal. Monitoree la temperatura los primeros 30 minutos de operación.',
    ],
  },
  'education.tutoring': {
    user: [
      'No entiendo bien el concepto de derivadas. ¿Me lo puede explicar?',
      'Creo que entiendo la idea general, pero no sé cómo calcularlas.',
      '¿Puede darme un ejemplo práctico paso a paso?',
      'Entonces si f(x) = 3x², la derivada sería f\'(x) = 6x, ¿verdad?',
      '¿Cómo resuelvo derivadas de funciones compuestas?',
      'Me cuesta trabajo identificar cuál es la función interna y cuál la externa.',
      '¿Tiene ejercicios para practicar?',
      'Gracias, creo que ya me queda más claro. ¿Algo más que deba estudiar para el examen?',
    ],
    assistant: [
      'La derivada mide la tasa de cambio instantánea de una función. Imagina que conduces un auto: la posición es la función, la velocidad es la derivada (cuánto cambia la posición por unidad de tiempo). ¿Has escuchado antes la idea de "razón de cambio"?',
      'Empecemos con la regla más básica: la regla de la potencia. Si f(x) = xⁿ, entonces f\'(x) = n·xⁿ⁻¹. Es decir, bajas el exponente como coeficiente y reduces el exponente en 1. ¿Quieres intentar con un ejemplo sencillo?',
      'Vamos con f(x) = x². Aplicando la regla: el exponente es 2, baja como coeficiente → 2x. El exponente se reduce en 1 → 2-1=1. Resultado: f\'(x) = 2x. Esto significa que en x=3, la función crece a una tasa de 6 unidades por cada unidad que avanza x. Es la pendiente de la recta tangente en ese punto.',
      '¡Exactamente! Muy bien. El 3 es un coeficiente constante que se mantiene, y el exponente 2 baja multiplicando: 3 × 2 = 6, y el exponente se reduce a 1. Entonces f\'(x) = 6x. En x=2, la pendiente es 12. Vas por muy buen camino.',
      'Para funciones compuestas usamos la regla de la cadena. Si y = f(g(x)), entonces y\' = f\'(g(x)) · g\'(x). Piénsalo así: derivas de afuera hacia adentro y multiplicas cada paso. Es como pelar una cebolla — capa por capa.',
      'Un truco que funciona muy bien: pregúntate "¿qué es lo último que haría si tuviera que evaluar esta función?" Eso es la función externa. Por ejemplo, en (3x+1)⁵, lo último que harías es elevar a la quinta potencia — esa es f. La función interna es g(x) = 3x+1. Entonces: f\'= 5(3x+1)⁴ · 3 = 15(3x+1)⁴.',
      'Le preparo una serie de 10 ejercicios graduales: los primeros 3 son derivadas directas (regla de potencia), luego 4 con regla de la cadena, y los últimos 3 combinan múltiples reglas. La respuesta del ejercicio 1 es f\'(x) = 12x³. ¿Quiere que los resolvamos juntos o los intenta por su cuenta primero?',
      'Para el examen, asegúrate de dominar también: 1) La regla del producto: (fg)\' = f\'g + fg\', 2) La regla del cociente: (f/g)\' = (f\'g - fg\')/g², y 3) Las derivadas de funciones trigonométricas básicas (sen, cos, tan). Con eso y la regla de la cadena, puedes resolver cualquier ejercicio que te pongan.',
    ],
  },
}

const DEFAULT_MOCK_TURNS = {
  user: ['Hola, necesito ayuda con una consulta.', '¿Podría darme más detalles?', 'Gracias, eso es muy útil.', '¿Hay algo más que deba considerar?'],
  assistant: ['Con gusto le ayudo. ¿En qué puedo asistirle?', 'Claro, permítame explicarle en detalle.', 'Esa es una excelente pregunta. Aquí tiene la información.', 'Le recomiendo tener en cuenta estos puntos adicionales.'],
}

function generateMockConversation(seed: SeedSchema, languageOverride?: string): Conversation {
  const minTurns = seed.pasos_turnos?.turnos_min ?? 3
  const maxTurns = seed.pasos_turnos?.turnos_max ?? 10
  const numTurns = minTurns + Math.floor(Math.random() * (maxTurns - minTurns + 1))

  const roles = (seed.roles?.length ?? 0) >= 2 ? seed.roles : ['usuario', 'asistente']
  const idioma = languageOverride || seed.idioma
  const pool = MOCK_TURNS[seed.dominio] ?? DEFAULT_MOCK_TURNS

  const turnos: ConversationTurn[] = Array.from({ length: numTurns }, (_, i) => {
    const isUser = i % 2 === 0
    const bank = isUser ? pool.user : pool.assistant
    const content = bank[Math.floor(Math.random() * bank.length)]

    return {
      turno: i + 1,
      rol: roles[i % roles.length],
      contenido: content,
      herramientas_usadas: [],
      metadata: {}
    }
  })

  return {
    conversation_id: crypto.randomUUID(),
    seed_id: seed.seed_id,
    dominio: seed.dominio,
    idioma,
    turnos,
    es_sintetica: true,
    created_at: new Date().toISOString(),
    metadata: {
      generated_by: 'uncase-demo-generator',
      source_seed: seed.seed_id
    }
  }
}

function generateMockQualityReport(conv: Conversation, seedId: string): QualityReport {
  const metrics = {
    rouge_l: 0.25 + Math.random() * 0.25,
    fidelidad_factual: 0.82 + Math.random() * 0.16,
    diversidad_lexica: 0.58 + Math.random() * 0.25,
    coherencia_dialogica: 0.68 + Math.random() * 0.27,
    tool_call_validity: 1.0,
    privacy_score: 0.0,
    memorizacion: 0.001 + Math.random() * 0.005,
    semantic_fidelity: 0.65 + Math.random() * 0.28,
    embedding_drift: 0.35 + Math.random() * 0.50,
  }

  const composite = Math.min(
    metrics.rouge_l, metrics.fidelidad_factual, metrics.diversidad_lexica,
    metrics.coherencia_dialogica, metrics.tool_call_validity,
    metrics.semantic_fidelity, metrics.embedding_drift
  )

  // Weighted mean (mirrors backend weights)
  const pairs: [number, number][] = [
    [metrics.rouge_l, 0.15], [metrics.fidelidad_factual, 0.25],
    [metrics.diversidad_lexica, 0.10], [metrics.coherencia_dialogica, 0.20],
    [metrics.tool_call_validity, 0.10], [metrics.semantic_fidelity, 0.10],
    [metrics.embedding_drift, 0.10],
  ]

  const totalW = pairs.reduce((s, [, w]) => s + w, 0)
  const wMean = pairs.reduce((s, [v, w]) => s + v * w, 0) / totalW

  return {
    conversation_id: conv.conversation_id,
    seed_id: seedId,
    metrics,
    composite_score: Math.round(composite * 1000) / 1000,
    weighted_mean: Math.round(wMean * 1000) / 1000,
    passed: true,
    failures: [],
    evaluated_at: new Date().toISOString(),
  }
}

// ─── Domain Colors — neutral palette ───
const DOMAIN_COLORS: Record<string, string> = {
  'automotive.sales': '',
  'medical.consultation': '',
  'legal.advisory': '',
  'finance.advisory': '',
  'industrial.support': '',
  'education.tutoring': ''
}

const LANGUAGES = [
  { value: '', label: 'Use seed default' },
  { value: 'es', label: 'Spanish' },
  { value: 'en', label: 'English' }
] as const

export function GeneratePage() {
  const [seeds] = useState<SeedSchema[]>(() => loadSeeds())
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [conversationsPerSeed, setConversationsPerSeed] = useState(5)
  const [temperature, setTemperature] = useState(0.7)
  const [languageOverride, setLanguageOverride] = useState('')
  const [generating, setGenerating] = useState(false)
  const [progress, setProgress] = useState(0)
  const [lastRunCount, setLastRunCount] = useState<number | null>(null)
  const [history, setHistory] = useState<GenerationRun[]>(() => loadHistory())

  // API integration state
  const [apiAvailable, setApiAvailable] = useState(false)
  const [demoMode, setDemoMode] = useState(false)
  const [evaluateAfter, setEvaluateAfter] = useState(true)
  const [abortController, setAbortController] = useState<AbortController | null>(null)
  const [generationError, setGenerationError] = useState<string | null>(null)

  const [qualityResults, setQualityResults] = useState<{
    total: number
    passed: number
    avgScore: number | null
  } | null>(null)

  // ─── Check API health on mount ───
  useEffect(() => {
    let cancelled = false

    async function init() {
      const healthy = await checkApiHealth()

      if (!cancelled) {
        setApiAvailable(healthy)

        if (!healthy) setDemoMode(true)
      }
    }

    init()

    return () => {
      cancelled = true
    }
  }, [])

  // ─── Selection ───
  function toggleSeed(seedId: string) {
    setSelected(prev => {
      const next = new Set(prev)

      if (next.has(seedId)) {
        next.delete(seedId)
      } else {
        next.add(seedId)
      }

      return next
    })
  }

  function selectAll() {
    setSelected(new Set(seeds.map(s => s.seed_id)))
  }

  const clearSelection = useCallback(() => {
    setSelected(new Set())
  }, [])

  // ─── Cancel handler ───
  function handleCancel() {
    abortController?.abort()
    setAbortController(null)
  }

  // ─── Generation ───
  async function handleGenerate() {
    const selectedSeeds = seeds.filter(s => selected.has(s.seed_id))

    if (selectedSeeds.length === 0) return

    setGenerating(true)
    setProgress(0)
    setLastRunCount(null)
    setGenerationError(null)
    setQualityResults(null)

    const controller = new AbortController()

    setAbortController(controller)

    const totalConversations = selectedSeeds.length * conversationsPerSeed
    const generated: Conversation[] = []
    const allReports: QualityReport[] = []
    let completed = 0

    try {
      if (demoMode) {
        // Demo: use mock generator
        for (const seed of selectedSeeds) {
          for (let i = 0; i < conversationsPerSeed; i++) {
            if (controller.signal.aborted) break
            await new Promise(resolve => setTimeout(resolve, 50 + Math.random() * 100))

            const conversation = generateMockConversation(seed, languageOverride || undefined)

            generated.push(conversation)

            if (evaluateAfter) {
              allReports.push(generateMockQualityReport(conversation, seed.seed_id))
            }

            completed++
            setProgress(Math.round((completed / totalConversations) * 100))
          }

          if (controller.signal.aborted) break
        }
      } else {
        // Real API: one call per seed
        for (const seed of selectedSeeds) {
          if (controller.signal.aborted) break

          const { data, error } = await generateConversations(
            {
              seed,
              count: conversationsPerSeed,
              temperature,
              language_override: languageOverride || undefined,
              evaluate_after: evaluateAfter
            },
            controller.signal
          )

          if (error) {
            if (error.status === 0 && error.message === 'Request cancelled') break
            setGenerationError(
              `Generation failed for seed ${seed.seed_id?.slice(0, 8) ?? 'unknown'}: ${error.message}`
            )
            break
          }

          if (data) {
            generated.push(...data.conversations)

            if (data.reports) allReports.push(...data.reports)

            completed += data.generation_summary.total_generated
            setProgress(Math.round((completed / totalConversations) * 100))
          }
        }
      }
    } catch {
      // Cancelled or unexpected
    }

    if (generated.length > 0) {
      // Save to localStorage
      const existing = loadConversations()

      saveConversations([...existing, ...generated])

      // Best-effort API persistence (fire-and-forget) — in demo mode,
      // conversations only exist locally; sync them to the backend if available
      if (demoMode && apiAvailable) {
        bulkCreateConversations(
          generated.map(c => ({ ...c } as unknown as Record<string, unknown>))
        ).catch(() => {})
      }

      // Quality results
      if (allReports.length > 0) {
        const passedCount = allReports.filter(r => r.passed).length

        const avgScore =
          allReports.reduce((sum, r) => sum + r.composite_score, 0) / allReports.length

        setQualityResults({
          total: allReports.length,
          passed: passedCount,
          avgScore: Math.round(avgScore * 1000) / 1000
        })

        // Persist evaluation reports to localStorage
        try {
          const existingEvals: QualityReport[] = JSON.parse(localStorage.getItem('uncase-evaluations') || '[]')

          localStorage.setItem('uncase-evaluations', JSON.stringify([...existingEvals, ...allReports]))
        } catch { /* ignore parse errors */ }
      }

      // Save history
      const run: GenerationRun = {
        id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
        seed_count: selectedSeeds.length,
        conversations_per_seed: conversationsPerSeed,
        conversation_count: generated.length,
        temperature,
        language_override: languageOverride || null,
        seed_ids: selectedSeeds.map(s => s.seed_id),
        mode: demoMode ? 'demo' : 'api'
      }

      const updatedHistory = [run, ...history]

      setHistory(updatedHistory)
      saveHistory(updatedHistory)
    }

    setLastRunCount(generated.length)
    setGenerating(false)
    setProgress(100)
    setAbortController(null)
    clearSelection()
  }

  // ─── Computed ───
  const selectedCount = selected.size
  const totalToGenerate = selectedCount * conversationsPerSeed

  // ─── Empty state ───
  if (seeds.length === 0) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Synthetic Generation"
          description="Generate synthetic conversations from seeds"
        />
        <EmptyState
          icon={Rocket}
          title="No seeds available"
          description="Create seeds in the Seed Library first, then come back to generate synthetic conversations."
          action={
            <Button asChild variant="outline">
              <Link href="/dashboard/pipeline/seeds">
                <Sparkles className="mr-1.5 size-4" /> Go to Seed Library
              </Link>
            </Button>
          }
        />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Synthetic Generation"
        description={`${seeds.length} seeds available for generation`}
        actions={
          <div className="flex items-center gap-2">
            {generating && (
              <Button variant="outline" size="sm" onClick={handleCancel}>
                <StopCircle className="mr-1.5 size-4" /> Cancel
              </Button>
            )}
            <Button
              size="sm"
              onClick={handleGenerate}
              disabled={generating || selectedCount === 0}
            >
              {generating ? (
                <Loader2 className="mr-1.5 size-4 animate-spin" />
              ) : (
                <Zap className="mr-1.5 size-4" />
              )}
              {generating
                ? 'Generating...'
                : selectedCount > 0
                  ? `Generate ${totalToGenerate} Conversations`
                  : 'Select Seeds to Generate'}
            </Button>
          </div>
        }
      />

      {/* Info banner */}
      <Card className="bg-muted/40">
        <CardContent className="flex items-start gap-3 p-4">
          <Info className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
          <div className="space-y-1 text-xs text-muted-foreground">
            <p className="text-[15px] font-semibold text-foreground">How Synthetic Generation Works</p>
            <p>
              Select one or more seeds and configure generation parameters. The SCSF engine uses your seed&apos;s
              domain context, role definitions, and conversation flow to generate realistic synthetic conversations
              via LLM. Each generated conversation is optionally evaluated against 6 quality metrics to ensure
              it meets the required thresholds.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Progress bar during generation */}
      {generating && (
        <Card>
          <CardContent className="p-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">Generating conversations...</span>
                <span className="text-muted-foreground">{progress}%</span>
              </div>
              <Progress value={progress} />
              <p className="text-xs text-muted-foreground">
                Processing {selectedCount} seed{selectedCount !== 1 ? 's' : ''} x {conversationsPerSeed} conversation{conversationsPerSeed !== 1 ? 's' : ''} each
                {!demoMode && ' (API mode)'}
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error display */}
      {generationError && (
        <Card className="bg-muted/40">
          <CardContent className="flex items-center gap-3 p-3">
            <AlertTriangle className="size-4 shrink-0 text-muted-foreground" />
            <p className="flex-1 text-xs text-muted-foreground">{generationError}</p>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 text-xs"
              onClick={() => setGenerationError(null)}
            >
              <X className="size-3" />
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Success banner */}
      {lastRunCount !== null && !generating && (
        <Card className="border-l-4 border-l-foreground/20">
          <CardContent className="flex items-center justify-between p-4">
            <div>
              <p className="text-sm font-semibold">
                Successfully generated {lastRunCount} conversation{lastRunCount !== 1 ? 's' : ''}
              </p>
              <p className="text-xs text-muted-foreground">
                Conversations have been saved to the local store.
              </p>
            </div>
            <Button asChild size="sm" variant="outline">
              <Link href="/dashboard/conversations">
                View Conversations
              </Link>
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Quality evaluation results */}
      {qualityResults && !generating && (
        <Card className="border-l-4 border-l-foreground/20">
          <CardContent className="p-4">
            <p className="mb-2 text-sm font-semibold">Quality Evaluation Results</p>
            <div className="grid grid-cols-3 gap-2 text-center sm:gap-4">
              <div>
                <p className="text-lg font-bold">{qualityResults.total}</p>
                <p className="text-[10px] text-muted-foreground">Evaluated</p>
              </div>
              <div>
                <p className="text-lg font-bold">
                  {qualityResults.passed}
                </p>
                <p className="text-[10px] text-muted-foreground">Passed</p>
              </div>
              <div>
                <p className="text-lg font-bold">
                  {qualityResults.avgScore?.toFixed(3) ?? 'N/A'}
                </p>
                <p className="text-[10px] text-muted-foreground">Avg Score</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 lg:grid-cols-3">
        {/* Seed selection */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium">Select Seeds</CardTitle>
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={selectAll}>
                    Select All
                  </Button>
                  {selectedCount > 0 && (
                    <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={clearSelection}>
                      Clear ({selectedCount})
                    </Button>
                  )}
                </div>
              </div>
              <CardDescription className="text-xs">
                Pick one or more seeds to generate synthetic conversations from.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="max-h-[280px] space-y-1.5 overflow-y-auto sm:max-h-[400px]">
                {seeds.map(seed => (
                  <label
                    key={seed.seed_id}
                    className={cn(
                      'flex cursor-pointer items-start gap-3 rounded-md border px-3 py-2.5 transition-colors hover:bg-muted',
                      selected.has(seed.seed_id) && 'border-primary bg-primary/5'
                    )}
                  >
                    <Checkbox
                      checked={selected.has(seed.seed_id)}
                      onCheckedChange={() => toggleSeed(seed.seed_id)}
                      className="mt-0.5"
                    />
                    <div className="flex-1 overflow-hidden">
                      <div className="flex items-center gap-2">
                        <span className="truncate font-mono text-xs font-medium">
                          {(seed.seed_id ?? '').slice(0, 16)}...
                        </span>
                        <Badge
                          variant="secondary"
                          className={cn('shrink-0 text-[10px]', DOMAIN_COLORS[seed.dominio])}
                        >
                          {(seed.dominio ?? '').split('.').pop()}
                        </Badge>
                        <Badge variant="outline" className="shrink-0 text-[10px]">
                          {seed.idioma}
                        </Badge>
                      </div>
                      <p className="mt-0.5 truncate text-xs text-muted-foreground">
                        {seed.objetivo}
                      </p>
                      <div className="mt-1 flex items-center gap-2 text-[10px] text-muted-foreground">
                        <span>{(seed.roles ?? []).join(', ')}</span>
                        <span>|</span>
                        <span>{seed.pasos_turnos?.turnos_min ?? 0}-{seed.pasos_turnos?.turnos_max ?? 0} turns</span>
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Generation config */}
        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Generation Config</CardTitle>
              <CardDescription className="text-xs">
                Configure parameters for synthetic conversation generation.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              {/* API Status & Demo Mode */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Label className="flex items-center gap-1 text-xs">
                    Demo Mode
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <HelpCircle className="size-3 text-muted-foreground" />
                        </TooltipTrigger>
                        <TooltipContent side="left" className="max-w-xs text-xs">
                          In demo mode, conversations are generated locally with placeholder content.
                          When connected to the API, real LLM-powered generation is used.
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </Label>
                  <Switch checked={demoMode} onCheckedChange={setDemoMode} />
                </div>
                <Badge variant="outline" className="gap-1 text-[10px]">
                  {apiAvailable ? (
                    <>
                      <Cloud className="size-3" /> API Connected
                    </>
                  ) : (
                    <>
                      <CloudOff className="size-3" /> API Unavailable
                    </>
                  )}
                </Badge>
              </div>

              {/* Evaluate After toggle (API mode only) */}
              {!demoMode && (
                <div className="flex items-center justify-between">
                  <Label className="flex items-center gap-1 text-xs">
                    Evaluate After
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <HelpCircle className="size-3 text-muted-foreground" />
                        </TooltipTrigger>
                        <TooltipContent side="left" className="max-w-xs text-xs">
                          Automatically run quality evaluation on each generated conversation.
                          Checks ROUGE-L, factual fidelity, lexical diversity, coherence, privacy,
                          and memorization.
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </Label>
                  <Switch checked={evaluateAfter} onCheckedChange={setEvaluateAfter} />
                </div>
              )}

              {/* Conversations per seed */}
              <div className="space-y-2">
                <Label className="text-xs">Conversations per Seed</Label>
                <Input
                  type="number"
                  min={1}
                  max={50}
                  value={conversationsPerSeed}
                  onChange={e => {
                    const v = Math.max(1, Math.min(50, Number(e.target.value) || 1))

                    setConversationsPerSeed(v)
                  }}
                />
                <p className="text-[10px] text-muted-foreground">
                  Range: 1-50. Will generate {totalToGenerate > 0 ? totalToGenerate : '...'} total.
                </p>
              </div>

              {/* Temperature */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label className="flex items-center gap-1 text-xs">
                    Temperature
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <HelpCircle className="size-3 text-muted-foreground" />
                        </TooltipTrigger>
                        <TooltipContent side="left" className="max-w-xs text-xs">
                          Controls randomness in LLM output. Lower values (0.0-0.3) produce more
                          deterministic, consistent conversations. Higher values (0.7-1.5) increase
                          creativity and diversity. Default 0.7 is recommended for balanced output.
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </Label>
                  <span className="text-xs font-medium">{temperature.toFixed(1)}</span>
                </div>
                <Slider
                  value={[temperature]}
                  onValueChange={([v]) => setTemperature(Math.round(v * 10) / 10)}
                  min={0}
                  max={2}
                  step={0.1}
                />
                <div className="flex justify-between text-[10px] text-muted-foreground">
                  <span>0.0 (deterministic)</span>
                  <span>2.0 (creative)</span>
                </div>
              </div>

              {/* Language override */}
              <div className="space-y-2">
                <Label className="flex items-center gap-1 text-xs">
                  Language Override
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <HelpCircle className="size-3 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent side="left" className="max-w-xs text-xs">
                        Override the seed&apos;s default language for all generated conversations.
                        Useful for generating multilingual datasets from the same seed.
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </Label>
                <Select value={languageOverride || '__default'} onValueChange={v => setLanguageOverride(v === '__default' ? '' : v)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Use seed default" />
                  </SelectTrigger>
                  <SelectContent>
                    {LANGUAGES.map(lang => (
                      <SelectItem key={lang.value || '__default'} value={lang.value || '__default'}>
                        {lang.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Summary */}
              {selectedCount > 0 && (
                <div className="rounded-md border bg-muted/50 p-3">
                  <p className="text-xs font-medium">Generation Summary</p>
                  <ul className="mt-1 space-y-0.5 text-[11px] text-muted-foreground">
                    <li>Seeds selected: <strong className="text-foreground">{selectedCount}</strong></li>
                    <li>Conversations per seed: <strong className="text-foreground">{conversationsPerSeed}</strong></li>
                    <li>Total to generate: <strong className="text-foreground">{totalToGenerate}</strong></li>
                    <li>Temperature: <strong className="text-foreground">{temperature.toFixed(1)}</strong></li>
                    <li>Language: <strong className="text-foreground">{languageOverride || 'seed default'}</strong></li>
                    <li>Mode: <strong className="text-foreground">{demoMode ? 'Demo' : 'API'}</strong></li>
                    {!demoMode && (
                      <li>Evaluate: <strong className="text-foreground">{evaluateAfter ? 'Yes' : 'No'}</strong></li>
                    )}
                    <li>
                      Est. time:{' '}
                      <strong className="text-foreground">
                        {demoMode ? '< 5s' : `~${Math.ceil(selectedCount * conversationsPerSeed * 8)}s`}
                      </strong>
                    </li>
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Generation History */}
      {history.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <History className="size-4 text-muted-foreground" />
              <CardTitle className="text-sm font-medium">Generation History</CardTitle>
            </div>
            <CardDescription className="text-xs">
              Past generation runs stored locally.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {history.map(run => (
                <div
                  key={run.id}
                  className="flex items-center justify-between rounded-md border px-3 py-2"
                >
                  <div className="flex items-center gap-3">
                    <Clock className="size-3.5 text-muted-foreground" />
                    <div>
                      <p className="text-xs font-medium">
                        {run.conversation_count} conversation{run.conversation_count !== 1 ? 's' : ''} from{' '}
                        {run.seed_count} seed{run.seed_count !== 1 ? 's' : ''}
                      </p>
                      <p className="text-[10px] text-muted-foreground">
                        {new Date(run.timestamp).toLocaleString()} | temp: {run.temperature} | lang: {run.language_override || 'default'}
                      </p>
                    </div>
                  </div>
                  <Badge variant="outline" className="text-[10px]">
                    {run.mode === 'api' ? 'API' : 'Demo'} | {run.conversations_per_seed}/seed
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
