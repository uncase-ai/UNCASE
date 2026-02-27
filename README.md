
<p align="center">
  <img src=".github/assets/logo-horizontal.png" alt="UNCASE" height="80" />
</p>

<p align="center">
  <strong>Unbiased Neutral Convention for Agnostic Seed Engineering</strong>
</p>

<p align="center">
  The open-source framework for generating high-quality synthetic conversational data<br/>
  for LoRA/QLoRA fine-tuning in regulated industries — without exposing real data.
</p>

<p align="center">
  <a href="https://opensource.org/licenses/BSD-3-Clause"><img src="https://img.shields.io/badge/License-BSD_3--Clause-blue.svg" /></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/python-≥3.11-blue.svg" alt="Python" /></a>
  <a href="https://docs.astral.sh/ruff/"><img src="https://img.shields.io/badge/code%20style-ruff-000000.svg" alt="Ruff" /></a>
  <a href="#"><img src="https://img.shields.io/badge/tests-970%20passing-brightgreen.svg" alt="Tests" /></a>
  <a href="#"><img src="https://img.shields.io/badge/coverage-73%25-green.svg" alt="Coverage" /></a>
  <a href="#"><img src="https://img.shields.io/badge/API%20endpoints-75+-purple.svg" alt="Endpoints" /></a>
</p>
<div align="center">

<p> This project is proudly</p>

  [![SPONSORED BY E2B FOR STARTUPS](https://img.shields.io/badge/SPONSORED%20BY-E2B%20FOR%20STARTUPS-ff8800?style=for-the-badge)](https://e2b.dev/startups)

</div>

<div>
  
  
</div>


## The Problem

Organizations in healthcare, finance, legal, and manufacturing **need specialized LLMs** but face an impossible tradeoff:

- **Fine-tuning requires real conversations** — but real conversations contain PII, PHI, financial records, and legally privileged information.
- **Anonymization alone is not enough** — masked data loses the domain-specific patterns that make fine-tuning valuable.
- **Synthetic data generators produce garbage** — generic tools create conversations that sound plausible but fail on domain accuracy and compliance.
- **No unified pipeline exists** — teams stitch together 6-10 tools with bespoke glue code that breaks on every update.

**The result:** Most organizations either give up on specialization, or risk compliance violations by feeding real data into cloud APIs.

---

## The Solution

UNCASE is a **complete, privacy-first pipeline** that transforms real conversations into certified synthetic training data without any real PII ever leaving your infrastructure.

```
  Real Conversations ──▶ [PII Scan & Anonymize] ──▶ [Parse & Validate]
       ──▶ [Quality Evaluate] ──▶ [Synthetic Generate] ──▶ [Re-evaluate]
       ──▶ [Export to 10 formats] ──▶ [LoRA/QLoRA Fine-tune]
```

**One command. One pipeline. Zero PII.**

### The Seed Paradigm

Unlike traditional synthetic data tools that generate from prompts, UNCASE uses a **Seed Schema** — a structured blueprint that captures the DNA of a conversation without containing any real data:

```json
{
  "seed_id": "auto-001",
  "dominio": "automotive.sales",
  "idioma": "es",
  "objetivo": "Customer negotiating price on a certified pre-owned SUV",
  "roles": ["customer", "sales_advisor"],
  "pasos_turnos": [
    "Customer expresses interest in specific vehicle",
    "Advisor runs inventory search",
    "Customer asks about financing options",
    "Advisor presents payment plans"
  ]
}
```

Seeds are **traceable** (every synthetic conversation maps back to its seed), **reproducible** (same seed + same config = consistent output), and **auditable** (regulators can inspect seeds without seeing real data).

---

## Key Features

| Feature | Description |
|---|---|
| **Privacy-first pipeline** | Zero PII tolerance. 9 regex patterns + Presidio NER. Three privacy modes: audit, warn, block |
| **6 quality metrics** | ROUGE-L, Fidelity, TTR, Coherence, Privacy, Memorization — all with hard thresholds |
| **Multi-provider LLM gateway** | Route to Claude, GPT-4, Gemini, Groq, Ollama, vLLM through a single endpoint |
| **10 export formats** | ChatML, Llama, Mistral, Qwen, Nemotron, Alpaca, and more — all with tool-use support |
| **30 domain tools** | 5 built-in tools per industry, with simulation and training data generation |
| **E2B cloud sandboxes** | Parallel generation in isolated MicroVMs (up to 20 concurrent, ~2s boot) |
| **Instant demo containers** | Per-industry sandbox with pre-loaded seeds, auto-destroy after TTL |
| **LLM-as-judge evaluation** | Opik in ephemeral sandboxes — hallucination, coherence, relevance |
| **Enterprise features** | JWT + RBAC, audit logging, cost tracking, rate limiting, Prometheus + Grafana |
| **Full-stack dashboard** | Next.js 16 UI for the entire SCSF pipeline |
| **MCP server** | Expose tools to Claude Code and any MCP-compatible AI agent |
| **Plugin marketplace** | 6 official plugins, extensible architecture |

| Feature | Generic Generators | Enterprise Platforms | **UNCASE** |
|---|---|---|---|
| Privacy-first | No | Partial | **Zero PII, enforced by pipeline** |
| Regulated industries | No | Limited | **Healthcare, finance, legal, manufacturing** |
| Open source | Sometimes | No | **Apache 2.0** |
| Seed-based generation | No | No | **Deterministic, traceable, reproducible** |
| Full pipeline (import to LoRA) | No | Partial | **5 layers, end-to-end** |

---

## Quick Start

### Option A: Docker (recommended — batteries included)

Docker Compose gives you PostgreSQL, Redis, and the API in one command. Each developer gets **their own local databases** — nothing is shared. Migrations run automatically on startup.

```bash
git clone https://github.com/uncase-ai/uncase.git
cd uncase

# 1. Configure
cp .env.example .env
# Edit .env → set at least one LLM API key (ANTHROPIC_API_KEY, OPENAI_API_KEY, etc.)

# 2. Start everything (API + PostgreSQL + Redis)
docker compose up -d

# 3. Verify — all 3 containers should show "healthy" / "running"
docker compose ps
curl http://localhost:8000/health        # → {"status": "healthy", ...}
# Open http://localhost:8000/docs        → Swagger UI
```

Data persists in Docker volumes across restarts. Use `docker compose down` to stop (data kept) or `docker compose down -v` to stop **and wipe all data**.

```bash
# 4. (Optional) Start the dashboard
cd frontend
cp .env.example .env
npm install && npm run dev
# Open http://localhost:3000             → Dashboard
```

### Option B: Docker + extras (MLflow, GPU, Observability)

```bash
docker compose --profile ml up -d                 # + MLflow tracking server
docker compose --profile gpu up -d                # + API with NVIDIA GPU
docker compose --profile observability up -d      # + Prometheus + Grafana
```

| Service | Port | Profile | Notes |
|---|---|---|---|
| API (FastAPI) | 8000 | default | Runs migrations on startup |
| PostgreSQL 16 | **5433** | default | Mapped to 5433 to avoid conflicts with local PG |
| Redis 7 | 6379 | default | Rate limiting; optional without Docker |
| MLflow | 5000 | `ml` | Experiment tracking |
| API + GPU | 8001 | `gpu` | Requires NVIDIA Docker runtime |
| Prometheus | 9090 | `observability` | Metrics scraping |
| Grafana | 3001 | `observability` | Dashboards (admin/uncase) |

### Option C: Local development (uv + your own PostgreSQL)

Prerequisites: Python 3.11+, [uv](https://docs.astral.sh/uv/), PostgreSQL 16+ running locally.

```bash
git clone https://github.com/uncase-ai/uncase.git
cd uncase

# 1. Install Python dependencies
uv sync --extra dev           # core + dev tools (ruff, pytest, mypy)

# 2. Configure
cp .env.example .env
# Edit .env → set DATABASE_URL to your local PostgreSQL and at least one LLM key.
# Redis is optional — rate limiting falls back to in-memory without it.

# 3. Run database migrations (required before first start)
make migrate

# 4. Start the API
make api

# 5. Verify
curl http://localhost:8000/health        # → {"status": "healthy", ...}
# Open http://localhost:8000/docs        → Swagger UI

# 6. (Optional) Start the dashboard
cd frontend
cp .env.example .env
npm install && npm run dev
# Open http://localhost:3000             → Dashboard
```

### Option D: pip (library usage only)

```bash
pip install uncase
```

### Try it: register a provider and generate conversations

```bash
# Register an LLM provider
curl -X POST http://localhost:8000/api/v1/providers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Claude Provider",
    "provider_type": "anthropic",
    "api_key": "sk-ant-...",
    "default_model": "claude-sonnet-4-20250514",
    "is_default": true
  }'

# Generate synthetic conversations from a seed
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

# Export for fine-tuning
uncase template export conversations.json llama -o train_data.txt
```

### Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `port is already allocated` on 5433 | Another service uses that port | Set `POSTGRES_PORT=5434` in `.env` |
| `password authentication failed` | Alembic/app connects to the wrong Postgres instance | Verify `DATABASE_URL` port matches `POSTGRES_PORT` in `.env` |
| Stale data after schema changes | Docker volume has old schema | `docker compose down -v && docker compose up -d` |
| `InvalidPasswordError` with Alembic | Port 5432 hits a different Postgres (e.g. Supabase) | Default is now 5433; update your `.env` if you still use 5432 |

---

## Supported Domains

| Domain | Namespace | Built-in Tools |
|---|---|---|
| Automotive Sales | `automotive.sales` | 5 tools |
| Medical Consultation | `medical.consultation` | 5 tools |
| Legal Advisory | `legal.advisory` | 5 tools |
| Financial Advisory | `finance.advisory` | 5 tools |
| Industrial Support | `industrial.support` | 5 tools |
| Education Tutoring | `education.tutoring` | 5 tools |

---

## Architecture

UNCASE implements the **SCSF (Synthetic Conversational Seed Framework)** — a 5-layer pipeline:

| Layer | Module | Purpose |
|---|---|---|
| **Layer 0** | `core/privacy/` | PII detection (9 regex + Presidio NER), anonymization |
| **Layer 1** | `core/parser/` | Multi-format parsing (CSV, JSONL, WhatsApp, Webhook) |
| **Layer 2** | `core/evaluator/` | 6 quality metrics, composite scoring, pass/fail |
| **Layer 3** | `core/generator/` | LiteLLM-based generation, provider routing |
| **Layer 4** | `core/lora_pipeline/` | LoRA/QLoRA fine-tuning with DP-SGD |

**75+ REST API endpoints** across 22 routers. **970 tests** at 73% coverage.

See [docs/architecture.md](docs/architecture.md) for the full system diagram, project structure, and database schema.

---

## Documentation

| Document | Description |
|---|---|
| [Architecture](docs/architecture.md) | System diagram, SCSF layers, project structure, database schema |
| [API Reference](docs/api-reference.md) | Complete endpoint map with request/response examples |
| [Features](docs/features.md) | Detailed feature documentation with usage examples |
| [Configuration](docs/configuration.md) | Environment variables, Docker services, pip extras |
| [Development](docs/development.md) | Setup, testing, CLI reference, contributing guide |
| [CLAUDE.md](CLAUDE.md) | Coding conventions and project guidelines |

---

## Installation Options

### pip extras

```bash
pip install uncase                  # Core: FastAPI, Pydantic, LiteLLM, SQLAlchemy
pip install "uncase[dev]"           # + pytest, ruff, mypy
pip install "uncase[ml]"            # + transformers, peft, trl, torch
pip install "uncase[privacy]"       # + SpaCy, Presidio NER
pip install "uncase[sandbox]"       # + E2B cloud sandboxes
pip install "uncase[evaluation]"    # + Opik LLM-as-judge
pip install "uncase[all]"           # Everything
```

### Docker Compose profiles

```bash
docker compose up -d                              # API + PostgreSQL + Redis
docker compose --profile ml up -d                 # + MLflow tracking server
docker compose --profile gpu up -d                # + API with NVIDIA GPU
docker compose --profile observability up -d      # + Prometheus + Grafana
```

### What you get with Docker Compose

| Service | Port | Profile | Notes |
|---|---|---|---|
| API (FastAPI) | 8000 | default | Runs migrations on startup |
| PostgreSQL 16 | **5433** | default | Mapped to 5433 to avoid conflicts with local PG |
| Redis 7 | 6379 | default | Rate limiting; optional without Docker |
| MLflow | 5000 | `ml` | Experiment tracking |
| API + GPU | 8001 | `gpu` | Requires NVIDIA Docker runtime |
| Prometheus | 9090 | `observability` | Metrics scraping |
| Grafana | 3001 | `observability` | Dashboards (admin/uncase) |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Run `make check` (lint + typecheck + tests)
4. Run `uv run pytest tests/privacy/` (mandatory)
5. Submit a PR

See [docs/development.md](docs/development.md) for the full contributing guide.

---

## License

[Apache License 2.0](LICENSE) — Free for commercial and non-commercial use.

---

<p align="center">
  <strong>UNCASE</strong> — Because the best training data is data that never existed.
</p>
