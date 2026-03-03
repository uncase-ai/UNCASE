'use client'

import { useCallback, useRef, useState } from 'react'

import { ArrowLeft, Globe, Loader2, MessageSquare, PanelRightClose, PanelRightOpen, Sparkles } from 'lucide-react'
import Link from 'next/link'

import type { ChatMessage, ExtractionProgress } from '@/types/layer0'
import { checkApiHealth } from '@/lib/api/client'
import { endSession, sendTurn, startExtraction } from '@/lib/api/layer0'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

import { ChatContainer } from '../chat/chat-container'
import { ChatInput } from '../chat/chat-input'
import { ExtractionProgressPanel } from '../chat/extraction-progress'
import { TypingIndicator } from '../chat/typing-indicator'
import { PageHeader } from '../page-header'

type SessionState = 'idle' | 'active' | 'processing' | 'complete'

// ─── Demo interview script ───
// Pre-built questions and field extraction for when no backend is running.

interface DemoStep {
  question: string
  fields: Record<string, { status: 'extracted' | 'confirmed'; confidence: number; is_required: boolean }>
}

const DEMO_SCRIPTS: Record<string, Record<string, DemoStep[]>> = {
  automotive: {
    en: [
      {
        question: "Welcome! I'll help you create a conversation seed for the automotive industry. Let's start — what type of automotive interaction do you want to model? (e.g., new vehicle sales, test drive scheduling, financing consultation, service appointment)",
        fields: {},
      },
      {
        question: "Great choice. Now, who are the participants in this conversation? Please describe the two main roles (e.g., \"customer looking for a family SUV\" and \"certified sales advisor with inventory access\").",
        fields: { dominio: { status: 'confirmed', confidence: 0.95, is_required: true } },
      },
      {
        question: "What is the main objective of this conversation? What should the interaction accomplish from start to finish?",
        fields: {
          dominio: { status: 'confirmed', confidence: 0.95, is_required: true },
          roles: { status: 'extracted', confidence: 0.90, is_required: true },
          descripcion_roles: { status: 'extracted', confidence: 0.85, is_required: true },
        },
      },
      {
        question: "What tone should the conversation have? (e.g., professional-friendly, professional-consultative, professional-efficient). Also, how many turns should it typically take (min and max)?",
        fields: {
          dominio: { status: 'confirmed', confidence: 0.95, is_required: true },
          roles: { status: 'confirmed', confidence: 0.95, is_required: true },
          descripcion_roles: { status: 'confirmed', confidence: 0.92, is_required: true },
          objetivo: { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "What are the key constraints or rules the assistant must follow? (e.g., \"only mention vehicles from current inventory\", \"prices must include tax\", \"no unauthorized discounts\")",
        fields: {
          dominio: { status: 'confirmed', confidence: 0.95, is_required: true },
          roles: { status: 'confirmed', confidence: 0.95, is_required: true },
          descripcion_roles: { status: 'confirmed', confidence: 0.92, is_required: true },
          objetivo: { status: 'confirmed', confidence: 0.93, is_required: true },
          tono: { status: 'extracted', confidence: 0.90, is_required: true },
          pasos_turnos: { status: 'extracted', confidence: 0.85, is_required: true },
        },
      },
      {
        question: "Describe the expected conversation flow — what steps should the dialogue follow from beginning to end? (e.g., greeting → needs assessment → presentation → comparison → quote → next steps)",
        fields: {
          dominio: { status: 'confirmed', confidence: 0.95, is_required: true },
          roles: { status: 'confirmed', confidence: 0.95, is_required: true },
          descripcion_roles: { status: 'confirmed', confidence: 0.92, is_required: true },
          objetivo: { status: 'confirmed', confidence: 0.93, is_required: true },
          tono: { status: 'confirmed', confidence: 0.92, is_required: true },
          pasos_turnos: { status: 'confirmed', confidence: 0.90, is_required: true },
          restricciones: { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
    ],
    es: [
      {
        question: "Bienvenido! Te ayudaré a crear un seed de conversación para la industria automotriz. Comencemos — ¿qué tipo de interacción automotriz quieres modelar? (ej: venta de vehículo nuevo, prueba de manejo, consulta de financiamiento, cita de servicio)",
        fields: {},
      },
      {
        question: "Excelente elección. Ahora, ¿quiénes son los participantes en esta conversación? Describe los dos roles principales (ej: \"cliente buscando un SUV familiar\" y \"asesor de ventas certificado con acceso al inventario\").",
        fields: { dominio: { status: 'confirmed', confidence: 0.95, is_required: true } },
      },
      {
        question: "¿Cuál es el objetivo principal de esta conversación? ¿Qué debe lograr la interacción de inicio a fin?",
        fields: {
          dominio: { status: 'confirmed', confidence: 0.95, is_required: true },
          roles: { status: 'extracted', confidence: 0.90, is_required: true },
          descripcion_roles: { status: 'extracted', confidence: 0.85, is_required: true },
        },
      },
      {
        question: "¿Qué tono debe tener la conversación? (ej: profesional-amigable, profesional-consultivo). También, ¿cuántos turnos debería tener típicamente (mínimo y máximo)?",
        fields: {
          dominio: { status: 'confirmed', confidence: 0.95, is_required: true },
          roles: { status: 'confirmed', confidence: 0.95, is_required: true },
          descripcion_roles: { status: 'confirmed', confidence: 0.92, is_required: true },
          objetivo: { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "¿Cuáles son las restricciones o reglas clave que debe seguir el asistente? (ej: \"solo mencionar vehículos del inventario actual\", \"precios deben incluir IVA\")",
        fields: {
          dominio: { status: 'confirmed', confidence: 0.95, is_required: true },
          roles: { status: 'confirmed', confidence: 0.95, is_required: true },
          descripcion_roles: { status: 'confirmed', confidence: 0.92, is_required: true },
          objetivo: { status: 'confirmed', confidence: 0.93, is_required: true },
          tono: { status: 'extracted', confidence: 0.90, is_required: true },
          pasos_turnos: { status: 'extracted', confidence: 0.85, is_required: true },
        },
      },
      {
        question: "Describe el flujo esperado de la conversación — ¿qué pasos debe seguir el diálogo de principio a fin? (ej: saludo → detección de necesidad → presentación → comparativa → cotización → siguiente paso)",
        fields: {
          dominio: { status: 'confirmed', confidence: 0.95, is_required: true },
          roles: { status: 'confirmed', confidence: 0.95, is_required: true },
          descripcion_roles: { status: 'confirmed', confidence: 0.92, is_required: true },
          objetivo: { status: 'confirmed', confidence: 0.93, is_required: true },
          tono: { status: 'confirmed', confidence: 0.92, is_required: true },
          pasos_turnos: { status: 'confirmed', confidence: 0.90, is_required: true },
          restricciones: { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
    ],
  },
  medical: {
    en: [
      {
        question: "Welcome! I'll help you create a conversation seed for medical consultations. What type of medical interaction do you want to model? (e.g., initial cardiology evaluation, pediatric wellness visit, mental health intake, follow-up consultation)",
        fields: {},
      },
      {
        question: "Who are the participants? Please describe the patient profile and the healthcare provider role (e.g., \"adult patient with chest pain\" and \"board-certified cardiologist\").",
        fields: { dominio: { status: 'confirmed', confidence: 0.95, is_required: true } },
      },
      {
        question: "What is the primary clinical objective? What should the consultation accomplish?",
        fields: {
          dominio: { status: 'confirmed', confidence: 0.95, is_required: true },
          roles: { status: 'extracted', confidence: 0.90, is_required: true },
          descripcion_roles: { status: 'extracted', confidence: 0.85, is_required: true },
        },
      },
      {
        question: "What tone should the consultation have? And how many turns should it typically take?",
        fields: {
          dominio: { status: 'confirmed', confidence: 0.95, is_required: true },
          roles: { status: 'confirmed', confidence: 0.95, is_required: true },
          descripcion_roles: { status: 'confirmed', confidence: 0.92, is_required: true },
          objetivo: { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "What clinical constraints must be followed? (e.g., \"review complete medical history before recommendations\", \"allergy verification required\", \"emergency symptoms require escalation\")",
        fields: {
          dominio: { status: 'confirmed', confidence: 0.95, is_required: true },
          roles: { status: 'confirmed', confidence: 0.95, is_required: true },
          descripcion_roles: { status: 'confirmed', confidence: 0.92, is_required: true },
          objetivo: { status: 'confirmed', confidence: 0.93, is_required: true },
          tono: { status: 'extracted', confidence: 0.90, is_required: true },
          pasos_turnos: { status: 'extracted', confidence: 0.85, is_required: true },
        },
      },
      {
        question: "Describe the expected clinical flow — what steps should the consultation follow? (e.g., chief complaint → history review → exam findings → diagnostic plan → patient education → follow-up)",
        fields: {
          dominio: { status: 'confirmed', confidence: 0.95, is_required: true },
          roles: { status: 'confirmed', confidence: 0.95, is_required: true },
          descripcion_roles: { status: 'confirmed', confidence: 0.92, is_required: true },
          objetivo: { status: 'confirmed', confidence: 0.93, is_required: true },
          tono: { status: 'confirmed', confidence: 0.92, is_required: true },
          pasos_turnos: { status: 'confirmed', confidence: 0.90, is_required: true },
          restricciones: { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
    ],
    es: [
      {
        question: "Bienvenido! Te ayudaré a crear un seed para consultas médicas. ¿Qué tipo de consulta deseas modelar? (ej: evaluación cardiológica, consulta pediátrica, evaluación de salud mental)",
        fields: {},
      },
      {
        question: "¿Quiénes son los participantes? Describe el perfil del paciente y el rol del profesional de salud.",
        fields: { dominio: { status: 'confirmed', confidence: 0.95, is_required: true } },
      },
      {
        question: "¿Cuál es el objetivo clínico principal de esta consulta?",
        fields: {
          dominio: { status: 'confirmed', confidence: 0.95, is_required: true },
          roles: { status: 'extracted', confidence: 0.90, is_required: true },
          descripcion_roles: { status: 'extracted', confidence: 0.85, is_required: true },
        },
      },
      {
        question: "¿Qué tono debe tener la consulta? ¿Y cuántos turnos debería tener?",
        fields: {
          dominio: { status: 'confirmed', confidence: 0.95, is_required: true },
          roles: { status: 'confirmed', confidence: 0.95, is_required: true },
          descripcion_roles: { status: 'confirmed', confidence: 0.92, is_required: true },
          objetivo: { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "¿Qué restricciones clínicas deben seguirse? (ej: \"revisar historial completo\", \"verificar alergias\", \"protocolo de emergencia\")",
        fields: {
          dominio: { status: 'confirmed', confidence: 0.95, is_required: true },
          roles: { status: 'confirmed', confidence: 0.95, is_required: true },
          descripcion_roles: { status: 'confirmed', confidence: 0.92, is_required: true },
          objetivo: { status: 'confirmed', confidence: 0.93, is_required: true },
          tono: { status: 'extracted', confidence: 0.90, is_required: true },
          pasos_turnos: { status: 'extracted', confidence: 0.85, is_required: true },
        },
      },
      {
        question: "Describe el flujo clínico esperado — ¿qué pasos debe seguir la consulta? (ej: motivo de consulta → revisión de historial → hallazgos → plan diagnóstico → educación al paciente → seguimiento)",
        fields: {
          dominio: { status: 'confirmed', confidence: 0.95, is_required: true },
          roles: { status: 'confirmed', confidence: 0.95, is_required: true },
          descripcion_roles: { status: 'confirmed', confidence: 0.92, is_required: true },
          objetivo: { status: 'confirmed', confidence: 0.93, is_required: true },
          tono: { status: 'confirmed', confidence: 0.92, is_required: true },
          pasos_turnos: { status: 'confirmed', confidence: 0.90, is_required: true },
          restricciones: { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
    ],
  },
}

function buildDemoProgress(step: number, totalSteps: number, fields: Record<string, { status: string; confidence: number; is_required: boolean }>): ExtractionProgress {
  const fieldEntries = Object.entries(fields)
  const allFieldNames = ['dominio', 'roles', 'descripcion_roles', 'objetivo', 'tono', 'pasos_turnos', 'restricciones', 'flujo_esperado', 'contexto', 'herramientas']
  const progressFields: ExtractionProgress['fields'] = {}

  for (const name of allFieldNames) {
    const existing = fields[name]
    progressFields[name] = existing
      ? { status: existing.status as 'extracted' | 'confirmed', confidence: existing.confidence, is_required: existing.is_required }
      : { status: 'empty', confidence: 0, is_required: name === 'dominio' || name === 'roles' || name === 'objetivo' }
  }

  const filled = fieldEntries.length
  const requiredFilled = fieldEntries.filter(([, v]) => v.is_required).length
  const requiredTotal = allFieldNames.filter(n => n === 'dominio' || n === 'roles' || n === 'descripcion_roles' || n === 'objetivo' || n === 'tono' || n === 'pasos_turnos' || n === 'restricciones').length

  return {
    turn: step,
    max_turns: totalSteps + 1,
    total_fields: allFieldNames.length,
    filled_fields: filled,
    required_total: requiredTotal,
    required_filled: requiredFilled,
    is_complete: step >= totalSteps,
    fields: progressFields,
  }
}

export function SeedExtractPage() {
  const [sessionState, setSessionState] = useState<SessionState>('idle')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [progress, setProgress] = useState<ExtractionProgress | null>(null)
  const [seed, setSeed] = useState<Record<string, unknown> | null>(null)
  const [industry, setIndustry] = useState('automotive')
  const [locale, setLocale] = useState('en')
  const [error, setError] = useState<string | null>(null)
  const [showSidebar, setShowSidebar] = useState(true)
  const [starting, setStarting] = useState(false)
  const [demoMode, setDemoMode] = useState(false)
  const demoStepRef = useRef(0)

  const addMessage = useCallback((role: ChatMessage['role'], content: string, msgProgress?: ExtractionProgress) => {
    setMessages(prev => [
      ...prev,
      {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        role,
        content,
        timestamp: new Date(),
        progress: msgProgress,
      },
    ])
  }, [])

  const handleStart = useCallback(async () => {
    setStarting(true)
    setError(null)
    setMessages([])
    setProgress(null)
    setSeed(null)
    setDemoMode(false)
    demoStepRef.current = 0

    // Check if API is available first
    const apiOk = await checkApiHealth()

    if (apiOk) {
      // Real API mode
      const { data, error: apiError } = await startExtraction({ industry, locale })

      if (apiError || !data) {
        setError(apiError?.message ?? 'Failed to start session')
        setStarting(false)
        return
      }

      setSessionId(data.session_id)
      setProgress(data.message.progress ?? null)
      addMessage('assistant', data.message.content, data.message.progress)
      setSessionState('active')
      setStarting(false)
      return
    }

    // Demo mode — simulate the interview
    setDemoMode(true)
    const script = DEMO_SCRIPTS[industry]?.[locale] ?? DEMO_SCRIPTS.automotive.en
    const step = script[0]
    const demoProgress = buildDemoProgress(0, script.length, step.fields)

    setSessionId(`demo-${Date.now()}`)
    setProgress(demoProgress)
    addMessage('assistant', step.question, demoProgress)
    demoStepRef.current = 1
    setSessionState('active')
    setStarting(false)
  }, [industry, locale, addMessage])

  const handleSend = useCallback(async (text: string) => {
    if (!sessionId || sessionState !== 'active') return

    addMessage('user', text)
    setSessionState('processing')

    // ─── Demo mode ───
    if (demoMode) {
      await new Promise(r => setTimeout(r, 800 + Math.random() * 700))

      const script = DEMO_SCRIPTS[industry]?.[locale] ?? DEMO_SCRIPTS.automotive.en
      const stepIdx = demoStepRef.current

      if (stepIdx >= script.length) {
        // Extraction complete — build the seed
        const demoSeed = {
          version: '1.0',
          dominio: industry === 'medical' ? 'medical.consultation' : 'automotive.sales',
          idioma: locale,
          etiquetas: ['demo-extracted', industry],
          roles: industry === 'medical' ? ['patient', 'physician'] : ['customer', 'sales_advisor'],
          descripcion_roles: industry === 'medical'
            ? { patient: 'Patient seeking consultation', physician: 'Board-certified specialist' }
            : { customer: 'Customer exploring vehicle options', sales_advisor: 'Certified sales advisor' },
          objetivo: `AI-extracted seed for ${industry} conversation`,
          tono: 'professional-friendly',
          pasos_turnos: { turnos_min: 4, turnos_max: 8, flujo_esperado: ['Greeting', 'Assessment', 'Recommendation', 'Follow-up'] },
          parametros_factuales: {
            contexto: `${industry} domain conversation`,
            restricciones: ['Follow domain best practices', 'Maintain professional tone'],
            herramientas: [],
            metadata: { extracted_by: 'demo-interview' },
          },
          privacidad: { pii_eliminado: true, metodo_anonimizacion: 'presidio_v2', nivel_confianza: 0.99, campos_sensibles_detectados: [] },
          metricas_calidad: { rouge_l_min: 0.65, fidelidad_min: 0.85, diversidad_lexica_min: 0.55, coherencia_dialogica_min: 0.80 },
        }

        const summaryMsg = locale === 'es'
          ? 'Extracción completada. He recopilado todos los parámetros necesarios para tu seed de conversación. Puedes revisarlo y crearlo.'
          : 'Extraction complete! I\'ve gathered all the parameters needed for your conversation seed. You can review and create it.'

        const finalProgress = buildDemoProgress(script.length, script.length, script[script.length - 1].fields)
        setProgress(finalProgress)
        addMessage('system', summaryMsg, finalProgress)
        setSeed(demoSeed)
        setSessionState('complete')
        return
      }

      const step = script[stepIdx]
      const demoProgress = buildDemoProgress(stepIdx, script.length, step.fields)

      setProgress(demoProgress)
      addMessage('assistant', step.question, demoProgress)
      demoStepRef.current = stepIdx + 1
      setSessionState('active')
      return
    }

    // ─── API mode ───
    const { data, error: apiError } = await sendTurn({
      session_id: sessionId,
      user_message: text,
    })

    if (apiError || !data) {
      setError(apiError?.message ?? 'Failed to process turn')
      setSessionState('active')
      return
    }

    setProgress(data.message.progress ?? null)
    addMessage(
      data.message.type === 'summary' ? 'system' : 'assistant',
      data.message.content,
      data.message.progress,
    )

    if (data.is_complete) {
      setSessionState('complete')
      if (data.message.seed) {
        setSeed(data.message.seed as Record<string, unknown>)
      }
    } else {
      setSessionState('active')
    }
  }, [sessionId, sessionState, demoMode, industry, locale, addMessage])

  const handleEndSession = useCallback(async () => {
    if (sessionId && !demoMode) {
      await endSession(sessionId)
    }
    setSessionState('idle')
    setSessionId(null)
    setDemoMode(false)
    demoStepRef.current = 0
  }, [sessionId, demoMode])

  const handleCreateSeed = useCallback(() => {
    if (!seed) return
    const existing = JSON.parse(localStorage.getItem('uncase-seeds') ?? '[]')
    const newSeed = {
      ...seed,
      seed_id: `seed-${Date.now()}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    localStorage.setItem('uncase-seeds', JSON.stringify([newSeed, ...existing]))
    window.location.href = '/dashboard/pipeline/seeds'
  }, [seed])

  const turnsLeft = progress ? progress.max_turns - progress.turn : 0

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col">
      <PageHeader
        title="AI Interview — Seed Extraction"
        description={sessionState === 'idle' ? 'Start an AI-guided interview to create a conversation seed' : `Active session · ${industry} · ${locale.toUpperCase()}${demoMode ? ' · Demo' : ''}`}
        actions={
          <div className="flex items-center gap-2">
            {sessionState !== 'idle' && (
              <Button variant="outline" size="sm" onClick={() => setShowSidebar(!showSidebar)}>
                {showSidebar ? <PanelRightClose className="size-4" /> : <PanelRightOpen className="size-4" />}
              </Button>
            )}
            <Button variant="outline" size="sm" asChild>
              <Link href="/dashboard/pipeline/seeds">
                <ArrowLeft className="mr-1 size-3" /> Seeds
              </Link>
            </Button>
          </div>
        }
      />

      {/* Error banner */}
      {error && (
        <div className="mx-4 mb-2 rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-xs text-red-700 dark:border-red-800 dark:bg-red-950/20 dark:text-red-300">
          {error}
          <button onClick={() => setError(null)} className="ml-2 underline">Dismiss</button>
        </div>
      )}

      {/* Pre-session: industry + language selector */}
      {sessionState === 'idle' && (
        <div className="flex flex-1 items-center justify-center">
          <div className="mx-auto w-full max-w-md space-y-6 rounded-xl border bg-card p-8 shadow-sm">
            <div className="text-center">
              <MessageSquare className="mx-auto mb-3 size-12 text-primary" />
              <h2 className="text-lg font-semibold">Extraction Interview</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                The AI will guide you through questions to extract all the parameters needed to create a conversation seed.
              </p>
            </div>

            <div className="space-y-3">
              <div className="space-y-1">
                <label className="text-xs font-medium">Industry</label>
                <Select value={industry} onValueChange={setIndustry}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="automotive">Automotive</SelectItem>
                    <SelectItem value="medical">Medical</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-1">
                <label className="flex items-center gap-1.5 text-xs font-medium">
                  <Globe className="size-3" /> Language
                </label>
                <Select value={locale} onValueChange={setLocale}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="es">Spanish</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button onClick={handleStart} className="w-full gap-2" disabled={starting}>
                {starting ? (
                  <><Loader2 className="size-4 animate-spin" /> Starting...</>
                ) : (
                  <><Sparkles className="size-4" /> Start Interview</>
                )}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Active session: chat + sidebar */}
      {sessionState !== 'idle' && (
        <div className="flex min-h-0 flex-1">
          {/* Chat area */}
          <div className="flex min-w-0 flex-1 flex-col">
            <ChatContainer messages={messages} />

            {sessionState === 'processing' && <TypingIndicator />}

            {/* Turn warning */}
            {progress && turnsLeft <= 2 && turnsLeft > 0 && sessionState !== 'complete' && (
              <div className="bg-amber-50 px-4 py-1.5 text-center text-xs text-amber-700 dark:bg-amber-950/30 dark:text-amber-300">
                {turnsLeft} turn{turnsLeft !== 1 ? 's' : ''} remaining
              </div>
            )}

            {/* Input or completion actions */}
            {sessionState === 'complete' ? (
              <div className="flex items-center gap-3 border-t bg-emerald-50 p-4 dark:border-zinc-700 dark:bg-emerald-950/20">
                <Sparkles className="size-5 text-emerald-600" />
                <span className="flex-1 text-sm font-medium text-emerald-800 dark:text-emerald-200">
                  Extraction complete
                </span>
                <Button variant="outline" size="sm" onClick={handleEndSession}>
                  New Interview
                </Button>
                {seed && (
                  <Button size="sm" onClick={handleCreateSeed} className="gap-1.5">
                    <Sparkles className="size-3" /> Create Seed
                  </Button>
                )}
              </div>
            ) : (
              <ChatInput
                onSend={handleSend}
                disabled={sessionState !== 'active'}
                placeholder={sessionState === 'processing' ? 'Processing...' : 'Type your response...'}
              />
            )}
          </div>

          {/* Progress sidebar */}
          {showSidebar && (
            <div className="hidden w-80 shrink-0 border-l bg-card lg:block dark:border-zinc-800">
              <div className="border-b px-3 py-2 dark:border-zinc-800">
                <h3 className="text-xs font-semibold">Extraction Progress</h3>
              </div>
              <ExtractionProgressPanel progress={progress} />
            </div>
          )}
        </div>
      )}
    </div>
  )
}
