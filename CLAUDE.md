# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Language

All development, commits, and code documentation must be written in **English**. Commit messages follow conventional format (feat:, fix:, chore:, etc.) in English.

**Documentation must be bilingual (EN + ES).** Every doc file, guide, or note needs both an English and a Spanish version. The Haiku doc-agent (`scripts/doc-agent.py`) handles automatic translation on each commit.

## Commits

**Commits must NOT include `Co-Authored-By: Claude` or any AI signature**, unless the user explicitly requests it for that particular commit. Do not add signatures by default.

## Deployment

Always use `./deploy.sh <environment>` to deploy. The script validates no uncommitted changes, everything is pushed, and the correct channel is used. Valid environments: `production`, `development`, `preview`.

## Doc Agent

A Haiku-powered post-commit hook runs automatically after every commit:
- Detects changed documentation files and translates them (en <-> es)
- Reports code changes that may require documentation updates
- Can generate changelog entries from commit messages

Setup: `git config core.hooksPath .githooks` (already configured)

Manual usage:
```bash
python scripts/doc-agent.py                  # process last commit
python scripts/doc-agent.py --all            # translate all docs
python scripts/doc-agent.py --translate FILE # translate specific file
python scripts/doc-agent.py --changelog      # generate changelog entry
```

Requires `ANTHROPIC_API_KEY` in the environment for translation features.

## Visión general

**UNCASE** (Unbiased Neutral Convention for Agnostic Seed Engineering) es un framework open-source para generar datos conversacionales sintéticos de alta calidad para fine-tuning de LoRA/QLoRA en industrias reguladas (salud, finanzas, legal, manufactura) sin exponer datos reales.

El repositorio tiene dos componentes principales:

1. **Landing page** — `shadcn-nextjs-flow-landing-page-1.0.0/` (Next.js 16, React 19, TypeScript)
2. **Framework SCSF** — `uncase/` (Python, FastAPI, el pipeline principal)

---

## Framework SCSF (Python Backend)

### Comandos de desarrollo

Todos los comandos se ejecutan desde `uncase/`:

```bash
# Entorno
uv sync                          # Instalar dependencias
uv run python -m uncase          # Ejecutar aplicación

# Servidor API
uv run uvicorn uncase.api.main:app --reload --port 8000

# Tests
uv run pytest                    # Toda la suite
uv run pytest tests/unit/        # Solo unit tests
uv run pytest tests/integration/ # Solo integration tests
uv run pytest tests/privacy/     # Suite de privacidad (obligatoria antes de PR)
uv run pytest -x -k "test_name"  # Un test específico
uv run pytest --cov=uncase       # Con cobertura

# Calidad de código
uv run ruff check .              # Linter
uv run ruff format .             # Formatter
uv run mypy uncase/              # Type checking
uv run ruff check . --fix        # Auto-fix linting

# CLI
uv run uncase --help             # CLI principal
uv run uncase seed create        # Crear semilla
uv run uncase parse whatsapp     # Parsear exportación WhatsApp
uv run uncase evaluate           # Evaluar calidad
uv run uncase generate           # Generar sintéticos
uv run uncase train              # Pipeline LoRA
```

### Stack tecnológico

| Componente | Tecnología |
|---|---|
| Lenguaje | Python >= 3.11 |
| Gestión dependencias | `uv` (lockfile: `uv.lock`) |
| API REST | FastAPI + Uvicorn |
| Validación de datos | Pydantic v2 (BaseModel, Field, model_validator) |
| LLM integrations | LiteLLM (interfaz unificada a Claude, Gemini, Qwen, LLaMA) |
| Fine-tuning | transformers + peft + trl (+ Unsloth/Axolotl opcionales) |
| NER / PII | SpaCy + Presidio (Microsoft) |
| CLI | Typer |
| Testing | pytest + pytest-asyncio + pytest-cov |
| Linting/Format | Ruff (linter + formatter) |
| Type checking | mypy (strict) |
| Logging | structlog (JSON structured logging) |
| Tracking ML | MLflow |
| Base de datos | PostgreSQL (async via asyncpg + SQLAlchemy) |
| i18n | gettext / babel (español + inglés) |

### Arquitectura de 5 capas (SCSF)

```
uncase/
├── core/
│   ├── seed_engine/        # Capa 0 — Motor de Semillas
│   ├── parser/             # Capa 1 — Parser y Validador Multi-formato
│   ├── evaluator/          # Capa 2 — Evaluador de Calidad
│   ├── generator/          # Capa 3 — Motor de Reproducción Sintética
│   └── lora_pipeline/      # Capa 4 — Pipeline LoRA Integrado
├── api/                    # FastAPI endpoints
│   ├── main.py             # App factory, middleware, CORS
│   ├── routers/            # Un router por capa
│   └── deps.py             # Dependency injection
├── schemas/                # Pydantic models (SeedSchema v1, etc.)
├── domains/                # Configuraciones por industria
├── i18n/                   # Internacionalización (es, en)
├── cli/                    # Comandos Typer
└── utils/                  # Logging, config, helpers compartidos
```

**Flujo de datos:**
```
Conversación Real → [Capa 0: Eliminación PII] → SeedSchema v1
    → [Capa 1: Parsing + Validación] → Esquema interno SCSF
    → [Capa 2: Evaluación de calidad] → Seeds validadas
    → [Capa 3: Generación sintética] → Conversaciones sintéticas
    → [Capa 2: Re-evaluación] → Datos certificados
    → [Capa 4: Pipeline LoRA] → Adaptador LoRA
    → Producción → Feedback → [Capa 0] (ciclo flywheel)
```

### Convenciones de código Python

**Estilo:**
- Ruff como linter y formatter (reemplaza black, isort, flake8)
- Line length: 120 caracteres
- Docstrings: Google style, en español
- Type hints obligatorios en todas las funciones públicas

**Pydantic:**
- Todos los modelos de datos heredan de `BaseModel`
- Usar `Field(...)` con description para documentación automática en OpenAPI
- Validadores con `@model_validator` y `@field_validator`
- El SeedSchema v1 es el modelo central — no modificar campos existentes sin migración

**FastAPI:**
- Un router por capa/dominio en `api/routers/`
- Dependency injection para servicios, DB, config
- Responses tipadas con Pydantic models
- Status codes explícitos en cada endpoint
- Versionado de API: `/api/v1/`

**Async:**
- Endpoints FastAPI siempre async
- SQLAlchemy en modo async (asyncpg)
- httpx para llamadas HTTP externas
- LiteLLM soporta async nativo

**Logging:**
- Usar `structlog` para logging estructurado (JSON)
- Nunca `print()` — siempre `logger.info()`, `logger.error()`, etc.
- Incluir contexto: `logger.info("seed_created", seed_id=seed.seed_id, domain=seed.dominio)`
- Niveles: DEBUG para desarrollo, INFO para producción, WARNING para degradación, ERROR para fallos

**Testing:**
- Cobertura mínima: 80% para core/, 90% para schemas/
- Tests de privacidad son OBLIGATORIOS antes de merge
- Fixtures compartidas en `conftest.py`
- Usar `factory_boy` o fixtures para datos de prueba, nunca datos reales
- Tests parametrizados para validaciones de SeedSchema

**Errores:**
- Excepciones custom en `uncase/exceptions.py` que heredan de una base `UNCASEError`
- FastAPI exception handlers para mapear a HTTP responses
- Nunca exponer stack traces en producción

**Seguridad y privacidad (NO NEGOCIABLE):**
- PII tolerance = 0 (cero) en datos finales
- Toda conversación generada debe rastrear su seed de origen
- DP-SGD con epsilon <= 8.0 durante fine-tuning
- Extraction attack success rate < 1%
- Nunca loguear contenido de conversaciones reales
- Nunca incluir datos reales en tests — usar solo datos sintéticos/ficticios

### Métricas de calidad (umbrales obligatorios)

| Métrica | Umbral | Nota |
|---|---|---|
| ROUGE-L | >= 0.65 | Coherencia estructural con semilla |
| Fidelidad Factual | >= 0.90 | Precisión de hechos del dominio |
| Diversidad Léxica (TTR) | >= 0.55 | Type-Token Ratio |
| Coherencia Dialógica | >= 0.85 | Consistencia de roles inter-turno |
| Privacy Score | = 0.00 | Cero PII residual (Presidio) |
| Memorización | < 0.01 | Extraction attack success rate |

**Fórmula compuesta:** `Q = min(ROUGE, Fidelidad, TTR, Coherencia)` si privacy=0 Y memorización<0.01, sino Q=0.

### Dominios soportados (namespaces)

- `automotive.sales` — Dominio piloto
- `medical.consultation`
- `legal.advisory`
- `finance.advisory`
- `industrial.support`
- `education.tutoring`

### Variables de entorno

Las variables se cargan desde `.env` (nunca se commitean):
- `DATABASE_URL` — PostgreSQL connection string
- `LITELLM_API_KEY` — API key para el provider LLM activo
- `ANTHROPIC_API_KEY` — Claude API (opcional, LiteLLM lo gestiona)
- `MLFLOW_TRACKING_URI` — URI de MLflow
- `UNCASE_ENV` — `development` | `staging` | `production`
- `UNCASE_LOG_LEVEL` — `DEBUG` | `INFO` | `WARNING` | `ERROR`
- `UNCASE_DEFAULT_LOCALE` — `es` | `en`

### Antes de cada PR (checklist obligatorio)

1. `uv run ruff check .` — sin errores
2. `uv run ruff format --check .` — formateado
3. `uv run mypy uncase/` — sin errores de tipos
4. `uv run pytest` — todos los tests pasan
5. `uv run pytest tests/privacy/` — suite de privacidad pasa
6. Ningún dato real en el código o tests

---

## Landing Page (Next.js)

### Comandos

Desde `shadcn-nextjs-flow-landing-page-1.0.0/`:

```bash
npm run dev          # Servidor de desarrollo (localhost:3000)
npm run build        # Build de producción
npm run lint         # ESLint
npm run lint:fix     # Auto-fix ESLint
npm run format       # Prettier
npm run check-types  # TypeScript check
```

### Stack

- Next.js 16 (App Router), React 19, TypeScript 5.9 (strict)
- Tailwind CSS v4, shadcn/ui (new-york style), Radix UI, Lucide icons
- Motion (framer-motion override), next-themes, next-mdx-remote-client
- Desplegado en Vercel

### Convenciones frontend

- Sin punto y coma, comillas simples, `printWidth: 120`
- `'use client'` solo en componentes interactivos
- `cn()` de `@/lib/utils` para merge de clases
- `cva` para variantes de componentes
- Type imports: `import type { Foo } from '...'`
- Path alias: `@/*` → `./src/*`

### Estructura de rutas

- `(pages)/` — Páginas públicas con header/footer
- `(auth)/` — Autenticación (layout 2 columnas)
- Datos estáticos en `src/assets/data/`
- Blog MDX en `src/content/blog/`

---

## Distribución del framework

### 3 vías de instalación

**Git + uv (desarrollo):**
```bash
git clone https://github.com/uncase-ai/uncase.git
cd uncase
uv sync                    # core
uv sync --extra dev        # + desarrollo
uv sync --extra all        # todo
```

**pip:**
```bash
pip install uncase                  # core
pip install "uncase[ml]"            # + ML (torch, transformers, peft, trl)
pip install "uncase[privacy]"       # + privacidad (spacy, presidio)
pip install "uncase[all]"           # todo
```

**Docker:**
```bash
docker compose up -d                      # API + PostgreSQL
docker compose --profile ml up -d         # + MLflow
docker compose --profile gpu up -d        # + GPU (NVIDIA)
```

### Extras disponibles en pyproject.toml

| Extra | Contenido |
|---|---|
| *(core)* | fastapi, pydantic, litellm, structlog, typer, sqlalchemy, etc. |
| `[dev]` | pytest, ruff, mypy, factory-boy, pre-commit |
| `[ml]` | transformers, peft, trl, torch, mlflow, accelerate, bitsandbytes |
| `[privacy]` | spacy, presidio-analyzer, presidio-anonymizer |
| `[all]` | dev + ml + privacy |

### Makefile — Comandos principales

```bash
make help          # Ver todos los comandos
make install       # Instalar dependencias core
make dev           # Instalar core + dev
make dev-all       # Instalar todo (core + dev + ml + privacy)
make api           # Levantar servidor de desarrollo (puerto 8000)
make test          # Ejecutar toda la suite de tests
make lint          # Ruff check
make format        # Ruff format
make typecheck     # mypy
make check         # lint + typecheck + tests (pre-PR)
make docker-build  # Construir imagen Docker
make docker-up     # Levantar servicios Docker
make docker-down   # Detener servicios Docker
make clean         # Limpiar artefactos
```

### Docker Compose — Servicios

| Servicio | Descripción | Puerto | Perfil |
|---|---|---|---|
| `api` | FastAPI (UNCASE API) | 8000 | *(default)* |
| `postgres` | PostgreSQL 16 Alpine | 5432 | *(default)* |
| `mlflow` | MLflow tracking server | 5000 | `ml` |
| `api-gpu` | API con soporte NVIDIA GPU | 8001 | `gpu` |
