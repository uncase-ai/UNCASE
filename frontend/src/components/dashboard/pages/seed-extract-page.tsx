'use client'

import { useCallback, useRef, useState } from 'react'

import { ArrowLeft, Globe, Info, Loader2, MessageSquare, PanelRightClose, PanelRightOpen, Sparkles } from 'lucide-react'
import Link from 'next/link'

import type { ChatMessage, ExtractionProgress } from '@/types/layer0'
import { checkApiHealthDetailed } from '@/lib/api/client'
import { createSeedApi } from '@/lib/api/seeds'
import { endSession, sendTurn, startExtraction } from '@/lib/api/layer0'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

import { ChatContainer } from '../chat/chat-container'
import { ChatInput } from '../chat/chat-input'
import { ExtractionProgressPanel } from '../chat/extraction-progress'
import { TypingIndicator } from '../chat/typing-indicator'
import { PageHeader } from '../page-header'

type SessionState = 'idle' | 'active' | 'processing' | 'complete'

// ─── i18n strings ───

const t = {
  en: {
    pageTitle: 'AI Interview — Seed Extraction',
    pageDescIdle: 'Start an AI-guided interview to create a conversation seed',
    heading: 'Extraction Interview',
    headingDesc: 'The AI will guide you through questions to extract all the parameters needed to create a conversation seed.',
    alertTitle: 'API connection required',
    alertDesc1: 'The AI Interview requires a running UNCASE API with an LLM configured.',
    alertDemo: 'A scripted demo will run if no API is detected.',
    alertManual: 'create a seed manually',
    alertBrowse: 'existing seeds',
    alertAlso: 'You can also',
    alertOr: 'or browse',
    industryLabel: 'Industry',
    automotive: 'Automotive',
    medical: 'Medical',
    languageLabel: 'Language',
    english: 'English',
    spanish: 'Spanish',
    starting: 'Starting...',
    startInterview: 'Start Interview',
    dismiss: 'Dismiss',
    turnsRemaining: (n: number) => `${n} turn${n !== 1 ? 's' : ''} remaining`,
    extractionComplete: 'Extraction complete',
    newInterview: 'New Interview',
    createSeed: 'Create Seed',
    processing: 'Processing...',
    typePlaceholder: 'Type your response...',
    progressTitle: 'Extraction Progress',
  },
  es: {
    pageTitle: 'Entrevista IA — Extracción de Seed',
    pageDescIdle: 'Inicia una entrevista guiada por IA para crear un seed de conversación',
    heading: 'Entrevista de Extracción',
    headingDesc: 'La IA te guiará con preguntas para extraer todos los parámetros necesarios para crear un seed de conversación.',
    alertTitle: 'Conexión a API requerida',
    alertDesc1: 'La entrevista IA requiere una API de UNCASE con un LLM configurado.',
    alertDemo: 'Se ejecutará un demo guionizado si no se detecta la API.',
    alertManual: 'crear un seed manualmente',
    alertBrowse: 'seeds existentes',
    alertAlso: 'También puedes',
    alertOr: 'o explorar',
    industryLabel: 'Industria',
    automotive: 'Automotriz',
    medical: 'Médica',
    languageLabel: 'Idioma',
    english: 'Inglés',
    spanish: 'Español',
    starting: 'Iniciando...',
    startInterview: 'Iniciar Entrevista',
    dismiss: 'Descartar',
    turnsRemaining: (n: number) => `${n} turno${n !== 1 ? 's' : ''} restante${n !== 1 ? 's' : ''}`,
    extractionComplete: 'Extracción completada',
    newInterview: 'Nueva Entrevista',
    createSeed: 'Crear Seed',
    processing: 'Procesando...',
    typePlaceholder: 'Escribe tu respuesta...',
    progressTitle: 'Progreso de Extracción',
  },
} as const

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
        question: "Hello! I'll help you design a synthetic conversation scenario for automotive sales. Together we'll define the parameters to generate realistic training conversations for AI fine-tuning. What type of sales scenario do you want to simulate? (e.g., new vehicle sale, used car inquiry, financing consultation, service follow-up)",
        fields: {},
      },
      {
        question: "Got it. Now, what kind of customer should we simulate? Describe their profile: are they a first-time buyer or experienced? What's their urgency level — just exploring, actively deciding, or urgent need?",
        fields: {
          'escenario.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
        },
      },
      {
        question: "What communication channel should this conversation happen on — in-person at the dealership, WhatsApp, phone call, or web chat? And what's the primary use for the vehicle — personal, family, work, or business?",
        fields: {
          'escenario.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.tipo_cliente': { status: 'extracted', confidence: 0.90, is_required: true },
          'cliente_perfil.nivel_experiencia_compra': { status: 'extracted', confidence: 0.90, is_required: true },
          'cliente_perfil.urgencia': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "What tone should the conversation have — formal, casual, technical, or empathetic? And how complex should the scenario be — simple (straightforward sale), medium (some objections), or complex (multiple rounds of negotiation)?",
        fields: {
          'escenario.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.tipo_cliente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.nivel_experiencia_compra': { status: 'confirmed', confidence: 0.92, is_required: true },
          'cliente_perfil.urgencia': { status: 'confirmed', confidence: 0.92, is_required: true },
          'contexto_conversacion.canal': { status: 'extracted', confidence: 0.90, is_required: true },
          'intencion.uso_principal': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "Should the conversation include customer objections (e.g., price concerns, trust issues)? Should it include price negotiation? What about comparisons with competing brands?",
        fields: {
          'escenario.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.tipo_cliente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.nivel_experiencia_compra': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.urgencia': { status: 'confirmed', confidence: 0.95, is_required: true },
          'contexto_conversacion.canal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'intencion.uso_principal': { status: 'confirmed', confidence: 0.92, is_required: true },
          'escenario.tono_esperado': { status: 'extracted', confidence: 0.90, is_required: true },
          'escenario.complejidad': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "Last question — any specific business rules or constraints the sales advisor must follow? (e.g., \"only offer current inventory\", \"prices must include tax\", \"maximum discount of 5%\")",
        fields: {
          'escenario.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.tipo_cliente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.nivel_experiencia_compra': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.urgencia': { status: 'confirmed', confidence: 0.95, is_required: true },
          'contexto_conversacion.canal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'intencion.uso_principal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'escenario.tono_esperado': { status: 'confirmed', confidence: 0.95, is_required: true },
          'escenario.complejidad': { status: 'confirmed', confidence: 0.95, is_required: true },
        },
      },
    ],
    es: [
      {
        question: "Hola! Te ayudaré a diseñar un escenario de conversación sintética para ventas automotrices. Juntos definiremos los parámetros para generar conversaciones de entrenamiento realistas. ¿Qué tipo de escenario de ventas quieres simular? (ej: venta de vehículo nuevo, consulta de seminuevo, financiamiento, seguimiento postventa)",
        fields: {},
      },
      {
        question: "Perfecto. ¿Qué tipo de cliente debemos simular? Describe su perfil: ¿es comprador primerizo o tiene experiencia? ¿Cuál es su nivel de urgencia — explorando, decidiendo, o necesidad urgente?",
        fields: {
          'escenario.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
        },
      },
      {
        question: "¿Por qué canal debería ocurrir esta conversación — presencial en la agencia, WhatsApp, teléfono, o chat web? ¿Y cuál es el uso principal del vehículo — personal, familia, trabajo, o negocio?",
        fields: {
          'escenario.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.tipo_cliente': { status: 'extracted', confidence: 0.90, is_required: true },
          'cliente_perfil.nivel_experiencia_compra': { status: 'extracted', confidence: 0.90, is_required: true },
          'cliente_perfil.urgencia': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "¿Qué tono debe tener la conversación — formal, casual, técnico, o empático? ¿Y qué tan complejo debe ser el escenario — simple (venta directa), medio (con objeciones), o complejo (múltiples rondas de negociación)?",
        fields: {
          'escenario.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.tipo_cliente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.nivel_experiencia_compra': { status: 'confirmed', confidence: 0.92, is_required: true },
          'cliente_perfil.urgencia': { status: 'confirmed', confidence: 0.92, is_required: true },
          'contexto_conversacion.canal': { status: 'extracted', confidence: 0.90, is_required: true },
          'intencion.uso_principal': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "¿Debe incluir la conversación objeciones del cliente (ej: dudas de precio, desconfianza)? ¿Debe incluir negociación de precios? ¿Y comparaciones con marcas de la competencia?",
        fields: {
          'escenario.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.tipo_cliente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.nivel_experiencia_compra': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.urgencia': { status: 'confirmed', confidence: 0.95, is_required: true },
          'contexto_conversacion.canal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'intencion.uso_principal': { status: 'confirmed', confidence: 0.92, is_required: true },
          'escenario.tono_esperado': { status: 'extracted', confidence: 0.90, is_required: true },
          'escenario.complejidad': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "Última pregunta — ¿hay reglas o restricciones específicas que el asesor de ventas deba seguir? (ej: \"solo ofrecer inventario actual\", \"precios con IVA incluido\", \"descuento máximo del 5%\")",
        fields: {
          'escenario.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.tipo_cliente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.nivel_experiencia_compra': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.urgencia': { status: 'confirmed', confidence: 0.95, is_required: true },
          'contexto_conversacion.canal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'intencion.uso_principal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'escenario.tono_esperado': { status: 'confirmed', confidence: 0.95, is_required: true },
          'escenario.complejidad': { status: 'confirmed', confidence: 0.95, is_required: true },
        },
      },
    ],
  },
  medical: {
    en: [
      {
        question: "Hello! I'll help you design a synthetic consultation scenario for medical training. We'll define all the parameters to generate realistic patient-provider conversations. What type of medical consultation do you want to simulate? (e.g., cardiology evaluation, pediatric visit, mental health intake, follow-up)",
        fields: {},
      },
      {
        question: "What patient profile should we simulate? Describe their condition, experience level with the healthcare system, and urgency (routine, moderately urgent, emergency).",
        fields: { 'escenario.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true } },
      },
      {
        question: "What's the communication channel — in-person, telemedicine, phone? And what's the primary clinical objective of this consultation?",
        fields: {
          'escenario.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.tipo_cliente': { status: 'extracted', confidence: 0.90, is_required: true },
          'cliente_perfil.nivel_experiencia_compra': { status: 'extracted', confidence: 0.90, is_required: true },
          'cliente_perfil.urgencia': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "What tone should the consultation have — formal-clinical, empathetic-supportive, or educational? How complex should the case be?",
        fields: {
          'escenario.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.tipo_cliente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.nivel_experiencia_compra': { status: 'confirmed', confidence: 0.92, is_required: true },
          'cliente_perfil.urgencia': { status: 'confirmed', confidence: 0.92, is_required: true },
          'contexto_conversacion.canal': { status: 'extracted', confidence: 0.90, is_required: true },
          'intencion.uso_principal': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "What clinical constraints must be followed? (e.g., \"review allergies before prescribing\", \"emergency escalation protocol\", \"informed consent required\")",
        fields: {
          'escenario.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.tipo_cliente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.nivel_experiencia_compra': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.urgencia': { status: 'confirmed', confidence: 0.95, is_required: true },
          'contexto_conversacion.canal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'intencion.uso_principal': { status: 'confirmed', confidence: 0.92, is_required: true },
          'escenario.tono_esperado': { status: 'extracted', confidence: 0.90, is_required: true },
          'escenario.complejidad': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "Describe the expected consultation flow — what steps should the conversation follow? (e.g., chief complaint → history → examination → diagnosis → treatment plan → follow-up)",
        fields: {
          'escenario.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.tipo_cliente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.nivel_experiencia_compra': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.urgencia': { status: 'confirmed', confidence: 0.95, is_required: true },
          'contexto_conversacion.canal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'intencion.uso_principal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'escenario.tono_esperado': { status: 'confirmed', confidence: 0.95, is_required: true },
          'escenario.complejidad': { status: 'confirmed', confidence: 0.95, is_required: true },
        },
      },
    ],
    es: [
      {
        question: "Hola! Te ayudaré a diseñar un escenario de consulta médica sintética para entrenamiento de IA. ¿Qué tipo de consulta deseas simular? (ej: evaluación cardiológica, consulta pediátrica, evaluación de salud mental, seguimiento)",
        fields: {},
      },
      {
        question: "¿Qué perfil de paciente debemos simular? Describe su condición, experiencia con el sistema de salud, y nivel de urgencia (rutina, moderadamente urgente, emergencia).",
        fields: { 'escenario.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true } },
      },
      {
        question: "¿Cuál es el canal — presencial, telemedicina, teléfono? ¿Y cuál es el objetivo clínico principal de esta consulta?",
        fields: {
          'escenario.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.tipo_cliente': { status: 'extracted', confidence: 0.90, is_required: true },
          'cliente_perfil.nivel_experiencia_compra': { status: 'extracted', confidence: 0.90, is_required: true },
          'cliente_perfil.urgencia': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "¿Qué tono debe tener la consulta — formal-clínico, empático, o educativo? ¿Qué tan complejo debe ser el caso?",
        fields: {
          'escenario.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.tipo_cliente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.nivel_experiencia_compra': { status: 'confirmed', confidence: 0.92, is_required: true },
          'cliente_perfil.urgencia': { status: 'confirmed', confidence: 0.92, is_required: true },
          'contexto_conversacion.canal': { status: 'extracted', confidence: 0.90, is_required: true },
          'intencion.uso_principal': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "¿Qué restricciones clínicas deben seguirse? (ej: \"revisar alergias antes de prescribir\", \"protocolo de escalación de emergencia\", \"consentimiento informado requerido\")",
        fields: {
          'escenario.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.tipo_cliente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.nivel_experiencia_compra': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.urgencia': { status: 'confirmed', confidence: 0.95, is_required: true },
          'contexto_conversacion.canal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'intencion.uso_principal': { status: 'confirmed', confidence: 0.92, is_required: true },
          'escenario.tono_esperado': { status: 'extracted', confidence: 0.90, is_required: true },
          'escenario.complejidad': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "Describe el flujo clínico esperado — ¿qué pasos debe seguir la consulta? (ej: motivo → historial → exploración → diagnóstico → plan de tratamiento → seguimiento)",
        fields: {
          'escenario.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.tipo_cliente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.nivel_experiencia_compra': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_perfil.urgencia': { status: 'confirmed', confidence: 0.95, is_required: true },
          'contexto_conversacion.canal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'intencion.uso_principal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'escenario.tono_esperado': { status: 'confirmed', confidence: 0.95, is_required: true },
          'escenario.complejidad': { status: 'confirmed', confidence: 0.95, is_required: true },
        },
      },
    ],
  },
}

// All field names from the automotive extraction schema (dot-path format)
const ALL_EXTRACTION_FIELDS = [
  'cliente_perfil.tipo_cliente',
  'cliente_perfil.nivel_experiencia_compra',
  'cliente_perfil.urgencia',
  'cliente_perfil.presupuesto_rango',
  'intencion.uso_principal',
  'intencion.tipo_vehiculo',
  'contexto_conversacion.canal',
  'contexto_conversacion.objeciones_conocidas',
  'escenario.tipo_escenario',
  'escenario.complejidad',
  'escenario.tono_esperado',
  'reglas_negocio.restricciones',
]

const REQUIRED_EXTRACTION_FIELDS = new Set([
  'cliente_perfil.tipo_cliente',
  'cliente_perfil.nivel_experiencia_compra',
  'cliente_perfil.urgencia',
  'intencion.uso_principal',
  'contexto_conversacion.canal',
  'escenario.tipo_escenario',
  'escenario.complejidad',
  'escenario.tono_esperado',
])

function buildDemoProgress(step: number, totalSteps: number, fields: Record<string, { status: string; confidence: number; is_required: boolean }>): ExtractionProgress {
  const fieldEntries = Object.entries(fields)
  const progressFields: ExtractionProgress['fields'] = {}

  for (const name of ALL_EXTRACTION_FIELDS) {
    const existing = fields[name]

    progressFields[name] = existing
      ? { status: existing.status as 'extracted' | 'confirmed', confidence: existing.confidence, is_required: existing.is_required }
      : { status: 'empty', confidence: 0, is_required: REQUIRED_EXTRACTION_FIELDS.has(name) }
  }

  const filled = fieldEntries.length
  const requiredFilled = fieldEntries.filter(([name, v]) => v.is_required && REQUIRED_EXTRACTION_FIELDS.has(name)).length

  return {
    turn: step,
    max_turns: totalSteps + 1,
    total_fields: ALL_EXTRACTION_FIELDS.length,
    filled_fields: filled,
    required_total: REQUIRED_EXTRACTION_FIELDS.size,
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

    // Check if API is available and LLM is configured
    const { ok: apiOk, llmConfigured } = await checkApiHealthDetailed()

    if (apiOk && llmConfigured) {
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
        // Extraction complete — build a proper SeedSchema v1 from interview data
        const isAuto = industry !== 'medical'

        const demoSeed = {
          version: '1.0',
          dominio: isAuto ? 'automotive.sales' : 'medical.consultation',
          idioma: locale,
          etiquetas: ['ai-extracted', industry],
          roles: isAuto ? ['customer', 'sales_advisor'] : ['patient', 'physician'],
          descripcion_roles: isAuto
            ? {
                customer: 'Cliente particular, comprador primerizo, urgencia: explorando',
                sales_advisor: 'Asesor de ventas certificado con acceso al inventario',
              }
            : {
                patient: 'Paciente adulto buscando consulta especializada',
                physician: 'Médico especialista certificado',
              },
          objetivo: isAuto
            ? 'Simular una conversación de venta_directa automotriz con un cliente particular interesado en uso personal'
            : 'Simular una consulta médica de evaluación inicial con un paciente adulto',
          tono: 'profesional',
          pasos_turnos: {
            turnos_min: 4,
            turnos_max: 10,
            flujo_esperado: isAuto
              ? ['Saludo', 'Detección de necesidad', 'Manejo de objeciones', 'Presentación/Cotización', 'Cierre/Siguiente paso']
              : ['Motivo de consulta', 'Revisión de historial', 'Exploración', 'Diagnóstico', 'Plan de tratamiento', 'Seguimiento'],
          },
          parametros_factuales: {
            contexto: isAuto ? 'Canal: whatsapp. Tipo de vehículo: sedan' : 'Canal: presencial. Consulta de primera vez',
            restricciones: isAuto
              ? ['Solo ofrecer inventario actual', 'Precios con IVA incluido', 'No comparar con la competencia']
              : ['Revisar alergias antes de prescribir', 'Protocolo de escalación de emergencia', 'Consentimiento informado requerido'],
            herramientas: [],
            metadata: {
              extracted_by: 'ai-interview',
              scenario_type: isAuto ? 'venta_directa' : 'consulta_inicial',
              complexity: 'medio',
              client_type: isAuto ? 'particular' : 'paciente_nuevo',
              channel: isAuto ? 'whatsapp' : 'presencial',
            },
          },
          privacidad: { pii_eliminado: true, metodo_anonimizacion: 'presidio_v2', nivel_confianza: 0.99, campos_sensibles_detectados: [] },
          metricas_calidad: { rouge_l_min: 0.20, fidelidad_min: 0.80, diversidad_lexica_min: 0.55, coherencia_dialogica_min: 0.65 },
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

    // Best-effort API persistence (fire-and-forget)
    createSeedApi(newSeed as unknown as Record<string, unknown>).catch(() => {})

    window.location.href = '/dashboard/pipeline/seeds'
  }, [seed])

  const turnsLeft = progress ? progress.max_turns - progress.turn : 0
  const s = locale === 'es' ? t.es : t.en

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col">
      <PageHeader
        title={s.pageTitle}
        description={sessionState === 'idle' ? s.pageDescIdle : `Active session · ${industry} · ${locale.toUpperCase()}${demoMode ? ' · Demo' : ''}`}
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
          <button onClick={() => setError(null)} className="ml-2 underline">{s.dismiss}</button>
        </div>
      )}

      {/* Pre-session: industry + language selector */}
      {sessionState === 'idle' && (
        <div className="flex flex-1 items-center justify-center">
          <div className="mx-auto w-full max-w-md space-y-6 rounded-xl border bg-card p-8 shadow-sm">
            <div className="text-center">
              <MessageSquare className="mx-auto mb-3 size-12 text-primary" />
              <h2 className="text-lg font-semibold">{s.heading}</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                {s.headingDesc}
              </p>
            </div>

            <Alert className="text-left">
              <Info className="size-4" />
              <AlertTitle>{s.alertTitle}</AlertTitle>
              <AlertDescription>
                {s.alertDesc1}{' '}
                {s.alertDemo}{' '}
                {s.alertAlso}{' '}
                <Link href="/dashboard/pipeline/seeds/new" className="font-medium underline underline-offset-2">
                  {s.alertManual}
                </Link>{' '}
                {s.alertOr}{' '}
                <Link href="/dashboard/pipeline/seeds" className="font-medium underline underline-offset-2">
                  {s.alertBrowse}
                </Link>.
              </AlertDescription>
            </Alert>

            <div className="space-y-3">
              <div className="space-y-1">
                <label className="text-xs font-medium">{s.industryLabel}</label>
                <Select value={industry} onValueChange={setIndustry}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="automotive">{s.automotive}</SelectItem>
                    <SelectItem value="medical">{s.medical}</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-1">
                <label className="flex items-center gap-1.5 text-xs font-medium">
                  <Globe className="size-3" /> {s.languageLabel}
                </label>
                <Select value={locale} onValueChange={setLocale}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">{s.english}</SelectItem>
                    <SelectItem value="es">{s.spanish}</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button onClick={handleStart} className="w-full gap-2" disabled={starting}>
                {starting ? (
                  <><Loader2 className="size-4 animate-spin" /> {s.starting}</>
                ) : (
                  <><Sparkles className="size-4" /> {s.startInterview}</>
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
                {s.turnsRemaining(turnsLeft)}
              </div>
            )}

            {/* Input or completion actions */}
            {sessionState === 'complete' ? (
              <div className="flex items-center gap-3 border-t bg-emerald-50 p-4 dark:border-zinc-700 dark:bg-emerald-950/20">
                <Sparkles className="size-5 text-emerald-600" />
                <span className="flex-1 text-sm font-medium text-emerald-800 dark:text-emerald-200">
                  {s.extractionComplete}
                </span>
                <Button variant="outline" size="sm" onClick={handleEndSession}>
                  {s.newInterview}
                </Button>
                {seed && (
                  <Button size="sm" onClick={handleCreateSeed} className="gap-1.5">
                    <Sparkles className="size-3" /> {s.createSeed}
                  </Button>
                )}
              </div>
            ) : (
              <ChatInput
                onSend={handleSend}
                disabled={sessionState !== 'active'}
                placeholder={sessionState === 'processing' ? s.processing : s.typePlaceholder}
              />
            )}
          </div>

          {/* Progress sidebar */}
          {showSidebar && (
            <div className="hidden w-80 shrink-0 border-l bg-card lg:block dark:border-zinc-800">
              <div className="border-b px-3 py-2 dark:border-zinc-800">
                <h3 className="text-xs font-semibold">{s.progressTitle}</h3>
              </div>
              <ExtractionProgressPanel progress={progress} />
            </div>
          )}
        </div>
      )}
    </div>
  )
}
