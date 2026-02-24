'use client'

import {
  BookOpenIcon,
  BrainCircuitIcon,
  BuildingIcon,
  CpuIcon,
  GlobeIcon,
  RocketIcon,
  ShieldCheckIcon,
  UsersIcon
} from 'lucide-react'

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
          <div className='bg-primary/10 text-primary flex size-10 items-center justify-center rounded-lg'>
            <BookOpenIcon className='size-5' />
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
          <div className='bg-primary/10 text-primary flex size-10 items-center justify-center rounded-lg'>
            <BrainCircuitIcon className='size-5' />
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
          <div className='bg-primary/10 text-primary flex size-10 items-center justify-center rounded-lg'>
            <ShieldCheckIcon className='size-5' />
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
    title: 'Q4 2025 — LoRA Pipeline',
    content: (
      <Card className='max-w-sm shadow-none'>
        <CardContent className='space-y-3'>
          <div className='bg-primary/10 text-primary flex size-10 items-center justify-center rounded-lg'>
            <CpuIcon className='size-5' />
          </div>
          <h3 className='text-lg font-semibold'>Layer 4: Training Pipeline</h3>
          <p className='text-muted-foreground text-sm leading-relaxed'>
            LoRA/QLoRA fine-tuning with DP-SGD privacy guarantees. 10 chat format exports (ChatML, Alpaca, LLaMA,
            Mistral, Qwen, and more). MLflow experiment tracking.
          </p>
          <div className='flex flex-wrap gap-1.5'>
            <Badge variant='outline' className='text-xs'>
              DP-SGD
            </Badge>
            <Badge variant='outline' className='text-xs'>
              10 formats
            </Badge>
            <Badge variant='outline' className='text-xs'>
              MLflow
            </Badge>
          </div>
        </CardContent>
      </Card>
    )
  },
  {
    title: 'Q1 2026 — Platform Launch',
    content: (
      <Card className='max-w-sm shadow-none'>
        <CardContent className='space-y-3'>
          <div className='bg-primary/10 text-primary flex size-10 items-center justify-center rounded-lg'>
            <RocketIcon className='size-5' />
          </div>
          <h3 className='text-lg font-semibold'>API, Docker & Documentation</h3>
          <p className='text-muted-foreground text-sm leading-relaxed'>
            REST API with versioned endpoints. Docker Compose deployment (API + PostgreSQL + MLflow). Bilingual
            documentation (EN/ES) with Haiku doc-agent for auto-translation.
          </p>
          <div className='flex flex-wrap gap-1.5'>
            <Badge variant='outline' className='text-xs'>
              REST API
            </Badge>
            <Badge variant='outline' className='text-xs'>
              Docker
            </Badge>
            <Badge variant='outline' className='text-xs'>
              Bilingual docs
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
          <h3 className='text-lg font-semibold'>6 Industry Namespaces</h3>
          <p className='text-muted-foreground text-sm leading-relaxed'>
            Full support for automotive, medical, legal, finance, industrial, and education domains. WhatsApp chat
            parser. Domain-specific quality thresholds and seed templates.
          </p>
          <div className='flex flex-wrap gap-1.5'>
            <Badge variant='outline' className='text-xs'>
              6 domains
            </Badge>
            <Badge variant='outline' className='text-xs'>
              WhatsApp parser
            </Badge>
            <Badge variant='outline' className='text-xs'>
              Seed templates
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
          <h3 className='text-lg font-semibold'>PyPI, Plugins & Community</h3>
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
