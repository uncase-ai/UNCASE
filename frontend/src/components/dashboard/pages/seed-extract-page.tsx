'use client'

import { useCallback, useState } from 'react'

import { ArrowLeft, Loader2, MessageSquare, PanelRightClose, PanelRightOpen, Sparkles } from 'lucide-react'
import Link from 'next/link'

import type { ChatMessage, ExtractionProgress } from '@/types/layer0'
import { endSession, sendTurn, startExtraction } from '@/lib/api/layer0'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

import { ChatContainer } from '../chat/chat-container'
import { ChatInput } from '../chat/chat-input'
import { ExtractionProgressPanel } from '../chat/extraction-progress'
import { TypingIndicator } from '../chat/typing-indicator'
import { PageHeader } from '../page-header'

type SessionState = 'idle' | 'active' | 'processing' | 'complete'

export function SeedExtractPage() {
  const [sessionState, setSessionState] = useState<SessionState>('idle')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [progress, setProgress] = useState<ExtractionProgress | null>(null)
  const [seed, setSeed] = useState<Record<string, unknown> | null>(null)
  const [industry, setIndustry] = useState('automotive')
  const [error, setError] = useState<string | null>(null)
  const [showSidebar, setShowSidebar] = useState(true)
  const [starting, setStarting] = useState(false)

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

    const { data, error: apiError } = await startExtraction({ industry })

    if (apiError || !data) {
      setError(apiError?.message ?? 'Error al iniciar la sesión')
      setStarting(false)
      return
    }

    setSessionId(data.session_id)
    setProgress(data.message.progress ?? null)
    addMessage('assistant', data.message.content, data.message.progress)
    setSessionState('active')
    setStarting(false)
  }, [industry, addMessage])

  const handleSend = useCallback(async (text: string) => {
    if (!sessionId || sessionState !== 'active') return

    addMessage('user', text)
    setSessionState('processing')

    const { data, error: apiError } = await sendTurn({
      session_id: sessionId,
      user_message: text,
    })

    if (apiError || !data) {
      setError(apiError?.message ?? 'Error al procesar el turno')
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
  }, [sessionId, sessionState, addMessage])

  const handleEndSession = useCallback(async () => {
    if (sessionId) {
      await endSession(sessionId)
    }
    setSessionState('idle')
    setSessionId(null)
  }, [sessionId])

  const handleCreateSeed = useCallback(() => {
    if (!seed) return
    // Store in localStorage for the seeds page to pick up
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
        title="Entrevista AI — Extracción de Seed"
        description={sessionState === 'idle' ? 'Inicia una entrevista guiada por IA para crear un seed' : `Sesión activa · ${industry}`}
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
          <button onClick={() => setError(null)} className="ml-2 underline">Cerrar</button>
        </div>
      )}

      {/* Pre-session: industry selector */}
      {sessionState === 'idle' && (
        <div className="flex flex-1 items-center justify-center">
          <div className="mx-auto w-full max-w-md space-y-6 rounded-xl border bg-card p-8 shadow-sm">
            <div className="text-center">
              <MessageSquare className="mx-auto mb-3 size-12 text-emerald-600" />
              <h2 className="text-lg font-semibold">Entrevista de Extracción</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                La IA te guiará a través de preguntas para extraer todos los parámetros necesarios para crear un seed de conversación.
              </p>
            </div>

            <div className="space-y-3">
              <div className="space-y-1">
                <label className="text-xs font-medium">Industria</label>
                <Select value={industry} onValueChange={setIndustry}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="automotive">Automotriz</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button onClick={handleStart} className="w-full gap-2" disabled={starting}>
                {starting ? (
                  <><Loader2 className="size-4 animate-spin" /> Iniciando...</>
                ) : (
                  <><Sparkles className="size-4" /> Iniciar Entrevista</>
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
                ⚠ Solo {turnsLeft} turno{turnsLeft !== 1 ? 's' : ''} restante{turnsLeft !== 1 ? 's' : ''}
              </div>
            )}

            {/* Input or completion actions */}
            {sessionState === 'complete' ? (
              <div className="flex items-center gap-3 border-t bg-emerald-50 p-4 dark:border-zinc-700 dark:bg-emerald-950/20">
                <Sparkles className="size-5 text-emerald-600" />
                <span className="flex-1 text-sm font-medium text-emerald-800 dark:text-emerald-200">
                  Extracción completada
                </span>
                <Button variant="outline" size="sm" onClick={handleEndSession}>
                  Nueva Entrevista
                </Button>
                {seed && (
                  <Button size="sm" onClick={handleCreateSeed} className="gap-1.5">
                    <Sparkles className="size-3" /> Crear Seed
                  </Button>
                )}
              </div>
            ) : (
              <ChatInput
                onSend={handleSend}
                disabled={sessionState !== 'active'}
                placeholder={sessionState === 'processing' ? 'Procesando...' : 'Escribe tu respuesta...'}
              />
            )}
          </div>

          {/* Progress sidebar */}
          {showSidebar && (
            <div className="hidden w-80 shrink-0 border-l bg-card lg:block dark:border-zinc-800">
              <div className="border-b px-3 py-2 dark:border-zinc-800">
                <h3 className="text-xs font-semibold">Progreso de Extracción</h3>
              </div>
              <ExtractionProgressPanel progress={progress} />
            </div>
          )}
        </div>
      )}
    </div>
  )
}
