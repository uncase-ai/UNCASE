
<p align="center">
  <img src=".github/assets/logo-horizontal.png" alt="UNCASE" height="80" />
</p>

<p align="center">
  <strong>Unbiased Neutral Convention for Agnostic Seed Engineering</strong>
</p>

<p align="center">
  The open-source framework for generating high-quality synthetic conversational data<br/>
  for LoRA/QLoRA fine-tuning in regulated industries — without exposing real data.<br/>
  Now with <strong>blockchain-anchored quality verification</strong> on Polygon PoS.
</p>

<p align="center">
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" /></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/python-≥3.11-blue.svg" alt="Python" /></a>
  <a href="https://docs.astral.sh/ruff/"><img src="https://img.shields.io/badge/code%20style-ruff-000000.svg" alt="Ruff" /></a>
  <a href="#"><img src="https://img.shields.io/badge/tests-1160%2B%20passing-brightgreen.svg" alt="Tests" /></a>
  <a href="#"><img src="https://img.shields.io/badge/coverage-73%25-green.svg" alt="Coverage" /></a>
  <a href="#"><img src="https://img.shields.io/badge/API%20endpoints-106+-purple.svg" alt="Endpoints" /></a>
  <a href="#"><img src="https://img.shields.io/badge/quality%20metrics-9%20hard--gated-orange.svg" alt="Quality Metrics" /></a>
  <a href="#"><img src="https://img.shields.io/badge/blockchain-Polygon%20PoS-7b3fe4.svg" alt="Blockchain" /></a>
</p>
<div align="center">

<p> This project is proudly</p>

  [![SPONSORED BY E2B FOR STARTUPS](https://img.shields.io/badge/SPONSORED%20BY-E2B%20FOR%20STARTUPS-ff8800?style=for-the-badge)](https://e2b.dev/startups)

</div>

<div>


</div>


## The Problem

Organizations in healthcare, finance, legal, automotive, manufacturing, and education **need specialized LLMs** but face an impossible tradeoff:

- **Fine-tuning requires real conversations** — but real conversations contain PII, PHI, financial records, and legally privileged information.
- **Anonymization alone is not enough** — masked data loses the domain-specific patterns that make fine-tuning valuable.
- **Synthetic data generators produce garbage** — generic tools create conversations that sound plausible but fail on domain accuracy and compliance.
- **No unified pipeline exists** — teams stitch together 6-10 tools with bespoke glue code that breaks on every update.
- **Quality claims are unverifiable** — self-reported metrics can be fabricated, and auditors have no independent way to verify them.

**The result:** Most organizations either give up on specialization, or risk compliance violations by feeding real data into cloud APIs.

---

## The Solution

UNCASE is a **complete, privacy-first pipeline** that transforms real conversations into certified synthetic training data — with every quality evaluation cryptographically anchored on a public blockchain.

```
  Real Conversations ──▶ [PII Scan + PromptShield] ──▶ [Parse & Validate]
       ──▶ [9-Metric Quality Gate] ──▶ [Synthetic Generate] ──▶ [Re-evaluate]
       ──▶ [Blockchain Anchor] ──▶ [Export to 10+ formats] ──▶ [LoRA/QLoRA Fine-tune]
```

**One command. One pipeline. Zero PII. On-chain proof.**

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

Seeds are **traceable** (every synthetic conversation maps back to its seed via `seed_id`), **reproducible** (same seed + same config = consistent output), and **auditable** (regulators can inspect seeds without seeing real data).

---

## Key Features

| Feature | Description |
|---|---|
| **Privacy Interceptor + PromptShield** | Zero PII tolerance. Presidio NER + SpaCy + 9 regex patterns + adversarial scan (injection, jailbreak, extraction, toxic, PII solicitation). Three modes: audit, warn, block |
| **9 hard-gated quality metrics** | ROUGE-L, Factual Fidelity, TTR, Dialogic Coherence, Semantic Fidelity, Embedding Drift, Tool Call Validity, Privacy Score, Memorization Rate — all with hard thresholds |
| **Blockchain-verified quality** | Every evaluation is SHA-256 hashed, batched into a Merkle tree, and its root anchored on Polygon PoS. Tamper-proof, independently verifiable via Polygonscan |
| **Universal LLM Gateway** | Route to Claude, GPT-4, Gemini, Groq, Ollama, vLLM through a single endpoint with Privacy Interceptor on every request |
| **Connector Hub** | Import from WhatsApp exports, webhooks, HuggingFace, CRM, or build custom connectors via BaseConnector |
| **10+ export formats** | ChatML, Llama, Mistral, Qwen, Nemotron, Alpaca, ShareGPT, and more — all with tool-use support |
| **30 domain tools** | 5 built-in tools per industry (6 industries), with simulation and training data generation |
| **E2B cloud sandboxes** | Parallel generation in isolated MicroVMs (up to 20 concurrent, ~2s boot) |
| **Instant demo containers** | Per-industry sandbox with pre-loaded seeds, auto-destroy after TTL |
| **LLM-as-judge evaluation** | Semantic Fidelity via 4-dimension rubric + Opik in ephemeral sandboxes |
| **Python SDK** | Programmatic access to the entire pipeline — sync and async via httpx |
| **MCP server** | Expose tools to Claude Code and any MCP-compatible AI agent via FastMCP |
| **Plugin marketplace** | 6 official plugins (one per industry), extensible architecture |
| **Enterprise features** | JWT auth, audit logging, cost tracking per org/job, rate limiting, Prometheus + Grafana, security headers |
| **Full-stack dashboard** | Next.js 16 UI for the entire SCSF pipeline |

### How UNCASE Compares

| Feature | Generic Generators | Enterprise Platforms | **UNCASE** |
|---|---|---|---|
| Privacy-first | No | Partial | **Zero PII — Privacy Interceptor + PromptShield** |
| Quality verification | Self-reported | Self-reported | **9 metrics, blockchain-anchored on Polygon PoS** |
| Regulated industries | No | Limited | **6 verticals: healthcare, finance, legal, automotive, manufacturing, education** |
| Open source | Sometimes | No | **Apache 2.0 — free forever** |
| Seed-based generation | No | No | **Deterministic, traceable, reproducible** |
| Full pipeline (import to LoRA) | No | Partial | **5 layers, end-to-end, with on-chain audit trail** |

---

## Blockchain-Verified Quality

UNCASE is the **first data processing framework to cryptographically anchor every quality certification on a public blockchain**. No auditor or regulator needs to trust UNCASE — they verify on-chain.

### How It Works

```
Layer 2 Evaluation (9 metrics + composite score + seed lineage + timestamp)
    │
    ▼
SHA-256 Hash
    │
    ▼
Merkle Tree (batch of evaluation hashes)
    │
    ▼
Merkle Root → Published on Polygon PoS
    │
    ▼
Independently verifiable via Polygonscan
```

1. **Hash** — The complete evaluation payload (all 9 metric scores, composite quality score, `seed_id` lineage, and timestamp) is serialized and hashed using SHA-256.
2. **Batch** — Individual evaluation hashes are organized into a Merkle tree. Any single evaluation can be verified against the tree root without needing the entire batch.
3. **Anchor** — The Merkle root is published as a transaction on Polygon PoS, permanently recorded on a public, permissionless blockchain.
4. **Verify** — Any party can take an evaluation hash, check it against the on-chain Merkle root via Polygonscan, and confirm the evaluation was performed with specific results at a specific time.

### Smart Contract

The `UNCASEAuditAnchor` Solidity contract (OpenZeppelin Ownable, Solidity ^0.8.20) exposes:

| Function | Description |
|---|---|
| `anchorRoot(bytes32)` | Publish a Merkle root on-chain |
| `verifyRoot(bytes32)` | Check if a root was previously anchored |
| `getTimestamp(bytes32)` | Retrieve the block timestamp of an anchored root |

### Why This Matters for Auditing

| Traditional Audit | With UNCASE Blockchain Anchoring |
|---|---|
| Request internal documentation | Request the evaluation hash |
| Review self-reported metrics | Verify hash against on-chain Merkle root |
| Trust that logs haven't been altered | Confirm immutable timestamp on Polygonscan |
| Accept unverifiable methodology | Cross-reference against published 9-metric thresholds |
| Weeks of preparation | **Hours — or minutes** |

### Compliance Frameworks Supported

| Framework | Jurisdiction | How Blockchain Anchoring Helps |
|---|---|---|
| **GDPR** | EU | Verifiable proof of data minimization and privacy-by-design |
| **HIPAA** | US | Immutable audit trails for PHI processing |
| **CCPA** | California | Independently verifiable consumer data protection records |
| **AI Act** | EU | High-risk AI system documentation and traceability |
| **MiFID II** | EU | Tamper-proof financial services record-keeping |
| **LFPDPPP** | Mexico | Cryptographic evidence for personal data protection |
| **SOX Section 404** | US | Immutable internal controls over financial data pipelines |

---

## The 9 Quality Metrics

Every synthetic conversation is evaluated against 9 hard-gated metrics. Failure on **any single metric** sets the composite score to zero — no partial credit.

| # | Metric | Threshold | What It Measures |
|---|--------|-----------|------------------|
| 1 | **ROUGE-L** | ≥ 0.65 | Structural coherence between seed and synthetic output |
| 2 | **Factual Fidelity** | ≥ 0.90 | Domain-specific factual accuracy preservation |
| 3 | **Type-Token Ratio (TTR)** | ≥ 0.55 | Lexical diversity — prevents repetitive, collapsed output |
| 4 | **Dialogic Coherence** | ≥ 0.85 | Role consistency and information flow across turns |
| 5 | **Semantic Fidelity** | ≥ 0.60 | LLM-as-Judge with 4-dimension rubric (factual fidelity, logical coherence, role consistency, naturalness) |
| 6 | **Embedding Drift** | ≥ 0.40 | Cosine similarity with TF-IDF fallback — detects semantic deviation |
| 7 | **Tool Call Validity** | ≥ 0.90 | Validates correctness of `tool_calls` and `tool_results` |
| 8 | **Privacy Score** | = 0.00 | Must be exactly zero — any PII detected means Q = 0 |
| 9 | **Memorization Rate** | < 0.01 | Must be below 1% — prevents model memorization of source data |

**Composite formula:**

```
Q = min(ROUGE_L, Fidelity, TTR, Coherence)
    if privacy_score == 0.00 AND memorization_rate < 0.01
    else Q = 0
```

All 9 scores, the composite Q, seed lineage, and timestamp are hashed and anchored on Polygon PoS.

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

# 2. Start everything (API + PostgreSQL + Redis + Dashboard)
docker compose up -d

# 3. Verify — all 4 containers should show "healthy" / "running"
docker compose ps
curl http://localhost:8000/health        # → {"status": "healthy", ...}
# Open http://localhost:8000/docs        → Swagger UI
# Open http://localhost:3000             → Dashboard
```

Data persists in Docker volumes across restarts. Use `docker compose down` to stop (data kept) or `docker compose down -v` to stop **and wipe all data**.

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
| Dashboard (Next.js) | 3000 | default | Connects to API at localhost:8000 |
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

# Verify a quality evaluation on-chain
curl http://localhost:8000/api/v1/blockchain/verify/{merkle_root}

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

| Domain | Namespace | Built-in Tools | Plugin |
|---|---|---|---|
| Automotive Sales | `automotive.sales` | 5 tools | `automotive` |
| Medical Consultation | `medical.consultation` | 5 tools | `medical` |
| Legal Advisory | `legal.advisory` | 5 tools | `legal` |
| Financial Advisory | `finance.advisory` | 5 tools | `finance` |
| Industrial Support | `industrial.support` | 5 tools | `industrial` |
| Education Tutoring | `education.tutoring` | 5 tools | `education` |

Each domain includes specialized seed templates, quality thresholds, compliance rules, and 5 built-in tools (cotizador, simulador, CRM, etc.) accessible via the Plugin Marketplace.

---

## Architecture

UNCASE implements the **SCSF (Synthetic Conversational Seed Framework)** — a 5-layer pipeline with blockchain-anchored output:

| Layer | Module | Purpose |
|---|---|---|
| **Layer 0** | `core/privacy/` | PII detection (Presidio NER + SpaCy + 9 regex), PromptShield adversarial scan (5 threat categories), Privacy Interceptor (audit/warn/block) |
| **Layer 1** | `core/parser/` | Multi-format parsing (CSV, JSONL — auto-detects OpenAI, ShareGPT, UNCASE formats), validated Conversation objects with `seed_id` lineage |
| **Layer 2** | `core/evaluator/` | 9 hard-gated quality metrics, composite scoring, pass/fail — outputs hashed and anchored on Polygon PoS |
| **Layer 3** | `core/generator/` | LiteLLM-based parallel generation with semaphore concurrency, smart retry with escalating temperature, tool-augmented conversations (`tool_calls` + `tool_results`) |
| **Layer 4** | `core/lora_pipeline/` | LoRA/QLoRA fine-tuning with DP-SGD (epsilon ≤ 8.0), 50–150 MB adapters, $15–$45 USD per run |

### Additional Core Modules

| Module | Purpose |
|---|---|
| `core/blockchain/` | SHA-256 hashing, Merkle tree construction, Polygon PoS anchoring |
| `api/routers/` | 25 REST API routers, 106+ endpoints |
| `connectors/` | WhatsApp, webhook, HuggingFace, BaseConnector |
| `plugins/` | 6 official plugins, registry with install/uninstall lifecycle |
| `sdk/` | Python SDK — sync + async client via httpx |
| `mcp/` | MCP server via FastMCP — expose tools to AI agents |
| `sandbox/` | E2B cloud sandboxes, Opik runner, demo containers |
| `services/` | Auth (JWT), audit, blockchain, costs, organizations |

**106+ REST API endpoints** across 25 routers. **1,160+ tests** at 73% coverage.

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
pip install uncase                    # Core: FastAPI, Pydantic, LiteLLM, SQLAlchemy
pip install "uncase[dev]"             # + pytest, ruff, mypy
pip install "uncase[ml]"              # + transformers, peft, trl, torch
pip install "uncase[privacy]"         # + SpaCy, Presidio NER
pip install "uncase[sandbox]"         # + E2B cloud sandboxes
pip install "uncase[evaluation]"      # + Opik LLM-as-judge
pip install "uncase[blockchain]"      # + web3, eth-account (Polygon PoS anchoring)
pip install "uncase[all]"             # Everything
```

### Docker Compose profiles

```bash
docker compose up -d                              # API + PostgreSQL + Redis + Dashboard
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
| Dashboard (Next.js) | 3000 | default | Connects to API at localhost:8000 |
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
  <strong>UNCASE</strong> — Because the best training data is data that never existed.<br/>
  And the best proof is the one no one can alter.
</p>
