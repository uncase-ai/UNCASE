# Architecture

## System Overview

```
                                   UNCASE Architecture

  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  Clients                                                                     │
  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐          │
  │  │Dashboard │  │  CLI    │  │REST API │  │  MCP    │  │Webhooks │          │
  │  │(Next.js) │  │(Typer)  │  │(FastAPI)│  │(FastMCP)│  │(JSON)   │          │
  │  └────┬─────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘          │
  │       └──────────────┴───────────┬┴────────────┴────────────┘               │
  │                                  │                                           │
  │  ┌───────────────────────────────▼──────────────────────────────────────┐    │
  │  │  API Layer — 85+ endpoints across 22 routers                          │    │
  │  │  /health  /auth  /seeds  /generate  /evaluations  /templates         │    │
  │  │  /tools  /providers  /connectors  /gateway  /organizations  /import  │    │
  │  │  /sandbox  /plugins  /pipeline  /jobs  /knowledge  /usage            │    │
  │  │  /webhooks  /e2b-webhooks  /audit  /costs  /metrics                  │    │
  │  └───────────────────────────────┬──────────────────────────────────────┘    │
  │                                  │                                           │
  │  ┌───────────────────────────────▼──────────────────────────────────────┐    │
  │  │  Service Layer — Business logic, orchestration                        │    │
  │  │  GeneratorService  EvaluatorService  ProviderService  SeedService     │    │
  │  └───────────────────────────────┬──────────────────────────────────────┘    │
  │                                  │                                           │
  │  ┌──────────┬──────────┬─────────┴──┬──────────┬──────────┐                 │
  │  │ Layer 0  │ Layer 1  │  Layer 2   │ Layer 3  │ Layer 4  │                 │
  │  │ PII &    │ Parser & │  Quality   │ Synth    │ LoRA     │                 │
  │  │ Privacy  │ Validate │  Evaluate  │ Generate │ Pipeline │                 │
  │  └──────────┴──────────┴────────────┴──────────┴──────────┘                 │
  │                                  │                                           │
  │  ┌───────────────────────────────▼──────────────────────────────────────┐    │
  │  │  Sandbox Layer (optional — E2B Cloud)                                │    │
  │  │  E2BSandboxOrchestrator  │  DemoSandboxOrchestrator                  │    │
  │  │  OpikSandboxRunner       │  SandboxExporter                          │    │
  │  └───────────────────────────────┬──────────────────────────────────────┘    │
  │                                  │                                           │
  │  ┌───────────────────────────────▼──────────────────────────────────────┐    │
  │  │  Infrastructure                                                       │    │
  │  │  PostgreSQL (async)  │  LiteLLM Gateway  │  Fernet Encryption         │    │
  │  │  Alembic Migrations  │  structlog (JSON)  │  MLflow Tracking           │    │
  │  └──────────────────────────────────────────────────────────────────────┘    │
  │                                                                              │
  └──────────────────────────────────────────────────────────────────────────────┘
```

## SCSF 5-Layer Pipeline

| Layer | Module | Status | Purpose |
|---|---|---|---|
| **Layer 0** | `core/privacy/` | Complete | PII detection (9 regex + Presidio NER), anonymization, gateway interception |
| **Layer 1** | `core/parser/` | Complete | Multi-format parsing (CSV, JSONL, WhatsApp, Webhook), format detection |
| **Layer 2** | `core/evaluator/` | Complete | 6 quality metrics, composite scoring, pass/fail certification |
| **Layer 3** | `core/generator/` | Complete | LiteLLM-based generation, provider routing, seed-guided prompts |
| **Layer 4** | `core/lora_pipeline/` | Scaffolded | LoRA/QLoRA fine-tuning with DP-SGD (planned) |

**Data flow:**
```
Real Conversation → [Layer 0: PII Removal] → SeedSchema v1
    → [Layer 1: Parsing + Validation] → Internal SCSF schema
    → [Layer 2: Quality Evaluation] → Validated seeds
    → [Layer 3: Synthetic Generation] → Synthetic conversations
    → [Layer 2: Re-evaluation] → Certified data
    → [Layer 4: LoRA Pipeline] → LoRA adapter
    → Production → Feedback → [Layer 0] (flywheel loop)
```

## Project Structure

```
uncase/
├── api/                        # FastAPI REST API
│   ├── main.py                 # App factory, CORS, lifespan
│   ├── middleware.py           # Exception handlers
│   ├── deps.py                 # Dependency injection
│   └── routers/                # 22 routers, 85+ endpoints
│       ├── health.py           #   GET /health, GET /health/db
│       ├── auth.py             #   POST /api/v1/auth/{login,refresh,verify}
│       ├── seeds.py            #   CRUD /api/v1/seeds
│       ├── generation.py       #   POST /api/v1/generate
│       ├── evaluations.py      #   POST /api/v1/evaluations{,/batch}
│       ├── templates.py        #   CRUD /api/v1/templates + render
│       ├── tools.py            #   CRUD /api/v1/tools + execute, search
│       ├── providers.py        #   CRUD /api/v1/providers + test
│       ├── connectors.py       #   /api/v1/connectors (whatsapp, webhook, pii)
│       ├── gateway.py          #   POST /api/v1/gateway/chat
│       ├── organizations.py    #   CRUD /api/v1/organizations + API keys
│       ├── imports.py          #   POST /api/v1/import/{csv,jsonl}
│       ├── sandbox.py          #   /api/v1/sandbox (generate, stream, demo, evaluate)
│       ├── plugins.py          #   CRUD /api/v1/plugins + install/uninstall
│       ├── pipeline.py         #   POST /api/v1/pipeline/run + status
│       ├── jobs.py             #   CRUD /api/v1/jobs + cancel
│       ├── knowledge.py        #   CRUD /api/v1/knowledge + upload/search
│       ├── usage.py            #   GET /api/v1/usage/summary + breakdown
│       ├── webhooks.py         #   CRUD /api/v1/webhooks + deliveries
│       ├── e2b_webhooks.py     #   POST /api/v1/webhooks/e2b/{start,complete,error}
│       ├── audit.py            #   GET /api/v1/audit/logs + export
│       └── costs.py            #   GET /api/v1/costs/summary + by-org
├── cli/                        # Typer CLI (seed, template, tool, import, evaluate)
├── connectors/                 # Data source connectors
│   ├── base.py                 # Abstract BaseConnector
│   ├── whatsapp.py             # WhatsApp export parser
│   └── webhook.py              # JSON webhook receiver
├── core/
│   ├── privacy/                # PII scanner + gateway interceptor
│   │   ├── scanner.py          # PIIScanner (regex + Presidio)
│   │   └── interceptor.py      # PrivacyInterceptor (audit/warn/block)
│   ├── parser/                 # CSV, JSONL parsers + format detection
│   ├── evaluator/              # Quality engine
│   │   ├── evaluator.py        # ConversationEvaluator orchestrator
│   │   └── metrics/            # ROUGE-L, fidelity, diversity, coherence, privacy
│   ├── generator/              # LiteLLM synthetic generation
│   └── lora_pipeline/          # LoRA fine-tuning (scaffolded)
├── schemas/                    # Pydantic v2 models
│   ├── seed.py                 # SeedSchema v1
│   ├── conversation.py         # Conversation, ConversationTurn
│   ├── quality.py              # QualityReport, QualityThresholds
│   ├── generation.py           # GenerateRequest/Response
│   ├── provider.py             # Provider CRUD schemas
│   ├── connector.py            # Connector import/scan schemas
│   └── ...
├── services/                   # Business logic layer
│   ├── generator.py            # GeneratorService
│   ├── evaluator.py            # EvaluatorService
│   ├── provider.py             # ProviderService (Fernet encryption)
│   ├── seed.py                 # SeedService (CRUD)
│   └── organization.py         # OrganizationService
├── templates/                  # 10 chat template renderers
├── tools/                      # Tool definition, registry, execution
├── db/                         # PostgreSQL async (SQLAlchemy + asyncpg)
│   ├── models/                 # DB models
│   └── engine.py               # Async engine lifecycle
├── sandbox/                    # E2B cloud sandbox execution
│   ├── schemas.py              # 20+ Pydantic models for sandbox lifecycle
│   ├── e2b_client.py           # E2BSandboxOrchestrator (fan-out, SSE streaming)
│   ├── worker.py               # Self-contained script running inside sandboxes
│   ├── demo.py                 # DemoSandboxOrchestrator (6 industry verticals)
│   ├── opik_runner.py          # OpikSandboxRunner (LLM-as-judge evaluation)
│   ├── exporter.py             # SandboxExporter (artifact persistence)
│   └── template_builder.py     # Custom E2B template Dockerfile generation
├── mcp/                        # Model Context Protocol server
└── config.py                   # Pydantic-settings configuration
```

## Database Schema

```
  ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
  │  organizations   │       │    api_keys      │       │ api_key_audit   │
  │─────────────────│       │─────────────────│       │     _logs        │
  │ id (PK)         │◀──┐   │ id (PK)         │◀──┐   │─────────────────│
  │ name            │   │   │ key_hash        │   │   │ id (PK)         │
  │ slug (unique)   │   │   │ key_prefix      │   │   │ action          │
  │ is_active       │   └───│ organization_id  │   └───│ api_key_id      │
  │ created_at      │       │ scopes          │       │ ip_address      │
  └────────┬────────┘       │ expires_at      │       │ created_at      │
           │                └─────────────────┘       └─────────────────┘
           │
     ┌─────┴──────────────────────┐
     │                            │
     ▼                            ▼
  ┌─────────────────┐       ┌─────────────────┐
  │     seeds        │       │  llm_providers   │
  │─────────────────│       │─────────────────│
  │ id (PK)         │       │ id (PK)         │
  │ dominio         │       │ name            │
  │ idioma          │       │ provider_type   │
  │ objetivo        │       │ api_key_encrypted│
  │ tono            │       │ api_base        │
  │ roles (JSON)    │       │ default_model   │
  │ pasos_turnos    │       │ is_default      │
  │ parametros      │       │ is_active       │
  │ organization_id  │       │ organization_id  │
  └────────┬────────┘       └─────────────────┘
           │
           ▼
  ┌─────────────────┐
  │evaluation_reports│
  │─────────────────│
  │ id (PK)         │
  │ seed_id (FK)    │
  │ rouge_l         │
  │ fidelidad       │
  │ diversidad      │
  │ coherencia      │
  │ privacy_score   │
  │ composite_score │
  │ passed          │
  └─────────────────┘
```

8 Alembic migrations manage schema evolution (0001-initial through 0008-audit-logs).
