# API Reference

Interactive documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Complete Endpoint Map

| Router | Prefix | Endpoints | Description |
|---|---|---|---|
| **health** | `/health` | 2 | Service status, database connectivity |
| **auth** | `/api/v1/auth` | 3 | JWT login, token refresh, token verification |
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
| **sandbox** | `/api/v1/sandbox` | 5 | E2B sandbox generation, SSE streaming, demos, Opik evaluation |
| **knowledge** | `/api/v1/knowledge` | 5 | Document upload, search, chunking, CRUD |
| **usage** | `/api/v1/usage` | 4 | Usage metering, summary, timeline, event types |
| **webhooks** | `/api/v1/webhooks` | 8 | Subscription CRUD, delivery tracking, retry |
| **plugins** | `/api/v1/plugins` | 4 | Plugin marketplace, install, uninstall, publish |
| **pipeline** | `/api/v1/pipeline` | 3 | End-to-end pipeline runs, status, cancel |
| **jobs** | `/api/v1/jobs` | 5 | Background job queue, progress, cancel |
| **audit** | `/api/v1/audit` | 1 | Compliance audit trail with filtering |
| **scenarios** | `/api/v1/scenarios` | 3 | Scenario pack browsing, filtering by domain/skill/tags |
| **costs** | `/api/v1/costs` | 3 | LLM API cost tracking per org/job |
| **metrics** | `/metrics` | 1 | Prometheus-compatible metrics |

**Total: 78+ endpoints** across 23 routers.

## Key Endpoints

### Seeds

```bash
# Create a seed
curl -X POST http://localhost:8000/api/v1/seeds \
  -H "Content-Type: application/json" \
  -d '{"dominio": "automotive.sales", "idioma": "es", "objetivo": "...", ...}'

# List seeds
curl http://localhost:8000/api/v1/seeds?domain=automotive.sales&page=1&page_size=20

# Get / Update / Delete
curl http://localhost:8000/api/v1/seeds/{seed_id}
curl -X PUT http://localhost:8000/api/v1/seeds/{seed_id} -d '{...}'
curl -X DELETE http://localhost:8000/api/v1/seeds/{seed_id}
```

### Generation

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "seed": {"seed_id": "auto-001", "dominio": "automotive.sales", ...},
    "count": 5,
    "temperature": 0.7,
    "evaluate_after": true
  }'
```

### Evaluation

```bash
# Single evaluation
curl -X POST http://localhost:8000/api/v1/evaluations \
  -d '{"conversation": {...}, "seed": {...}}'

# Batch evaluation
curl -X POST http://localhost:8000/api/v1/evaluations/batch \
  -d '{"pairs": [{"conversation": {...}, "seed": {...}}, ...]}'

# Get thresholds
curl http://localhost:8000/api/v1/evaluations/thresholds
```

### Scenario Packs

```bash
# List all available scenario packs (summary)
curl http://localhost:8000/api/v1/scenarios/packs

# Get a specific pack with all scenario templates
curl http://localhost:8000/api/v1/scenarios/packs/automotive.sales

# List scenarios with filters
curl "http://localhost:8000/api/v1/scenarios/packs/automotive.sales/scenarios?skill_level=advanced&edge_case=true"
curl "http://localhost:8000/api/v1/scenarios/packs/medical.consultation/scenarios?tag=anxiety"
```

**Available packs:** `automotive.sales` (12), `medical.consultation` (10), `finance.advisory` (10), `legal.advisory` (8), `industrial.support` (8), `education.tutoring` (8) — 56 total scenarios.

### Quality Metrics

The evaluation system tracks 7 quality dimensions:

| Metric | Threshold | Description |
|---|---|---|
| `rouge_l` | >= 0.65 | Structural coherence with seed |
| `fidelidad_factual` | >= 0.90 | Factual fidelity |
| `diversidad_lexica` | >= 0.55 | Type-Token Ratio |
| `coherencia_dialogica` | >= 0.85 | Inter-turn dialog coherence |
| `tool_call_validity` | >= 0.90 | Tool call schema validity |
| `privacy_score` | = 0.00 | PII residual (must be zero) |
| `memorizacion` | < 0.01 | Extraction attack success rate |

**Composite formula:** `Q = min(rouge_l, fidelidad, ttr, coherencia, tool_validity)` if `privacy = 0.0 AND memorization < 0.01`, else `Q = 0.0`.

### LLM Gateway

```bash
curl -X POST http://localhost:8000/api/v1/gateway/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "..."}],
    "provider_id": "my-claude-provider",
    "privacy_mode": "block"
  }'
```

### Sandbox (E2B)

```bash
# Parallel generation
curl -X POST http://localhost:8000/api/v1/sandbox \
  -d '{"seeds": [...], "count_per_seed": 5, "evaluate_after": true}'

# Stream progress (SSE)
curl -N http://localhost:8000/api/v1/sandbox/stream -d '{"seeds": [...]}'

# Demo sandbox
curl -X POST http://localhost:8000/api/v1/sandbox/demo \
  -d '{"domain": "automotive.sales", "ttl_minutes": 30}'

# Opik evaluation
curl -X POST http://localhost:8000/api/v1/sandbox/evaluate \
  -d '{"conversations": [...], "seeds": [...], "run_hallucination_check": true}'
```

### Import

```bash
curl -X POST http://localhost:8000/api/v1/import/csv -F "file=@data.csv"
curl -X POST http://localhost:8000/api/v1/import/jsonl -F "file=@data.jsonl"
curl -X POST http://localhost:8000/api/v1/connectors/whatsapp -F "file=@chat.txt"
```

### Templates

```bash
# List formats
curl http://localhost:8000/api/v1/templates

# Export
curl -X POST http://localhost:8000/api/v1/templates/export \
  -d '{"conversations": [...], "template_name": "llama"}'
```
