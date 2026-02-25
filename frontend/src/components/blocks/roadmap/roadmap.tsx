'use client'

import { BuildingIcon, CheckCircle2Icon, CloudIcon, GlobeIcon, NetworkIcon, UsersIcon } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { MotionPreset } from '@/components/ui/motion-preset'

import JourneyTimeline from '@/components/shadcn-studio/blocks/timeline-component-02/timeline-component-02'

const roadmapData = [
  {
    title: 'Q1 2025 — Foundation',
    content: (
      <Card className='max-w-sm shadow-none'>
        <CardContent className='space-y-3'>
          <div className='flex items-center gap-2'>
            <div className='bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 flex size-10 items-center justify-center rounded-lg'>
              <CheckCircle2Icon className='size-5' />
            </div>
            <Badge className='bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'>Completed</Badge>
          </div>
          <h3 className='text-lg font-semibold'>Project Foundation</h3>
          <p className='text-muted-foreground text-sm leading-relaxed'>
            Repository architecture, SeedSchema v1 design, and the technical whitepaper establishing the SCSF
            (Synthetic Conversational Seed Framework) methodology.
          </p>
          <div className='flex flex-wrap gap-1.5'>
            <Badge variant='outline' className='text-xs'>
              SeedSchema v1
            </Badge>
            <Badge variant='outline' className='text-xs'>
              Whitepaper
            </Badge>
            <Badge variant='outline' className='text-xs'>
              Pydantic models
            </Badge>
          </div>
        </CardContent>
      </Card>
    )
  },
  {
    title: 'Q2 2025 — Core Pipeline',
    content: (
      <Card className='max-w-sm shadow-none'>
        <CardContent className='space-y-3'>
          <div className='flex items-center gap-2'>
            <div className='bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 flex size-10 items-center justify-center rounded-lg'>
              <CheckCircle2Icon className='size-5' />
            </div>
            <Badge className='bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'>Completed</Badge>
          </div>
          <h3 className='text-lg font-semibold'>Layers 0-1: Seed Engine & Parser</h3>
          <p className='text-muted-foreground text-sm leading-relaxed'>
            Seed Engine with Presidio + SpaCy PII elimination. Multi-format parser supporting CSV, JSONL with
            auto-detection of OpenAI, ShareGPT, and UNCASE formats.
          </p>
          <div className='flex flex-wrap gap-1.5'>
            <Badge variant='outline' className='text-xs'>
              PII elimination
            </Badge>
            <Badge variant='outline' className='text-xs'>
              Multi-format parser
            </Badge>
            <Badge variant='outline' className='text-xs'>
              FastAPI
            </Badge>
          </div>
        </CardContent>
      </Card>
    )
  },
  {
    title: 'Q3 2025 — Quality & Generation',
    content: (
      <Card className='max-w-sm shadow-none'>
        <CardContent className='space-y-3'>
          <div className='flex items-center gap-2'>
            <div className='bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 flex size-10 items-center justify-center rounded-lg'>
              <CheckCircle2Icon className='size-5' />
            </div>
            <Badge className='bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'>Completed</Badge>
          </div>
          <h3 className='text-lg font-semibold'>Layers 2-3: Evaluator & Generator</h3>
          <p className='text-muted-foreground text-sm leading-relaxed'>
            6-gate quality evaluation system (ROUGE-L, Factual Fidelity, TTR, Coherence, Privacy, Memorization).
            LiteLLM-powered synthetic generation with tool_calls and tool_results.
          </p>
          <div className='flex flex-wrap gap-1.5'>
            <Badge variant='outline' className='text-xs'>
              6 quality gates
            </Badge>
            <Badge variant='outline' className='text-xs'>
              LiteLLM
            </Badge>
            <Badge variant='outline' className='text-xs'>
              Tool-augmented
            </Badge>
          </div>
        </CardContent>
      </Card>
    )
  },
  {
    title: 'Q4 2025 — LoRA Pipeline & API',
    content: (
      <Card className='max-w-sm shadow-none'>
        <CardContent className='space-y-3'>
          <div className='flex items-center gap-2'>
            <div className='bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 flex size-10 items-center justify-center rounded-lg'>
              <CheckCircle2Icon className='size-5' />
            </div>
            <Badge className='bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'>Completed</Badge>
          </div>
          <h3 className='text-lg font-semibold'>Layer 4 + Full REST API</h3>
          <p className='text-muted-foreground text-sm leading-relaxed'>
            LoRA/QLoRA fine-tuning with DP-SGD privacy guarantees. 52 REST API endpoints covering the complete
            pipeline. Docker Compose deployment with PostgreSQL and MLflow.
          </p>
          <div className='flex flex-wrap gap-1.5'>
            <Badge variant='outline' className='text-xs'>
              DP-SGD
            </Badge>
            <Badge variant='outline' className='text-xs'>
              52 endpoints
            </Badge>
            <Badge variant='outline' className='text-xs'>
              Docker
            </Badge>
          </div>
        </CardContent>
      </Card>
    )
  },
  {
    title: 'Q1 2026 — Gateway & Connectors',
    content: (
      <Card className='max-w-sm shadow-none'>
        <CardContent className='space-y-3'>
          <div className='flex items-center gap-2'>
            <div className='bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 flex size-10 items-center justify-center rounded-lg'>
              <NetworkIcon className='size-5' />
            </div>
            <Badge className='bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'>Completed</Badge>
          </div>
          <h3 className='text-lg font-semibold'>LLM Gateway & Connector Hub</h3>
          <p className='text-muted-foreground text-sm leading-relaxed'>
            Universal LLM Gateway with privacy interception on all traffic. Provider Registry with Fernet-encrypted
            API keys. WhatsApp and webhook connectors. Privacy Interceptor with audit/warn/block modes. Dashboard UI.
          </p>
          <div className='flex flex-wrap gap-1.5'>
            <Badge variant='outline' className='text-xs'>
              LLM Gateway
            </Badge>
            <Badge variant='outline' className='text-xs'>
              Connectors
            </Badge>
            <Badge variant='outline' className='text-xs'>
              Privacy Interceptor
            </Badge>
          </div>
        </CardContent>
      </Card>
    )
  },
  {
    title: 'Q1 2026 — E2B Cloud Sandboxes',
    content: (
      <Card className='max-w-sm border-primary/30 shadow-none'>
        <CardContent className='space-y-3'>
          <div className='flex items-center gap-2'>
            <div className='bg-primary/10 text-primary flex size-10 items-center justify-center rounded-lg'>
              <CloudIcon className='size-5' />
            </div>
            <Badge className='bg-primary/10 text-primary'>Current</Badge>
          </div>
          <h3 className='text-lg font-semibold'>Parallel Sandboxes & Instant Demos</h3>
          <p className='text-muted-foreground text-sm leading-relaxed'>
            E2B MicroVM parallel generation — one sandbox per seed, up to 20 concurrent. Instant demo containers for 6
            industry verticals. Opik LLM-as-judge evaluation sandboxes. SSE real-time streaming. Artifact export before
            auto-destruction.
          </p>
          <div className='flex flex-wrap gap-1.5'>
            <Badge variant='outline' className='text-xs'>
              E2B sandboxes
            </Badge>
            <Badge variant='outline' className='text-xs'>
              Demo containers
            </Badge>
            <Badge variant='outline' className='text-xs'>
              Opik evaluation
            </Badge>
          </div>
        </CardContent>
      </Card>
    )
  },
  {
    title: 'Q2 2026 — Multi-Domain Expansion',
    content: (
      <Card className='max-w-sm shadow-none'>
        <CardContent className='space-y-3'>
          <div className='bg-primary/10 text-primary flex size-10 items-center justify-center rounded-lg'>
            <GlobeIcon className='size-5' />
          </div>
          <h3 className='text-lg font-semibold'>Domain Templates & MCP Server</h3>
          <p className='text-muted-foreground text-sm leading-relaxed'>
            Domain-specific seed templates for all 6 industries. MCP (Model Context Protocol) server for IDE
            integration. Advanced WhatsApp parser improvements and CRM connector.
          </p>
          <div className='flex flex-wrap gap-1.5'>
            <Badge variant='outline' className='text-xs'>
              Seed templates
            </Badge>
            <Badge variant='outline' className='text-xs'>
              MCP server
            </Badge>
            <Badge variant='outline' className='text-xs'>
              CRM connector
            </Badge>
          </div>
        </CardContent>
      </Card>
    )
  },
  {
    title: 'Q3 2026 — Community & Distribution',
    content: (
      <Card className='max-w-sm shadow-none'>
        <CardContent className='space-y-3'>
          <div className='bg-primary/10 text-primary flex size-10 items-center justify-center rounded-lg'>
            <UsersIcon className='size-5' />
          </div>
          <h3 className='text-lg font-semibold'>PyPI, Plugins & Marketplace</h3>
          <p className='text-muted-foreground text-sm leading-relaxed'>
            PyPI package distribution with optional extras (ml, privacy, all). Plugin system for custom evaluators and
            generators. Community seed marketplace for shared domain templates.
          </p>
          <div className='flex flex-wrap gap-1.5'>
            <Badge variant='outline' className='text-xs'>
              pip install uncase
            </Badge>
            <Badge variant='outline' className='text-xs'>
              Plugins
            </Badge>
            <Badge variant='outline' className='text-xs'>
              Marketplace
            </Badge>
          </div>
        </CardContent>
      </Card>
    )
  },
  {
    title: 'Q4 2026 — Enterprise',
    content: (
      <Card className='max-w-sm shadow-none'>
        <CardContent className='space-y-3'>
          <div className='bg-primary/10 text-primary flex size-10 items-center justify-center rounded-lg'>
            <BuildingIcon className='size-5' />
          </div>
          <h3 className='text-lg font-semibold'>Enterprise & Audit Dashboard</h3>
          <p className='text-muted-foreground text-sm leading-relaxed'>
            Enterprise features: team management, role-based access, audit dashboard with full traceability from seed to
            adapter. SaaS platform with managed infrastructure.
          </p>
          <div className='flex flex-wrap gap-1.5'>
            <Badge variant='outline' className='text-xs'>
              Audit dashboard
            </Badge>
            <Badge variant='outline' className='text-xs'>
              RBAC
            </Badge>
            <Badge variant='outline' className='text-xs'>
              SaaS
            </Badge>
          </div>
        </CardContent>
      </Card>
    )
  }
]

const Roadmap = () => {
  return (
    <section id='roadmap'>
      <MotionPreset
        fade
        slide={{ direction: 'down', offset: 50 }}
        blur
        transition={{ duration: 0.5 }}
        className='text-center'
      >
        <p className='text-primary text-sm font-medium uppercase'>Roadmap</p>
      </MotionPreset>
      <JourneyTimeline data={roadmapData} />
    </section>
  )
}

export default Roadmap
