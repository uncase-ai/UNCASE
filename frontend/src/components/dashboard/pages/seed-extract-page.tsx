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
    finance: 'Finance',
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
    finance: 'Finanzas',
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
        question: "Hello! I'll help you design a synthetic medical consultation scenario. We'll define all the parameters to generate realistic patient-provider conversations for AI training. What type of consultation do you want to simulate? (e.g., first visit, follow-up, second opinion, emergency, test results review)",
        fields: {},
      },
      {
        question: "What patient profile should we simulate? Describe the patient type (adult, pediatric, geriatric), their condition severity, and emotional state (calm, anxious, scared, frustrated).",
        fields: {
          'escenario_medico.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'motivo_consulta.especialidad': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "What's the chief complaint and the medical specialty? What's the symptom duration — acute, subacute, or chronic? Any previous treatments?",
        fields: {
          'escenario_medico.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'motivo_consulta.especialidad': { status: 'confirmed', confidence: 0.92, is_required: true },
          'paciente_perfil.tipo_paciente': { status: 'extracted', confidence: 0.90, is_required: true },
          'paciente_perfil.severidad_condicion': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "What's the setting — office visit, hospital, clinic, home visit, or ER? And the channel — in-person, telemedicine, phone, or medical chat?",
        fields: {
          'escenario_medico.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'motivo_consulta.especialidad': { status: 'confirmed', confidence: 0.95, is_required: true },
          'paciente_perfil.tipo_paciente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'paciente_perfil.severidad_condicion': { status: 'confirmed', confidence: 0.92, is_required: true },
          'motivo_consulta.motivo_principal': { status: 'extracted', confidence: 0.90, is_required: true },
          'motivo_consulta.duracion_sintomas': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "What tone should the consultation have — professional, empathetic, direct, or educational? How complex should the case be? Should it include physical examination, diagnostic reasoning, or patient education?",
        fields: {
          'escenario_medico.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'motivo_consulta.especialidad': { status: 'confirmed', confidence: 0.95, is_required: true },
          'paciente_perfil.tipo_paciente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'paciente_perfil.severidad_condicion': { status: 'confirmed', confidence: 0.95, is_required: true },
          'motivo_consulta.motivo_principal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'motivo_consulta.duracion_sintomas': { status: 'confirmed', confidence: 0.92, is_required: true },
          'contexto_clinico.canal': { status: 'extracted', confidence: 0.90, is_required: true },
          'contexto_clinico.entorno': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "Last question — any specific clinical rules or regulatory constraints? (e.g., \"review allergies before prescribing\", \"informed consent required\", \"HIPAA compliance\", \"emergency escalation protocol\")",
        fields: {
          'escenario_medico.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'motivo_consulta.especialidad': { status: 'confirmed', confidence: 0.95, is_required: true },
          'paciente_perfil.tipo_paciente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'paciente_perfil.severidad_condicion': { status: 'confirmed', confidence: 0.95, is_required: true },
          'motivo_consulta.motivo_principal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'motivo_consulta.duracion_sintomas': { status: 'confirmed', confidence: 0.95, is_required: true },
          'contexto_clinico.canal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'contexto_clinico.entorno': { status: 'confirmed', confidence: 0.95, is_required: true },
          'escenario_medico.complejidad': { status: 'extracted', confidence: 0.90, is_required: true },
          'escenario_medico.tono': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
    ],
    es: [
      {
        question: "¡Hola! Te ayudaré a diseñar un escenario de consulta médica sintética para entrenamiento de IA. ¿Qué tipo de consulta deseas simular? (ej: primera consulta, seguimiento, segunda opinión, urgencia, revisión de resultados)",
        fields: {},
      },
      {
        question: "¿Qué perfil de paciente debemos simular? Describe el tipo (adulto, pediátrico, geriátrico), la severidad de su condición, y su estado emocional (tranquilo, ansioso, asustado, frustrado).",
        fields: {
          'escenario_medico.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'motivo_consulta.especialidad': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "¿Cuál es el motivo principal de consulta y la especialidad? ¿La duración de los síntomas — agudo, subagudo o crónico? ¿Tratamientos previos?",
        fields: {
          'escenario_medico.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'motivo_consulta.especialidad': { status: 'confirmed', confidence: 0.92, is_required: true },
          'paciente_perfil.tipo_paciente': { status: 'extracted', confidence: 0.90, is_required: true },
          'paciente_perfil.severidad_condicion': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "¿En qué entorno — consultorio, hospital, clínica, domicilio, o urgencias? ¿Y por qué canal — presencial, telemedicina, teléfono, o chat médico?",
        fields: {
          'escenario_medico.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'motivo_consulta.especialidad': { status: 'confirmed', confidence: 0.95, is_required: true },
          'paciente_perfil.tipo_paciente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'paciente_perfil.severidad_condicion': { status: 'confirmed', confidence: 0.92, is_required: true },
          'motivo_consulta.motivo_principal': { status: 'extracted', confidence: 0.90, is_required: true },
          'motivo_consulta.duracion_sintomas': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "¿Qué tono debe tener la consulta — profesional, empático, directo, o didáctico? ¿Qué tan complejo debe ser el caso? ¿Debe incluir exploración física, razonamiento diagnóstico, o educación al paciente?",
        fields: {
          'escenario_medico.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'motivo_consulta.especialidad': { status: 'confirmed', confidence: 0.95, is_required: true },
          'paciente_perfil.tipo_paciente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'paciente_perfil.severidad_condicion': { status: 'confirmed', confidence: 0.95, is_required: true },
          'motivo_consulta.motivo_principal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'motivo_consulta.duracion_sintomas': { status: 'confirmed', confidence: 0.92, is_required: true },
          'contexto_clinico.canal': { status: 'extracted', confidence: 0.90, is_required: true },
          'contexto_clinico.entorno': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "Última pregunta — ¿hay reglas clínicas o restricciones regulatorias específicas? (ej: \"revisar alergias antes de prescribir\", \"consentimiento informado requerido\", \"cumplimiento NOM\", \"protocolo de escalación\")",
        fields: {
          'escenario_medico.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'motivo_consulta.especialidad': { status: 'confirmed', confidence: 0.95, is_required: true },
          'paciente_perfil.tipo_paciente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'paciente_perfil.severidad_condicion': { status: 'confirmed', confidence: 0.95, is_required: true },
          'motivo_consulta.motivo_principal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'motivo_consulta.duracion_sintomas': { status: 'confirmed', confidence: 0.95, is_required: true },
          'contexto_clinico.canal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'contexto_clinico.entorno': { status: 'confirmed', confidence: 0.95, is_required: true },
          'escenario_medico.complejidad': { status: 'extracted', confidence: 0.90, is_required: true },
          'escenario_medico.tono': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
    ],
  },
  finance: {
    en: [
      {
        question: "Hello! I'll help you design a synthetic financial advisory scenario. We'll define the parameters to generate realistic client-advisor conversations for AI training. What type of financial service do you want to simulate? (e.g., credit application, investment advisory, savings plan, insurance, debt restructuring)",
        fields: {},
      },
      {
        question: "What client profile should we simulate? Describe their type (individual, SME, corporate, investor), risk profile (conservative, moderate, aggressive), and financial literacy level.",
        fields: {
          'escenario_financiero.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'objetivo_financiero.tipo_servicio': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "What's the client's specific financial goal? What amount range and time horizon are we looking at — short-term, medium-term, or long-term?",
        fields: {
          'escenario_financiero.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'objetivo_financiero.tipo_servicio': { status: 'confirmed', confidence: 0.92, is_required: true },
          'cliente_financiero.tipo_cliente': { status: 'extracted', confidence: 0.90, is_required: true },
          'cliente_financiero.perfil_riesgo': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "What's the channel — branch office, phone, digital banking, WhatsApp, or video call? And the institution type — bank, fintech, brokerage, or insurance company?",
        fields: {
          'escenario_financiero.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'objetivo_financiero.tipo_servicio': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_financiero.tipo_cliente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_financiero.perfil_riesgo': { status: 'confirmed', confidence: 0.92, is_required: true },
          'objetivo_financiero.objetivo_especifico': { status: 'extracted', confidence: 0.90, is_required: true },
          'objetivo_financiero.horizonte_temporal': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "What tone should the conversation have — professional, consultative, educational, or empathetic? Should it include risk disclosure, product comparisons, or financial simulations?",
        fields: {
          'escenario_financiero.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'objetivo_financiero.tipo_servicio': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_financiero.tipo_cliente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_financiero.perfil_riesgo': { status: 'confirmed', confidence: 0.95, is_required: true },
          'objetivo_financiero.objetivo_especifico': { status: 'confirmed', confidence: 0.95, is_required: true },
          'objetivo_financiero.horizonte_temporal': { status: 'confirmed', confidence: 0.92, is_required: true },
          'contexto_financiero.canal': { status: 'extracted', confidence: 0.90, is_required: true },
          'contexto_financiero.tipo_institucion': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "Last question — any specific regulatory or compliance constraints? (e.g., \"KYC verification required\", \"mandatory risk disclosure\", \"CNBV compliance\", \"commission transparency\")",
        fields: {
          'escenario_financiero.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'objetivo_financiero.tipo_servicio': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_financiero.tipo_cliente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_financiero.perfil_riesgo': { status: 'confirmed', confidence: 0.95, is_required: true },
          'objetivo_financiero.objetivo_especifico': { status: 'confirmed', confidence: 0.95, is_required: true },
          'objetivo_financiero.horizonte_temporal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'contexto_financiero.canal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'contexto_financiero.tipo_institucion': { status: 'confirmed', confidence: 0.95, is_required: true },
          'escenario_financiero.complejidad': { status: 'extracted', confidence: 0.90, is_required: true },
          'escenario_financiero.tono': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
    ],
    es: [
      {
        question: "¡Hola! Te ayudaré a diseñar un escenario de asesoría financiera sintética para entrenamiento de IA. ¿Qué tipo de servicio financiero deseas simular? (ej: solicitud de crédito, asesoría de inversión, plan de ahorro, seguro, reestructura de deuda)",
        fields: {},
      },
      {
        question: "¿Qué perfil de cliente debemos simular? Describe su tipo (persona física, PyME, corporativo, inversionista), perfil de riesgo (conservador, moderado, agresivo), y nivel de educación financiera.",
        fields: {
          'escenario_financiero.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'objetivo_financiero.tipo_servicio': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "¿Cuál es el objetivo financiero específico del cliente? ¿Qué monto y horizonte temporal — corto, mediano o largo plazo?",
        fields: {
          'escenario_financiero.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'objetivo_financiero.tipo_servicio': { status: 'confirmed', confidence: 0.92, is_required: true },
          'cliente_financiero.tipo_cliente': { status: 'extracted', confidence: 0.90, is_required: true },
          'cliente_financiero.perfil_riesgo': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "¿Por qué canal — sucursal, teléfono, banca digital, WhatsApp, o videollamada? ¿Y qué tipo de institución — banco, fintech, casa de bolsa, o aseguradora?",
        fields: {
          'escenario_financiero.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'objetivo_financiero.tipo_servicio': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_financiero.tipo_cliente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_financiero.perfil_riesgo': { status: 'confirmed', confidence: 0.92, is_required: true },
          'objetivo_financiero.objetivo_especifico': { status: 'extracted', confidence: 0.90, is_required: true },
          'objetivo_financiero.horizonte_temporal': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "¿Qué tono debe tener la conversación — profesional, consultivo, educativo, o empático? ¿Debe incluir divulgación de riesgos, comparaciones de productos, o simulaciones financieras?",
        fields: {
          'escenario_financiero.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'objetivo_financiero.tipo_servicio': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_financiero.tipo_cliente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_financiero.perfil_riesgo': { status: 'confirmed', confidence: 0.95, is_required: true },
          'objetivo_financiero.objetivo_especifico': { status: 'confirmed', confidence: 0.95, is_required: true },
          'objetivo_financiero.horizonte_temporal': { status: 'confirmed', confidence: 0.92, is_required: true },
          'contexto_financiero.canal': { status: 'extracted', confidence: 0.90, is_required: true },
          'contexto_financiero.tipo_institucion': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
      {
        question: "Última pregunta — ¿hay restricciones regulatorias o de cumplimiento específicas? (ej: \"verificación KYC requerida\", \"divulgación de riesgos obligatoria\", \"cumplimiento CNBV\", \"transparencia en comisiones\")",
        fields: {
          'escenario_financiero.tipo_escenario': { status: 'confirmed', confidence: 0.95, is_required: true },
          'objetivo_financiero.tipo_servicio': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_financiero.tipo_cliente': { status: 'confirmed', confidence: 0.95, is_required: true },
          'cliente_financiero.perfil_riesgo': { status: 'confirmed', confidence: 0.95, is_required: true },
          'objetivo_financiero.objetivo_especifico': { status: 'confirmed', confidence: 0.95, is_required: true },
          'objetivo_financiero.horizonte_temporal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'contexto_financiero.canal': { status: 'confirmed', confidence: 0.95, is_required: true },
          'contexto_financiero.tipo_institucion': { status: 'confirmed', confidence: 0.95, is_required: true },
          'escenario_financiero.complejidad': { status: 'extracted', confidence: 0.90, is_required: true },
          'escenario_financiero.tono': { status: 'extracted', confidence: 0.88, is_required: true },
        },
      },
    ],
  },
}

// Per-industry field names from extraction schemas (dot-path format)
const INDUSTRY_FIELDS: Record<string, { all: string[]; required: Set<string> }> = {
  automotive: {
    all: [
      'cliente_perfil.tipo_cliente', 'cliente_perfil.nivel_experiencia_compra', 'cliente_perfil.urgencia',
      'cliente_perfil.presupuesto_rango', 'intencion.uso_principal', 'intencion.tipo_vehiculo',
      'contexto_conversacion.canal', 'contexto_conversacion.objeciones_conocidas',
      'escenario.tipo_escenario', 'escenario.complejidad', 'escenario.tono_esperado', 'reglas_negocio.restricciones',
    ],
    required: new Set([
      'cliente_perfil.tipo_cliente', 'cliente_perfil.nivel_experiencia_compra', 'cliente_perfil.urgencia',
      'intencion.uso_principal', 'contexto_conversacion.canal',
      'escenario.tipo_escenario', 'escenario.complejidad', 'escenario.tono_esperado',
    ]),
  },
  medical: {
    all: [
      'paciente_perfil.tipo_paciente', 'paciente_perfil.severidad_condicion', 'paciente_perfil.cobertura_medica',
      'motivo_consulta.especialidad', 'motivo_consulta.motivo_principal', 'motivo_consulta.duracion_sintomas',
      'contexto_clinico.canal', 'contexto_clinico.entorno', 'contexto_clinico.restriccion_tiempo',
      'escenario_medico.tipo_escenario', 'escenario_medico.complejidad', 'escenario_medico.tono',
    ],
    required: new Set([
      'paciente_perfil.tipo_paciente', 'paciente_perfil.severidad_condicion',
      'motivo_consulta.especialidad', 'motivo_consulta.motivo_principal', 'motivo_consulta.duracion_sintomas',
      'contexto_clinico.canal', 'escenario_medico.tipo_escenario', 'escenario_medico.complejidad',
      'escenario_medico.tono',
    ]),
  },
  finance: {
    all: [
      'cliente_financiero.tipo_cliente', 'cliente_financiero.perfil_riesgo', 'cliente_financiero.nivel_conocimiento_financiero',
      'objetivo_financiero.tipo_servicio', 'objetivo_financiero.objetivo_especifico', 'objetivo_financiero.horizonte_temporal',
      'contexto_financiero.canal', 'contexto_financiero.tipo_institucion',
      'escenario_financiero.tipo_escenario', 'escenario_financiero.complejidad', 'escenario_financiero.tono',
      'reglas_financieras.marco_cumplimiento',
    ],
    required: new Set([
      'cliente_financiero.tipo_cliente', 'cliente_financiero.perfil_riesgo',
      'objetivo_financiero.tipo_servicio', 'objetivo_financiero.objetivo_especifico', 'objetivo_financiero.horizonte_temporal',
      'contexto_financiero.canal', 'escenario_financiero.tipo_escenario', 'escenario_financiero.complejidad',
      'escenario_financiero.tono',
    ]),
  },
}

function buildDemoProgress(step: number, totalSteps: number, fields: Record<string, { status: string; confidence: number; is_required: boolean }>, industryKey: string): ExtractionProgress {
  const { all: allFields, required: requiredFields } = INDUSTRY_FIELDS[industryKey] ?? INDUSTRY_FIELDS.automotive
  const fieldEntries = Object.entries(fields)
  const progressFields: ExtractionProgress['fields'] = {}

  for (const name of allFields) {
    const existing = fields[name]

    progressFields[name] = existing
      ? { status: existing.status as 'extracted' | 'confirmed', confidence: existing.confidence, is_required: existing.is_required }
      : { status: 'empty', confidence: 0, is_required: requiredFields.has(name) }
  }

  const filled = fieldEntries.length
  const requiredFilled = fieldEntries.filter(([name, v]) => v.is_required && requiredFields.has(name)).length

  return {
    turn: step,
    max_turns: totalSteps + 1,
    total_fields: allFields.length,
    filled_fields: filled,
    required_total: requiredFields.size,
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
    const demoProgress = buildDemoProgress(0, script.length, step.fields, industry)

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
        const seedTemplates: Record<string, Record<string, unknown>> = {
          automotive: {
            version: '1.0',
            dominio: 'automotive.sales',
            idioma: locale,
            etiquetas: ['ai-extracted', 'automotive', 'scenario:venta_directa', 'complexity:medio'],
            roles: ['customer', 'sales_advisor'],
            descripcion_roles: {
              customer: 'Cliente particular, experiencia: primera_vez, urgencia: explorando, pago: financiamiento',
              sales_advisor: 'Asesor de ventas certificado con acceso al inventario',
            },
            objetivo: 'Simular una conversación de venta_directa automotriz con un cliente particular interesado en un sedan nuevo para uso personal',
            tono: 'profesional',
            pasos_turnos: {
              turnos_min: 5, turnos_max: 10,
              flujo_esperado: ['Saludo y bienvenida', 'Detección de necesidades', 'Presentación de opciones', 'Manejo de objeciones', 'Cotización formal', 'Cierre y siguiente paso'],
            },
            parametros_factuales: {
              contexto: 'Canal: whatsapp. Tipo de vehículo: sedan. Condición: nuevo',
              restricciones: ['Solo ofrecer inventario actual', 'Precios con IVA incluido', 'No comparar con la competencia'],
              herramientas: ['consultar_inventario', 'generar_cotizacion', 'calcular_financiamiento'],
              metadata: { extracted_by: 'ai-interview', scenario_type: 'venta_directa', complexity: 'medio', client_type: 'particular', channel: 'whatsapp', vehicle_condition: 'nuevo' },
            },
          },
          medical: {
            version: '1.0',
            dominio: 'medical.consultation',
            idioma: locale,
            etiquetas: ['ai-extracted', 'medical', 'scenario:primera_consulta', 'complexity:moderado'],
            roles: ['patient', 'physician'],
            descripcion_roles: {
              patient: 'Paciente adulto, condición moderada, ansioso, con seguro privado',
              physician: 'Médico especialista certificado en cardiología',
            },
            objetivo: 'Simular una primera consulta de cardiología con un paciente adulto con síntomas subagudos de dolor torácico',
            tono: 'empático',
            pasos_turnos: {
              turnos_min: 5, turnos_max: 12,
              flujo_esperado: ['Saludo y motivo de consulta', 'Historia clínica', 'Revisión de síntomas', 'Exploración física', 'Razonamiento diagnóstico', 'Plan de tratamiento', 'Educación al paciente', 'Seguimiento'],
            },
            parametros_factuales: {
              contexto: 'Canal: presencial. Entorno: consultorio. Especialidad: cardiología. Severidad: moderada. Primera consulta',
              restricciones: ['Revisar alergias antes de prescribir', 'Consentimiento informado requerido', 'Documentar en nota médica', 'Cumplimiento NOM'],
              herramientas: ['consultar_historial', 'ordenar_estudios', 'generar_receta', 'agendar_seguimiento'],
              metadata: { extracted_by: 'ai-interview', scenario_type: 'primera_consulta', complexity: 'moderado', patient_type: 'adulto', specialty: 'cardiologia', channel: 'presencial', setting: 'consultorio' },
            },
          },
          finance: {
            version: '1.0',
            dominio: 'finance.advisory',
            idioma: locale,
            etiquetas: ['ai-extracted', 'finance', 'scenario:solicitud_credito', 'complexity:moderado'],
            roles: ['client', 'financial_advisor'],
            descripcion_roles: {
              client: 'Persona física, perfil moderado, nivel financiero intermedio, empleado asalariado',
              financial_advisor: 'Asesor financiero certificado con acceso a productos bancarios',
            },
            objetivo: 'Simular una asesoría de solicitud de crédito hipotecario con un cliente asalariado de perfil moderado',
            tono: 'consultivo',
            pasos_turnos: {
              turnos_min: 5, turnos_max: 12,
              flujo_esperado: ['Saludo e identificación', 'Evaluación de necesidades', 'Análisis de perfil crediticio', 'Presentación de opciones', 'Divulgación de riesgos', 'Simulación de pagos', 'Documentación requerida', 'Cierre y siguientes pasos'],
            },
            parametros_factuales: {
              contexto: 'Canal: sucursal. Institución: banco. Servicio: crédito hipotecario. Horizonte: largo plazo',
              restricciones: ['Verificación KYC obligatoria', 'Divulgación de CAT y tasa de interés', 'Cumplimiento CNBV', 'Transparencia en comisiones'],
              herramientas: ['consultar_buro_credito', 'simular_credito', 'comparar_productos', 'generar_solicitud'],
              metadata: { extracted_by: 'ai-interview', scenario_type: 'solicitud_credito', complexity: 'moderado', client_type: 'persona_fisica', risk_profile: 'moderado', channel: 'sucursal', institution: 'banco' },
            },
          },
        }

        const demoSeed = {
          ...seedTemplates[industry] ?? seedTemplates.automotive,
          privacidad: { pii_eliminado: true, metodo_anonimizacion: 'presidio_v2', nivel_confianza: 0.99, campos_sensibles_detectados: [] },
          metricas_calidad: { rouge_l_min: 0.20, fidelidad_min: 0.80, diversidad_lexica_min: 0.55, coherencia_dialogica_min: 0.65 },
        }

        const summaryMsg = locale === 'es'
          ? 'Extracción completada. He recopilado todos los parámetros necesarios para tu seed de conversación. Puedes revisarlo y crearlo.'
          : 'Extraction complete! I\'ve gathered all the parameters needed for your conversation seed. You can review and create it.'

        const finalProgress = buildDemoProgress(script.length, script.length, script[script.length - 1].fields, industry)

        setProgress(finalProgress)
        addMessage('system', summaryMsg, finalProgress)
        setSeed(demoSeed)
        setSessionState('complete')

        return
      }

      const step = script[stepIdx]
      const demoProgress = buildDemoProgress(stepIdx, script.length, step.fields, industry)

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
                    <SelectItem value="finance">{s.finance}</SelectItem>
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
