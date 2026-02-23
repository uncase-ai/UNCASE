# UNCASE

**Unbiased Neutral Convention for Agnostic Seed Engineering**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-≥3.11-blue.svg)](https://python.org)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)

Framework open-source para generar datos conversacionales sintéticos de alta calidad para fine-tuning de LoRA/QLoRA en industrias reguladas (salud, finanzas, legal, manufactura) sin exponer datos reales.

---

## Instalación

### Opción 1: Git + uv (desarrollo)

```bash
git clone https://github.com/uncase-ai/uncase.git
cd uncase
uv sync                    # dependencias core
uv sync --extra dev        # + herramientas de desarrollo
uv sync --extra all        # todo (dev + ml + privacy)
```

### Opción 2: pip

```bash
pip install uncase                      # core
pip install "uncase[dev]"               # + desarrollo
pip install "uncase[ml]"                # + machine learning
pip install "uncase[privacy]"           # + privacidad (SpaCy + Presidio)
pip install "uncase[all]"               # todo incluido
```

### Opción 3: Docker

```bash
# API + PostgreSQL
docker compose up -d

# Con MLflow tracking
docker compose --profile ml up -d

# Con soporte GPU (NVIDIA)
docker compose --profile gpu up -d
```

---

## Inicio rápido

### CLI

```bash
uncase --help              # ver comandos disponibles
uncase --version           # ver versión
```

### API

```bash
# Levantar servidor de desarrollo
make api
# o directamente:
uvicorn uncase.api.main:app --reload --port 8000

# Verificar que funciona
curl http://localhost:8000/health
```

### Makefile

```bash
make help                  # ver todos los comandos
make install               # instalar dependencias core
make dev                   # instalar core + dev
make dev-all               # instalar todo
make api                   # levantar servidor
make test                  # ejecutar tests
make lint                  # ejecutar linter
make format                # formatear código
make typecheck             # verificar tipos
make check                 # lint + typecheck + tests
make docker-up             # levantar con Docker
make docker-down           # detener Docker
make clean                 # limpiar artefactos
```

---

## Extras disponibles

| Extra | Incluye | Uso |
|---|---|---|
| *(core)* | FastAPI, Pydantic, LiteLLM, structlog, Typer, SQLAlchemy... | Instalación base |
| `[dev]` | pytest, ruff, mypy, factory-boy, pre-commit | Desarrollo y testing |
| `[ml]` | transformers, peft, trl, torch, mlflow, accelerate | Fine-tuning LoRA |
| `[privacy]` | spacy, presidio-analyzer, presidio-anonymizer | Detección/anonimización PII |
| `[all]` | dev + ml + privacy | Todo incluido |

---

## Arquitectura

UNCASE implementa el framework SCSF (Synthetic Conversational Seed Framework) con 5 capas:

```
Conversación Real → [Capa 0: Eliminación PII] → SeedSchema v1
    → [Capa 1: Parsing + Validación] → Esquema interno
    → [Capa 2: Evaluación de calidad] → Seeds validadas
    → [Capa 3: Generación sintética] → Conversaciones sintéticas
    → [Capa 4: Pipeline LoRA] → Adaptador LoRA listo para producción
```

---

## Dominios soportados

- `automotive.sales` — Dominio piloto
- `medical.consultation`
- `legal.advisory`
- `finance.advisory`
- `industrial.support`
- `education.tutoring`

---

## Desarrollo

```bash
# Configurar entorno
cp .env.example .env
make dev-all

# Workflow de desarrollo
make api                   # levantar servidor
make test                  # ejecutar tests
make check                 # verificación completa pre-PR
```

Consulta [CLAUDE.md](CLAUDE.md) para las convenciones detalladas del proyecto.

---

## Deployment

```bash
./deploy.sh development    # desarrollo local
./deploy.sh preview        # preview en Vercel
./deploy.sh production     # producción
```

---

## Licencia

[Apache License 2.0](LICENSE)
