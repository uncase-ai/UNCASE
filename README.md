
<p align="center">
  <img src=".github/assets/logo-horizontal.png" alt="UNCASE" height="80" />
</p>

<p align="center">
  <strong>Unbiased Neutral Convention for Agnostic Seed Engineering</strong><br/>
  Privacy-first synthetic data pipeline for fine-tuning LLMs in regulated industries.<br/>
  Blockchain-anchored quality verification on Polygon PoS.
</p>

<p align="center">
  <a href="https://opensource.org/licenses/BSD-3-Clause"><img src="https://img.shields.io/badge/License-BSD_3--Clause-blue.svg" /></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/python-≥3.11-blue.svg" /></a>
  <a href="https://docs.astral.sh/ruff/"><img src="https://img.shields.io/badge/code%20style-ruff-000000.svg" /></a>
  <a href="#"><img src="https://img.shields.io/badge/tests-1420%2B%20passing-brightgreen.svg" /></a>
  <a href="#"><img src="https://img.shields.io/badge/API%20endpoints-106+-purple.svg" /></a>
  <a href="#"><img src="https://img.shields.io/badge/blockchain-Polygon%20PoS-7b3fe4.svg" /></a>
</p>

<div align="center">

<p>This project is proudly</p>

[![SPONSORED BY E2B FOR STARTUPS](https://img.shields.io/badge/SPONSORED%20BY-E2B%20FOR%20STARTUPS-ff8800?style=for-the-badge)](https://e2b.dev/startups)

</div>

---

## Why UNCASE?

Organizations in healthcare, finance, legal, automotive, manufacturing, and education need specialized LLMs — but fine-tuning requires real conversations full of PII, PHI, and legally privileged data.

**UNCASE solves this.** It generates high-quality synthetic training data from structured *seeds* (conversation blueprints that contain zero real data), evaluates output against 9 hard-gated quality metrics, and anchors every evaluation on Polygon PoS so auditors can independently verify results without trusting anyone.

```
Real Conversations → PII Scan → Parse & Validate → 9-Metric Quality Gate
  → Synthetic Generation → Re-evaluate → Blockchain Anchor → LoRA/QLoRA Fine-tune
```

**One pipeline. Zero PII. On-chain proof.**

---

## Quick Start

### Docker (recommended)

```bash
git clone https://github.com/uncase-ai/uncase.git && cd uncase
cp .env.example .env
# Edit .env → set at least one LLM key (ANTHROPIC_API_KEY, GEMINI_API_KEY, etc.)

docker-compose up -d          # API + PostgreSQL + Redis + Dashboard
docker-compose ps             # Verify all containers are running
```

- **API**: http://localhost:8000 (Swagger at `/docs`)
- **Dashboard**: http://localhost:3000

Optional profiles:

```bash
docker-compose --profile ml up -d              # + MLflow (port 5000)
docker-compose --profile gpu up -d             # + NVIDIA GPU support (port 8001)
docker-compose --profile observability up -d   # + Prometheus (9090) + Grafana (3001)
```

### Local development (uv)

Requires Python 3.11+ and PostgreSQL 16+.

```bash
git clone https://github.com/uncase-ai/uncase.git && cd uncase
uv sync --extra dev
cp .env.example .env          # Set DATABASE_URL + at least one LLM key
make migrate                  # Run database migrations
make api                      # Start API on port 8000

# Optional: start the dashboard
cd frontend && npm install && npm run dev
```

### pip (library only)

```bash
pip install uncase                       # Core
pip install "uncase[ml]"                 # + transformers, peft, trl, torch
pip install "uncase[privacy]"            # + SpaCy, Presidio NER
pip install "uncase[blockchain]"         # + web3, Polygon PoS anchoring
pip install "uncase[all]"               # Everything
```

---

## Key Features

| | Feature | What it does |
|---|---|---|
| **Privacy** | Privacy Interceptor + PromptShield | Zero PII tolerance — Presidio NER, SpaCy, 9 regex patterns, adversarial scan |
| **Quality** | 9 hard-gated metrics | ROUGE-L, Factual Fidelity, TTR, Coherence, Semantic Fidelity, Embedding Drift, Tool Validity, Privacy, Memorization |
| **Verification** | Blockchain anchoring | Every evaluation SHA-256 hashed → Merkle tree → Polygon PoS. Verifiable via Polygonscan |
| **Generation** | LLM Gateway | Route to Claude, GPT-4, Gemini, Groq, Ollama, vLLM — privacy-intercepted |
| **Import** | Connector Hub | WhatsApp exports, webhooks, HuggingFace, CRM, custom connectors |
| **Export** | 10+ formats | ChatML, Llama, Mistral, Qwen, Nemotron, Alpaca, ShareGPT — all with tool-use |
| **Tools** | 30 domain tools | 5 per industry across 6 verticals, with simulation and training data |
| **Sandbox** | E2B cloud | Parallel generation in isolated MicroVMs, instant demo containers |
| **SDK** | Python SDK | Sync + async programmatic access via httpx |
| **MCP** | MCP server | Expose tools to Claude Code and any MCP-compatible agent |
| **Plugins** | Marketplace | 6 official plugins (one per industry), extensible architecture |
| **Enterprise** | Auth + observability | JWT, audit logging, cost tracking, rate limiting, Prometheus + Grafana |

---

## Supported Industries

| Domain | Namespace | Tools | Plugin |
|---|---|---|---|
| Automotive Sales | `automotive.sales` | 5 | `automotive` |
| Medical Consultation | `medical.consultation` | 5 | `medical` |
| Legal Advisory | `legal.advisory` | 5 | `legal` |
| Financial Advisory | `finance.advisory` | 5 | `finance` |
| Industrial Support | `industrial.support` | 5 | `industrial` |
| Education Tutoring | `education.tutoring` | 5 | `education` |

Each includes specialized seed templates, quality thresholds, compliance rules, and built-in tools.

---

## Architecture (SCSF)

| Layer | Purpose |
|---|---|
| **0 — Privacy** | PII detection + PromptShield adversarial scan (audit/warn/block) |
| **1 — Parser** | Multi-format parsing (CSV, JSONL), auto-detect OpenAI/ShareGPT/UNCASE formats |
| **2 — Evaluator** | 9 quality metrics, composite scoring, blockchain anchoring |
| **3 — Generator** | LLM-powered parallel generation with tool-augmented conversations |
| **4 — LoRA Pipeline** | LoRA/QLoRA fine-tuning with DP-SGD (epsilon ≤ 8.0) |

106+ API endpoints across 25 routers. 1,420+ tests at 73% coverage.

See [docs/architecture.md](docs/architecture.md) for the full system diagram and database schema.

---

## Documentation

| Document | Description |
|---|---|
| [Architecture](docs/architecture.md) | System diagram, SCSF layers, database schema |
| [API Reference](docs/api-reference.md) | Complete endpoint map with examples |
| [Features](docs/features.md) | Detailed feature docs with usage examples |
| [Configuration](docs/configuration.md) | Environment variables, Docker services, pip extras |
| [Development](docs/development.md) | Setup, testing, CLI, contributing guide |

---

## Contributing

```bash
git checkout -b feat/my-feature
make check                            # lint + typecheck + tests
uv run pytest tests/privacy/          # mandatory before PR
```

See [docs/development.md](docs/development.md) for the full guide.

---

## License

[BSD 3-Clause](LICENSE) — Free for commercial and non-commercial use.

<p align="center">
  <strong>UNCASE</strong> — Because the best training data is data that never existed.
</p>
