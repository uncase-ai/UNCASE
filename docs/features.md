# Features

## LLM Gateway with Privacy Interception

Route requests to **any LLM provider** through a single endpoint. Every message is scanned for PII before it leaves your infrastructure and after the response arrives.

```bash
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

All API keys are **Fernet-encrypted at rest**.

## Data Connectors with Built-in Anonymization

Import conversations from any source. PII is stripped **before** data enters the pipeline.

```bash
# WhatsApp export
curl -X POST http://localhost:8000/api/v1/connectors/whatsapp -F "file=@chat_export.txt"

# Webhook from CRM/helpdesk
curl -X POST http://localhost:8000/api/v1/connectors/webhook \
  -d '{"conversations": [{"turns": [{"role": "user", "content": "..."}]}]}'

# CSV and JSONL files
curl -X POST http://localhost:8000/api/v1/import/csv -F "file=@data.csv"
curl -X POST http://localhost:8000/api/v1/import/jsonl -F "file=@data.jsonl"
```

**PII detection — dual strategy:**

| Category | Method | Token |
|---|---|---|
| Email addresses | Regex | `[EMAIL]` |
| Phone (international + local) | Regex | `[PHONE]` |
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
| Passport/Driver's license | Presidio NER | `[PASSPORT]`/`[DRIVER_LICENSE]` |

Regex heuristics are always active. Presidio NER is an optional upgrade via the `[privacy]` extra.

## Quality Evaluation Engine

Every generated conversation is scored against **6 mandatory metrics** with hard thresholds:

| Metric | Threshold | What It Measures |
|---|---|---|
| ROUGE-L | >= 0.65 | Structural coherence with the seed |
| Factual Fidelity | >= 0.90 | Accuracy of domain-specific facts |
| Lexical Diversity (TTR) | >= 0.55 | Vocabulary richness |
| Dialogic Coherence | >= 0.85 | Inter-turn consistency |
| Privacy Score | = 0.00 | Zero residual PII |
| Memorization | < 0.01 | Extraction attack success rate |

**Composite score:** `Q = min(ROUGE-L, Fidelity, TTR, Coherence) if privacy == 0.0 AND memorization < 0.01 else 0.0`

## 10 Fine-Tuning Export Formats

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

## Tool-Use Training Data

30 built-in tools across 6 industry domains (5 per domain). Define, register, and simulate tools to generate training data with realistic tool-calling patterns.

```bash
uncase tool list --domain automotive.sales
curl -X POST http://localhost:8000/api/v1/tools/buscar_inventario/simulate \
  -d '{"marca": "Toyota", "tipo": "SUV"}'
```

## E2B Cloud Sandboxes

Fan out generation across **isolated E2B MicroVMs** — one sandbox per seed, up to 20 in parallel. Each sandbox boots in ~2s, runs a self-contained worker, and streams progress via SSE.

- **Isolation**: Failures don't cascade between sandboxes
- **Speed**: ~2s boot time, parallel execution
- **Cost**: $0.05/min per sandbox at [e2b.dev](https://e2b.dev)
- **Graceful fallback**: Works without E2B (sequential local generation)

## Instant Demo Containers

Spin up a fully configured UNCASE instance for any industry in seconds:

```bash
curl -X POST http://localhost:8000/api/v1/sandbox/demo \
  -d '{"domain": "automotive.sales", "ttl_minutes": 30, "preload_seeds": 5}'
```

6 industry demos: automotive, medical, legal, finance, industrial, education. Each includes pre-loaded seeds, running FastAPI with Swagger docs, and auto-destruction after TTL.

## Opik Evaluation Sandboxes

Run **LLM-as-judge evaluations** in ephemeral sandboxes using Opik. Three metrics: hallucination, coherence, and relevance. Zero infrastructure overhead — no persistent Opik server needed.

## MCP Server

Expose tools directly to Claude Code, AI agents, and any MCP-compatible client. Mount point: `http://localhost:8000/mcp`

## Enterprise Features

- **JWT auth** with access/refresh tokens, RBAC (admin/developer/viewer)
- **Audit logging** — immutable compliance trail
- **Cost tracking** — LLM API spend per organization and per job
- **Rate limiting** — per-key sliding window
- **Security headers** — OWASP middleware (HSTS, CSP, X-Frame-Options)
- **Prometheus metrics** + pre-built Grafana dashboard
- **Background job system** with progress tracking
- **Webhook subscriptions** with delivery tracking and retry
- **Data retention policies** with configurable per-resource periods
