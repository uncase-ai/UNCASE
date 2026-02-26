# Configuration

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

### Core

| Variable | Default | Description |
|---|---|---|
| `UNCASE_ENV` | `development` | Environment: development, staging, production |
| `UNCASE_LOG_LEVEL` | `DEBUG` | Logging: DEBUG, INFO, WARNING, ERROR |
| `UNCASE_DEFAULT_LOCALE` | `es` | Default language (es, en) |
| `API_PORT` | `8000` | FastAPI server port |
| `API_SECRET_KEY` | -- | Secret key for Fernet encryption (**required**) |
| `API_CORS_ORIGINS` | `http://localhost:3000` | Comma-separated CORS origins |
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection string |

### LLM Providers

| Variable | Default | Description |
|---|---|---|
| `LITELLM_API_KEY` | -- | Default LLM provider API key |
| `ANTHROPIC_API_KEY` | -- | Claude API key (alternative) |
| `MLFLOW_TRACKING_URI` | `http://localhost:5000` | MLflow tracking server |

### Privacy

| Variable | Default | Description |
|---|---|---|
| `UNCASE_PII_CONFIDENCE_THRESHOLD` | `0.85` | PII detection confidence (0.0-1.0) |
| `UNCASE_DP_EPSILON` | `8.0` | Differential privacy budget |

### E2B Sandboxes

| Variable | Default | Description |
|---|---|---|
| `E2B_API_KEY` | -- | E2B sandbox API key (from e2b.dev) |
| `E2B_TEMPLATE_ID` | `base` | E2B sandbox template ID |
| `E2B_MAX_PARALLEL` | `5` | Max concurrent sandboxes (1-20) |
| `E2B_SANDBOX_TIMEOUT` | `300` | Sandbox timeout in seconds (30-600) |
| `E2B_ENABLED` | `false` | Enable E2B sandbox support |

### Observability

| Variable | Default | Description |
|---|---|---|
| `PROMETHEUS_PORT` | `9090` | Prometheus server port |
| `GRAFANA_PORT` | `3001` | Grafana dashboard port |
| `GRAFANA_ADMIN_USER` | `admin` | Grafana admin username |
| `GRAFANA_ADMIN_PASSWORD` | `uncase` | Grafana admin password |

## Docker Compose Services

| Service | Port | Profile | Description |
|---|---|---|---|
| `api` | 8000 | default | UNCASE FastAPI server |
| `postgres` | 5432 | default | PostgreSQL 16 |
| `mlflow` | 5000 | `ml` | MLflow tracking server |
| `api-gpu` | 8001 | `gpu` | GPU-accelerated API |
| `prometheus` | 9090 | `observability` | Prometheus metrics collector |
| `grafana` | 3001 | `observability` | Grafana dashboards |

```bash
docker compose up -d                              # API + PostgreSQL
docker compose --profile ml up -d                 # + MLflow
docker compose --profile gpu up -d                # + GPU
docker compose --profile observability up -d      # + Prometheus + Grafana
```

## Available Extras (pip/uv)

| Extra | Includes | When You Need It |
|---|---|---|
| *(core)* | FastAPI, Pydantic, LiteLLM, structlog, Typer, SQLAlchemy, cryptography | Always installed |
| `[dev]` | pytest, ruff, mypy, factory-boy, pre-commit | Running tests, contributing |
| `[ml]` | transformers, peft, trl, torch, mlflow, accelerate, bitsandbytes | LoRA fine-tuning |
| `[privacy]` | spacy, presidio-analyzer, presidio-anonymizer | Enhanced NER-based PII detection |
| `[sandbox]` | e2b, e2b-code-interpreter | E2B cloud sandbox parallel generation |
| `[evaluation]` | opik | Opik LLM-as-judge evaluation in sandboxes |
| `[all]` | dev + ml + privacy + sandbox + evaluation | Full installation |
