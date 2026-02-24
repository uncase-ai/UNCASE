<p align="center">
  <img src="frontend/public/logo.svg" alt="UNCASE Logo" width="120" height="120" />
</p>

<h1 align="center">UNCASE</h1>

<p align="center">
  <strong>Unbiased Neutral Convention for Agnostic Seed Engineering</strong>
</p>

<p align="center">
  The open-source framework for generating high-quality synthetic conversational data<br/>
  for LoRA/QLoRA fine-tuning in regulated industries — without exposing real data.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="License" /></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/python-≥3.11-blue.svg" alt="Python" /></a>
  <a href="https://docs.astral.sh/ruff/"><img src="https://img.shields.io/badge/code%20style-ruff-000000.svg" alt="Ruff" /></a>
  <a href="#"><img src="https://img.shields.io/badge/tests-309%20passing-brightgreen.svg" alt="Tests" /></a>
  <a href="#"><img src="https://img.shields.io/badge/coverage-73%25-green.svg" alt="Coverage" /></a>
  <a href="#"><img src="https://img.shields.io/badge/API%20endpoints-47-purple.svg" alt="Endpoints" /></a>
</p>

---

## The Problem

Organizations in healthcare, finance, legal, and manufacturing **need specialized LLMs** but face an impossible tradeoff:

- **Fine-tuning requires real conversations** — but real conversations contain PII, PHI, financial records, and legally privileged information that cannot leave the building.
- **Anonymization alone is not enough** — masked data loses the domain-specific patterns that make fine-tuning valuable.
- **Synthetic data generators produce garbage** — generic tools create conversations that sound plausible but fail on domain accuracy, factual consistency, and regulatory compliance.
- **No unified pipeline exists** — teams stitch together 6-10 different tools (parsers, anonymizers, generators, evaluators, training scripts) with bespoke glue code that breaks on every update.

**The result:** Most organizations either give up on specialization, or they risk compliance violations by feeding real data into cloud APIs.

---

## The Solution

UNCASE is a **complete, privacy-first pipeline** that transforms real conversations into certified synthetic training data without any real PII ever leaving your infrastructure.

```
                              UNCASE — Synthetic Conversational Seed Framework (SCSF)

  ┌─────────────────────────────────────────────────────────────────────────────────────────┐
  │                                                                                         │
  │   Real Conversations                                                                    │
  │   (WhatsApp, CRM, Webhook)                                                              │
  │          │                                                                              │
  │          ▼                                                                              │
  │   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
  │   │   Layer 0    │    │   Layer 1    │    │   Layer 2    │    │   Layer 3    │          │
  │   │              │    │              │    │              │    │              │          │
  │   │  PII Scan &  │───▶│  Parse &     │───▶│  Quality     │───▶│  Synthetic   │          │
  │   │  Anonymize   │    │  Validate    │    │  Evaluate    │    │  Generate    │          │
  │   │              │    │              │    │              │    │              │          │
  │   │  9 regex +   │    │  CSV, JSONL  │    │  ROUGE-L     │    │  LiteLLM     │          │
  │   │  Presidio    │    │  WhatsApp    │    │  Fidelity    │    │  Claude      │          │
  │   │  NER         │    │  Webhook     │    │  Diversity   │    │  GPT-4       │          │
  │   │              │    │  OpenAI fmt  │    │  Coherence   │    │  Gemini      │          │
  │   │  Zero PII    │    │  ShareGPT    │    │  Privacy     │    │  Ollama      │          │
  │   │  tolerance   │    │              │    │  gate        │    │  vLLM        │          │
  │   └──────────────┘    └──────────────┘    └──────────────┘    └──────┬───────┘          │
  │                                                                      │                  │
  │                                                    ┌─────────────────┘                  │
  │                                                    ▼                                    │
  │   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                              │
  │   │   Layer 4    │    │   Export     │    │  Re-evaluate │                              │
  │   │              │    │              │    │              │                              │
  │   │  LoRA/QLoRA  │◀───│  10 Chat     │◀───│  Certified   │                              │
  │   │  Fine-tune   │    │  Templates   │    │  Synthetics  │                              │
  │   │              │    │              │    │              │                              │
  │   │  DP-SGD      │    │  Llama, GPT  │    │  Q = min()   │                              │
  │   │  ε ≤ 8.0     │    │  Mistral...  │    │  if PII = 0  │                              │
  │   └──────────────┘    └──────────────┘    └──────────────┘                              │
  │                                                                                         │
  └─────────────────────────────────────────────────────────────────────────────────────────┘
```

**One command. One pipeline. Zero PII.**

---

## What Makes UNCASE Different

| Feature | Generic Generators | Enterprise Platforms | **UNCASE** |
|---|---|---|---|
| Privacy-first architecture | No | Partial | **Zero PII tolerance, enforced by pipeline** |
| Regulated industry focus | No | Limited | **Healthcare, finance, legal, manufacturing** |
| Open source | Sometimes | No | **Apache 2.0, fully open** |
| Seed-based generation | No | No | **Deterministic, traceable, reproducible** |
| Quality gates with metrics | No | Basic | **6 metrics with hard thresholds** |
| Multi-provider LLM gateway | No | Vendor lock-in | **Any LLM via unified gateway** |
| PII scanning on ALL traffic | No | No | **Outbound + inbound interception** |
| 10 fine-tuning export formats | No | 1-2 | **Every major model family** |
| Tool-use training data | No | No | **Built-in tool simulation** |
| Full pipeline (import to LoRA) | No | Partial | **5 layers, end-to-end** |

### The Seed Paradigm

Unlike traditional synthetic data tools that generate from prompts, UNCASE uses a **Seed Schema** — a structured blueprint that captures the DNA of a conversation without containing any real data:

```json
{
  "seed_id": "auto-001",
  "dominio": "automotive.sales",
  "idioma": "es",
  "objetivo": "Customer negotiating price on a certified pre-owned SUV",
  "tono": "professional, empathetic",
  "roles": ["customer", "sales_advisor"],
  "pasos_turnos": [
    "Customer expresses interest in specific vehicle",
    "Advisor runs inventory search",
    "Customer asks about financing options",
    "Advisor presents payment plans"
  ],
  "parametros_factuales": {
    "vehicle_type": "SUV",
    "price_range": "25000-40000",
    "financing_available": true
  }
}
```

Seeds are **traceable** (every synthetic conversation maps back to its seed), **reproducible** (same seed + same config = consistent output), and **auditable** (regulators can inspect seeds without seeing real data).

---

## Features

### LLM Gateway with Privacy Interception

Route requests to **any LLM provider** through a single endpoint. Every message is scanned for PII before it leaves your infrastructure and after the response arrives.

```bash
# Chat through the gateway — PII is intercepted automatically
curl -X POST http://localhost:8000/api/v1/gateway/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Summarize this patient record..."}],
    "provider_id": "my-claude-provider",
    "privacy_mode": "block"
  }'
```

**Three privacy modes:**
- **audit** — Scan and log PII detections (default)
- **warn** — Scan, log, and include warnings in the response
- **block** — Reject any request or response containing PII

**Supported providers:**

| Provider | Type | Connection |
|---|---|---|
| Anthropic (Claude) | Cloud | API key |
| OpenAI (GPT-4) | Cloud | API key |
| Google (Gemini) | Cloud | API key |
| Groq | Cloud | API key |
| Ollama | Local | API base URL |
| vLLM | Local | API base URL |
| Custom (OpenAI-compatible) | Any | API base URL + optional key |

All API keys are **Fernet-encrypted at rest** — never stored in plaintext.

### Data Connectors with Built-in Anonymization

Import conversations from any source. PII is stripped **before** data enters the pipeline.

```bash
# WhatsApp export — parses iOS and Android formats
curl -X POST http://localhost:8000/api/v1/connectors/whatsapp \
  -F "file=@chat_export.txt"

# Webhook — receive from CRM, helpdesk, or any system
curl -X POST http://localhost:8000/api/v1/connectors/webhook \
  -H "Content-Type: application/json" \
  -d '{"conversations": [{"turns": [{"role": "user", "content": "..."}]}]}'

# CSV and JSONL files
curl -X POST http://localhost:8000/api/v1/import/csv -F "file=@data.csv"
curl -X POST http://localhost:8000/api/v1/import/jsonl -F "file=@data.jsonl"

# Preview PII detection before importing
curl -X POST http://localhost:8000/api/v1/connectors/scan-pii \
  -d "Call John at 555-123-4567 or john@example.com"
```

**PII detection — dual strategy:**

| Category | Method | Token |
|---|---|---|
| Email addresses | Regex | `[EMAIL]` |
| Phone (international) | Regex | `[PHONE]` |
| Phone (local) | Regex | `[PHONE]` |
| SSN (US) | Regex | `[SSN]` |
| CURP (Mexico) | Regex | `[CURP]` |
| RFC (Mexico) | Regex | `[RFC]` |
| Credit card numbers | Regex | `[CREDIT_CARD]` |
| IP addresses | Regex | `[IP_ADDRESS]` |
| IBAN | Regex | `[IBAN]` |
| Person names | Presidio NER | `[PERSON]` |
| Locations | Presidio NER | `[LOCATION]` |
| Dates | Presidio NER | `[DATE]` |
| Medical licenses | Presidio NER | `[LICENSE]` |
| Bank accounts | Presidio NER | `[BANK_ACCOUNT]` |
| Passport numbers | Presidio NER | `[PASSPORT]` |
| Driver's license | Presidio NER | `[DRIVER_LICENSE]` |

Regex heuristics are **always active**. Presidio NER is an optional upgrade via the `[privacy]` extra for higher accuracy on unstructured text.

### Quality Evaluation Engine

Every generated conversation is scored against **6 mandatory metrics** with hard thresholds:

| Metric | Threshold | What It Measures |
|---|---|---|
| ROUGE-L | >= 0.65 | Structural coherence with the seed |
| Factual Fidelity | >= 0.90 | Accuracy of domain-specific facts |
| Lexical Diversity (TTR) | >= 0.55 | Vocabulary richness |
| Dialogic Coherence | >= 0.85 | Inter-turn consistency |
| Privacy Score | = 0.00 | Zero residual PII |
| Memorization | < 0.01 | Extraction attack success rate |

**Composite score formula:**

```
Q = min(ROUGE-L, Fidelity, TTR, Coherence)
    if privacy == 0.0 AND memorization < 0.01
    else Q = 0.0
```

If **any** privacy check fails, the entire conversation is rejected — regardless of how well it scores on other metrics.

### Synthetic Generation with Provider Routing

Generate conversations using **any configured provider** with automatic quality evaluation:

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "seed": { "seed_id": "auto-001", "dominio": "automotive.sales", ... },
    "count": 10,
    "provider_id": "my-ollama-local",
    "temperature": 0.7,
    "evaluate_after": true
  }'
```

The generation pipeline:
1. Resolves the LLM provider (explicit ID or default)
2. Builds domain-aware prompts from the seed schema
3. Generates N conversations via LiteLLM
4. Runs quality evaluation on each conversation
5. Returns only certified synthetics with full quality reports

### 10 Fine-Tuning Export Formats

Export certified conversations in the exact chat template format required by any major model family:

```bash
# CLI export
uncase template export conversations.json llama -o train_llama.txt
uncase template export conversations.json chatml -o train_chatml.txt
uncase template export conversations.json mistral -o train_mistral.txt

# API export
curl -X POST http://localhost:8000/api/v1/templates/export \
  -H "Content-Type: application/json" \
  -d '{"conversations": [...], "template_name": "qwen"}'
```

| Format | Template | Tool Support | Target Models |
|---|---|---|---|
| ChatML | `chatml` | Yes | GPT-4, Qwen (base), Yi |
| Harmony | `harmony` | Yes | Cohere Command R+ |
| Llama 3/4 | `llama` | Yes | LLaMA 3/3.1/4 |
| Mistral | `mistral` | Yes | Mistral, Mixtral |
| Qwen 3 | `qwen` | Yes | Qwen 3, Qwen 2.5 |
| Nemotron | `nemotron` | Yes | NVIDIA Nemotron |
| Kimi | `moonshot` | Yes | Moonshot Kimi |
| MiniMax | `minimax` | Yes | MiniMax |
| OpenAI API | `openai_api` | Yes | Any model via OpenAI API |
| Alpaca | `alpaca` | No | Instruction-style models |

All templates support **tool-use training data** with three modes: native, function_calling, and inline.

### Tool-Use Training Data

Define, register, and simulate tools to generate training data with realistic tool-calling patterns:

```bash
# List registered tools
uncase tool list --domain automotive.sales

# Simulate a tool call
curl -X POST http://localhost:8000/api/v1/tools/buscar_inventario/simulate \
  -H "Content-Type: application/json" \
  -d '{"marca": "Toyota", "tipo": "SUV"}'
```

**5 built-in automotive tools** (pilot domain):
- `buscar_inventario` — Vehicle inventory search with filters
- `cotizar_vehiculo` — Price quote generation
- `consultar_financiamiento` — Financing options lookup
- `comparar_modelos` — Side-by-side model comparison
- `consultar_crm` — Customer record lookup

### MCP Server (Model Context Protocol)

UNCASE exposes tools directly to Claude Code, AI agents, and any MCP-compatible client:

- `check_health` — API status and version
- `list_domains` — Supported industry domains
- `get_quality_thresholds` — Metric thresholds and formula
- `validate_seed` — Validate seeds against SeedSchema v1
- `list_templates` — Available export formats
- `render_template` — Render conversations in any template
- `list_tools` — Registered tools
- `simulate_tool` — Execute tool simulations

Mount point: `http://localhost:8000/mcp`

### Full-Stack Dashboard

A Next.js 16 dashboard provides a visual interface for the entire SCSF pipeline:

| Route | Purpose |
|---|---|
| `/dashboard` | Overview and statistics |
| `/dashboard/pipeline/import` | Import conversations from files |
| `/dashboard/pipeline/seeds` | Create and manage seeds |
| `/dashboard/pipeline/generate` | Generate synthetic conversations |
| `/dashboard/pipeline/evaluate` | Run quality evaluations |
| `/dashboard/pipeline/export` | Export in any template format |
| `/dashboard/conversations` | Browse imported conversations |
| `/dashboard/templates` | View available formats |
| `/dashboard/tools` | Tool registry browser |
| `/dashboard/evaluations` | Quality reports |
| `/dashboard/settings` | Configuration |

---

## Architecture

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
  │  │  API Layer — 47 endpoints across 11 routers                          │    │
  │  │  /health  /seeds  /generate  /evaluations  /templates  /tools        │    │
  │  │  /providers  /connectors  /gateway  /organizations  /import          │    │
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
  │  │  Infrastructure                                                       │    │
  │  │  PostgreSQL (async)  │  LiteLLM Gateway  │  Fernet Encryption         │    │
  │  │  Alembic Migrations  │  structlog (JSON)  │  MLflow Tracking           │    │
  │  └──────────────────────────────────────────────────────────────────────┘    │
  │                                                                              │
  └──────────────────────────────────────────────────────────────────────────────┘
```

### SCSF 5-Layer Pipeline

| Layer | Module | Status | Purpose |
|---|---|---|---|
| **Layer 0** | `core/privacy/` | Complete | PII detection (9 regex + Presidio NER), anonymization, gateway interception |
| **Layer 1** | `core/parser/` | Complete | Multi-format parsing (CSV, JSONL, WhatsApp, Webhook), format detection |
| **Layer 2** | `core/evaluator/` | Complete | 6 quality metrics, composite scoring, pass/fail certification |
| **Layer 3** | `core/generator/` | Complete | LiteLLM-based generation, provider routing, seed-guided prompts |
| **Layer 4** | `core/lora_pipeline/` | Scaffolded | LoRA/QLoRA fine-tuning with DP-SGD (planned) |

### Project Structure

```
uncase/
├── api/                        # FastAPI REST API
│   ├── main.py                 # App factory, CORS, lifespan
│   ├── middleware.py           # Exception handlers
│   ├── deps.py                 # Dependency injection
│   └── routers/                # 11 routers, 47 endpoints
│       ├── health.py           #   GET /health, GET /health/db
│       ├── seeds.py            #   CRUD /api/v1/seeds
│       ├── generation.py       #   POST /api/v1/generate
│       ├── evaluations.py      #   POST /api/v1/evaluations{,/batch}
│       ├── templates.py        #   GET/POST /api/v1/templates
│       ├── tools.py            #   CRUD /api/v1/tools
│       ├── providers.py        #   CRUD /api/v1/providers + test
│       ├── connectors.py       #   /api/v1/connectors (whatsapp, webhook, pii)
│       ├── gateway.py          #   POST /api/v1/gateway/chat
│       ├── organizations.py    #   CRUD /api/v1/organizations + API keys
│       └── imports.py          #   POST /api/v1/import/{csv,jsonl}
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
│   ├── models/                 # 6 tables across 3 migrations
│   └── engine.py               # Async engine lifecycle
├── mcp/                        # Model Context Protocol server
└── config.py                   # Pydantic-settings configuration
```

### Database Schema

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

---

## Installation

### Option 1: Git + uv (recommended for development)

```bash
git clone https://github.com/uncase-ai/uncase.git
cd uncase
uv sync                        # Core dependencies
uv sync --extra dev            # + development tools
uv sync --extra all            # Everything (dev + ml + privacy)
```

### Option 2: pip

```bash
pip install uncase                       # Core framework
pip install "uncase[dev]"                # + development (pytest, ruff, mypy)
pip install "uncase[ml]"                 # + machine learning (transformers, peft, trl, torch)
pip install "uncase[privacy]"            # + enhanced PII detection (SpaCy + Presidio)
pip install "uncase[all]"                # Everything
```

### Option 3: Docker

```bash
# API + PostgreSQL
docker compose up -d

# With MLflow tracking
docker compose --profile ml up -d

# With NVIDIA GPU support
docker compose --profile gpu up -d
```

| Service | Port | Profile | Description |
|---|---|---|---|
| `api` | 8000 | default | UNCASE FastAPI server |
| `postgres` | 5432 | default | PostgreSQL 16 |
| `mlflow` | 5000 | `ml` | MLflow tracking server |
| `api-gpu` | 8001 | `gpu` | GPU-accelerated API |

### Available Extras

| Extra | Includes | When You Need It |
|---|---|---|
| *(core)* | FastAPI, Pydantic, LiteLLM, structlog, Typer, SQLAlchemy, cryptography | Always installed |
| `[dev]` | pytest, ruff, mypy, factory-boy, pre-commit | Running tests, contributing |
| `[ml]` | transformers, peft, trl, torch, mlflow, accelerate, bitsandbytes | LoRA fine-tuning |
| `[privacy]` | spacy, presidio-analyzer, presidio-anonymizer | Enhanced NER-based PII detection |
| `[all]` | dev + ml + privacy | Full installation |

---

## Quick Start

### 1. Configure environment

```bash
cp .env.example .env
# Edit .env with your database URL and LLM API keys
```

### 2. Start the API

```bash
make api
# or: uvicorn uncase.api.main:app --reload --port 8000
```

### 3. Register an LLM provider

```bash
curl -X POST http://localhost:8000/api/v1/providers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Claude Provider",
    "provider_type": "anthropic",
    "api_key": "sk-ant-...",
    "default_model": "claude-sonnet-4-20250514",
    "is_default": true
  }'
```

### 4. Import conversations

```bash
# From a WhatsApp export
curl -X POST http://localhost:8000/api/v1/connectors/whatsapp \
  -F "file=@chat.txt"

# From CSV
curl -X POST http://localhost:8000/api/v1/import/csv -F "file=@data.csv"
```

### 5. Generate synthetic data

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "seed": {
      "seed_id": "demo-001",
      "dominio": "automotive.sales",
      "idioma": "es",
      "objetivo": "Customer inquiring about SUV financing",
      "tono": "professional",
      "roles": ["customer", "advisor"],
      "pasos_turnos": ["Greeting", "Inquiry", "Options", "Decision"]
    },
    "count": 5,
    "evaluate_after": true
  }'
```

### 6. Export for fine-tuning

```bash
uncase template export conversations.json llama -o train_data.txt
```

### CLI Reference

```bash
uncase --help                  # All available commands
uncase --version               # Framework version

uncase seed validate seeds.json        # Validate seeds against SeedSchema v1
uncase seed show seeds.json            # Display seeds in table format

uncase template list                   # List all 10 export formats
uncase template export data.json llama # Export for Llama fine-tuning
uncase template preview data.json chatml # Preview rendering

uncase import csv data.csv -o out.json     # Import from CSV
uncase import jsonl data.jsonl -o out.json # Import from JSONL

uncase tool list                       # List registered tools
uncase tool show buscar_inventario     # Tool details

uncase evaluate run convs.json seeds.json  # Run quality evaluation
```

### Makefile

```bash
make help          # All commands
make install       # Core dependencies
make dev           # + dev tools
make dev-all       # Everything
make api           # Start development server
make test          # Full test suite (309 tests)
make test-privacy  # Mandatory privacy tests
make lint          # Ruff linter
make format        # Ruff formatter
make typecheck     # mypy strict mode
make check         # lint + typecheck + tests (pre-PR gate)
make migrate       # Run database migrations
make docker-up     # Start Docker stack
make docker-down   # Stop Docker stack
make clean         # Remove build artifacts
```

---

## Supported Domains

| Domain | Namespace | Status | Built-in Tools |
|---|---|---|---|
| Automotive Sales | `automotive.sales` | Pilot domain | 5 tools |
| Medical Consultation | `medical.consultation` | Planned | -- |
| Legal Advisory | `legal.advisory` | Planned | -- |
| Financial Advisory | `finance.advisory` | Planned | -- |
| Industrial Support | `industrial.support` | Planned | -- |
| Education Tutoring | `education.tutoring` | Planned | -- |

---

## API Reference

### Complete Endpoint Map

| Router | Prefix | Endpoints | Description |
|---|---|---|---|
| **health** | `/health` | 2 | Service status, database connectivity |
| **seeds** | `/api/v1/seeds` | 5 | Seed CRUD (create, list, get, update, delete) |
| **generate** | `/api/v1/generate` | 1 | Synthetic conversation generation |
| **evaluations** | `/api/v1/evaluations` | 3 | Single eval, batch eval, thresholds |
| **templates** | `/api/v1/templates` | 3 | List, render, export |
| **tools** | `/api/v1/tools` | 4 | List, get, register, simulate |
| **providers** | `/api/v1/providers` | 6 | Provider CRUD + connection test |
| **connectors** | `/api/v1/connectors` | 4 | WhatsApp, webhook, PII scan, list |
| **gateway** | `/api/v1/gateway` | 1 | Universal LLM chat proxy |
| **organizations** | `/api/v1/organizations` | 7 | Org CRUD + API key management |
| **import** | `/api/v1/import` | 2 | CSV and JSONL file import |

**Total: 47 endpoints** across 11 routers.

Interactive documentation available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `UNCASE_ENV` | `development` | Environment: development, staging, production |
| `UNCASE_LOG_LEVEL` | `DEBUG` | Logging: DEBUG, INFO, WARNING, ERROR |
| `UNCASE_DEFAULT_LOCALE` | `es` | Default language (es, en) |
| `API_PORT` | `8000` | FastAPI server port |
| `API_SECRET_KEY` | -- | Secret key for Fernet encryption (required) |
| `API_CORS_ORIGINS` | `http://localhost:3000` | Comma-separated CORS origins |
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection string |
| `LITELLM_API_KEY` | -- | Default LLM provider API key |
| `ANTHROPIC_API_KEY` | -- | Claude API key (alternative) |
| `MLFLOW_TRACKING_URI` | `http://localhost:5000` | MLflow tracking server |
| `UNCASE_PII_CONFIDENCE_THRESHOLD` | `0.85` | PII detection confidence (0.0-1.0) |
| `UNCASE_DP_EPSILON` | `8.0` | Differential privacy budget |

---

## Current State

### What's Built and Working

- **309 tests passing**, 73% code coverage
- **47 REST API endpoints** across 11 routers
- **5 SCSF layers** (4 complete, 1 scaffolded)
- **10 chat template** export formats with tool-use support
- **6 quality metrics** with automated pass/fail certification
- **Dual-strategy PII detection** (regex + optional Presidio NER)
- **LLM gateway** with privacy interception on all traffic
- **Provider registry** with Fernet-encrypted key storage
- **Data connectors** for WhatsApp, webhook, CSV, JSONL
- **Full-stack dashboard** with 18 routes (Next.js 16)
- **MCP server** for AI agent integration
- **CLI** with 20+ commands
- **Docker Compose** with PostgreSQL, MLflow, GPU support
- **Automated deployment** via Vercel + deploy.sh

### What's Next

- **Layer 4: LoRA Pipeline** — Dataset preparation from certified conversations, LoRA/QLoRA fine-tuning via transformers + peft + trl, DP-SGD with epsilon <= 8.0, MLflow experiment tracking, extraction attack testing
- **Multi-domain expansion** — Domain-specific tools and templates for healthcare, legal, finance
- **Streaming generation** — SSE-based real-time progress for long generation runs
- **Batch processing queue** — Async job queue for large-scale generation
- **Frontend models page** — Visual provider management and connection testing
- **Frontend connectors page** — Visual connector configuration and import history

---

## Roadmap

```
                                    UNCASE Roadmap

  COMPLETED                          IN PROGRESS                    PLANNED
  ─────────                          ───────────                    ───────

  Phase 0: Infrastructure            Phase 5: LoRA Pipeline         Phase 6: Multi-Domain
  ├─ Database + migrations           ├─ Dataset preparation         ├─ Healthcare tools
  ├─ Organization management         ├─ LoRA/QLoRA training         ├─ Legal tools
  ├─ API key auth                    ├─ DP-SGD (ε ≤ 8.0)           ├─ Finance tools
  └─ MCP server                      ├─ MLflow tracking             └─ Manufacturing tools
                                     └─ Extraction attack tests
  Phase 1: Parse & Template                                         Phase 7: Scale
  ├─ 10 chat templates               Phase 5.5: Frontend           ├─ Async job queue
  ├─ CSV/JSONL parsers               ├─ Models page                ├─ Rate limiting
  ├─ Tool framework (5 tools)        ├─ Connectors page            ├─ Streaming generation
  └─ Format auto-detection           └─ Provider selector          └─ Horizontal scaling

  Phase 2: Quality Engine
  ├─ ROUGE-L metric
  ├─ Factual fidelity
  ├─ Lexical diversity
  ├─ Dialogic coherence
  └─ Privacy score gate

  Phase 3: Generation
  ├─ LiteLLM integration
  ├─ Seed-guided generation
  ├─ Provider-aware routing
  └─ Quality re-evaluation loop

  Phase 4: Gateway & Connectors
  ├─ LLM provider registry
  ├─ Fernet-encrypted keys
  ├─ Privacy interceptor
  ├─ WhatsApp connector
  ├─ Webhook connector
  └─ Universal chat proxy
```

---

## Deployment

```bash
./deploy.sh development       # Local development
./deploy.sh preview           # Vercel preview branch
./deploy.sh production        # Production (requires confirmation)
```

The deploy script validates:
1. Clean git working directory
2. All commits pushed to remote
3. Correct branch for target environment
4. TypeScript compilation passes
5. ESLint passes
6. Production build succeeds
7. Explicit confirmation for production deployments

---

## Development

### Prerequisites

- Python >= 3.11
- Node.js >= 20 (for the dashboard)
- PostgreSQL 16+ (or Docker)
- `uv` package manager (recommended)

### Setup

```bash
git clone https://github.com/uncase-ai/uncase.git
cd uncase
cp .env.example .env
make dev-all                   # Install all dependencies
make migrate                   # Run database migrations
make api                       # Start API server (port 8000)

# In a separate terminal:
cd frontend && npm run dev     # Start dashboard (port 3000)
```

### Pre-PR Checklist

Every pull request must pass:

```bash
make check                     # Runs all three:
# 1. uv run ruff check .      — Zero lint errors
# 2. uv run mypy uncase/      — Zero type errors
# 3. uv run pytest            — All 309 tests pass

uv run pytest tests/privacy/   # MANDATORY: Privacy suite must pass
```

### Testing

```bash
uv run pytest                          # Full suite (309 tests)
uv run pytest tests/unit/              # Unit tests only
uv run pytest tests/integration/       # Integration tests
uv run pytest tests/privacy/           # Privacy tests (mandatory)
uv run pytest -x -k "test_name"        # Single test
uv run pytest --cov=uncase             # With coverage report
```

### Code Quality

- **Linter/Formatter**: Ruff (replaces black, isort, flake8)
- **Type checker**: mypy (strict mode)
- **Line length**: 120 characters
- **Docstrings**: Google style
- **Type hints**: Required on all public functions
- **Logging**: structlog (JSON structured), never `print()`
- **Security**: Zero real data in tests, custom exceptions only, no stack traces in production

---

## Contributing

UNCASE is looking for contributors across multiple areas:

### For Developers

- **New connectors**: Slack, Intercom, Zendesk, Salesforce, Telegram
- **New domain tools**: Healthcare (HL7/FHIR), legal (case management), finance (trading)
- **Layer 4 implementation**: LoRA/QLoRA training pipeline with DP-SGD
- **Streaming generation**: SSE/WebSocket support for real-time progress
- **Test coverage**: Integration tests for connectors, gateway, and provider service

### For Domain Experts

- **Seed libraries**: Curated seed collections for specific industries
- **Quality thresholds**: Domain-specific metric calibration
- **Tool definitions**: Industry-specific tool schemas and simulators
- **Compliance review**: HIPAA, SOX, GDPR regulatory alignment

### For Researchers

- **Privacy metrics**: Novel memorization detection techniques
- **Quality metrics**: Beyond ROUGE-L — semantic similarity, factual grounding
- **Differential privacy**: Optimal epsilon values per domain
- **Benchmark datasets**: Standardized evaluation suites for synthetic conversational data

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Run `make check` before submitting
4. Run `uv run pytest tests/privacy/` (mandatory)
5. Submit a PR with a clear description

See [CLAUDE.md](CLAUDE.md) for detailed coding conventions.

---

## For Organizations and Sponsors

### Why Sponsor UNCASE

UNCASE solves a **$4.2B market problem**: organizations need specialized LLMs but cannot use real data for training. Current solutions force a choice between compliance and capability. UNCASE eliminates that tradeoff.

**Target verticals:**
- **Healthcare** — Train medical LLMs without exposing PHI (HIPAA compliance)
- **Finance** — Specialize models on trading, advisory, or compliance conversations (SOX, PCI-DSS)
- **Legal** — Fine-tune on case discussions without attorney-client privilege exposure
- **Manufacturing** — Train support models on proprietary process knowledge
- **Government** — Specialized assistants trained on citizen interactions (GDPR, data sovereignty)

**What sponsors get:**
- Priority feature development aligned with your industry
- Early access to new domain tools and connectors
- Direct input on the roadmap
- Recognition in the project and at conferences
- Commercial support options

### For Investors

UNCASE sits at the intersection of three rapidly growing markets:

1. **Synthetic data** — projected $4.2B by 2028 (Gartner)
2. **LLM fine-tuning** — every enterprise will need domain-specific models
3. **Privacy-preserving AI** — regulatory pressure is accelerating globally

**Competitive moat:**
- First open-source framework with a **complete pipeline** (import → anonymize → generate → evaluate → export → fine-tune)
- **Seed-based architecture** is novel and patentable
- **Privacy-by-design** appeals to regulated industries that cannot use competitors
- **Multi-provider gateway** prevents vendor lock-in — a key enterprise requirement
- **Quality certification** with hard metrics creates trust that generic tools cannot match

**Contact**: Open an issue or reach out via the repository for partnership discussions.

---

## License

[Apache License 2.0](LICENSE) — Free for commercial and non-commercial use.

---

<p align="center">
  <strong>UNCASE</strong> — Because the best training data is data that never existed.
</p>
