# UNCASE

**Unbiased Neutral Convention for Agnostic Seed Engineering**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-≥3.11-blue.svg)](https://python.org)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![Tests](https://img.shields.io/badge/tests-228%20passing-brightgreen.svg)](#)
[![Coverage](https://img.shields.io/badge/coverage-86%25-green.svg)](#)

Framework open-source para generar datos conversacionales sinteticos de alta calidad para fine-tuning de LoRA/QLoRA en industrias reguladas (salud, finanzas, legal, manufactura) sin exponer datos reales.

> **Estado actual:** En desarrollo activo. Las actualizaciones de las Fases 2-4 se publicaran en las proximas 24 horas. Actualmente estamos desarrollando la Fase 5. Consulta la [hoja de ruta](#hoja-de-ruta) para mas detalles.

---

## Que puedes hacer ahora

UNCASE ya cuenta con un conjunto completo de herramientas funcionales. Esto es lo que puedes hacer hoy:

### Importar datasets externos

Carga conversaciones desde archivos CSV o JSONL (formatos OpenAI, ShareGPT, UNCASE nativo) al formato interno del framework, con deteccion automatica de formato.

```bash
# Importar desde CSV
uncase import csv datos_conversaciones.csv -o salida.json

# Importar desde JSONL (deteccion automatica de formato)
uncase import jsonl dataset.jsonl -o salida.json

# Especificar formato JSONL explicitamente
uncase import jsonl dataset.jsonl --format openai -o salida.json
uncase import jsonl dataset.jsonl --format sharegpt -o salida.json
```

### Exportar para fine-tuning en 10 formatos de LLM

Renderiza cualquier conversacion en el formato de chat template especifico de cada familia de LLM, listo para fine-tuning.

```bash
# Ver todos los formatos disponibles
uncase template list

# Exportar conversaciones como ChatML
uncase template export conversaciones.json chatml -o train_chatml.txt

# Previsualizar como se renderiza en formato Llama 3/4
uncase template preview conversaciones.json llama

# Exportar en cualquiera de los 10 formatos soportados
uncase template export conversaciones.json mistral -o train_mistral.txt
```

**Formatos soportados:**

| Formato | Archivo | Soporte de herramientas | Modelos tipicos |
|---|---|---|---|
| ChatML | `chatml` | Si | GPT-4, Qwen (base), Yi |
| Harmony | `harmony` | Si | Cohere Command R+ |
| Llama 3/4 | `llama` | Si | LLaMA 3/3.1/4, Meta |
| Mistral | `mistral` | Si | Mistral, Mixtral |
| Qwen 3 | `qwen` | Si | Qwen 3, Qwen 2.5 |
| Nemotron | `nemotron` | Si | NVIDIA Nemotron |
| Kimi | `moonshot` | Si | Moonshot Kimi |
| MiniMax | `minimax` | Si | MiniMax |
| OpenAI API | `openai_api` | Si | Cualquier modelo via OpenAI API |
| Alpaca | `alpaca` | No | Modelos estilo instruccion |

### Trabajar con herramientas (tool-use)

Define, registra y simula herramientas para generar datos de entrenamiento con patrones realistas de uso de herramientas.

```bash
# Listar herramientas registradas
uncase tool list

# Filtrar por dominio
uncase tool list --domain automotive.sales

# Ver detalles de una herramienta
uncase tool show buscar_inventario

# Validar una definicion de herramienta personalizada
uncase tool validate mi_herramienta.json
```

**5 herramientas automotrices integradas:**
- `buscar_inventario` — Buscar vehiculos con filtros
- `cotizar_vehiculo` — Generar cotizacion de precio
- `consultar_financiamiento` — Consultar opciones de financiamiento
- `comparar_modelos` — Comparar modelos lado a lado
- `consultar_crm` — Consultar registro de cliente

### Validar seeds

```bash
# Validar seeds contra SeedSchema v1
uncase seed validate mis_seeds.json

# Mostrar seeds en formato tabla
uncase seed show mis_seeds.json
```

### API REST

Todos los endpoints disponibles en `http://localhost:8000/docs`:

```bash
# Levantar servidor
make api

# Templates
curl http://localhost:8000/api/v1/templates
curl -X POST http://localhost:8000/api/v1/templates/render -H "Content-Type: application/json" -d '...'

# Herramientas
curl http://localhost:8000/api/v1/tools
curl http://localhost:8000/api/v1/tools/buscar_inventario
curl -X POST http://localhost:8000/api/v1/tools/buscar_inventario/simulate -H "Content-Type: application/json" -d '{"marca": "Toyota"}'

# Importar datos
curl -X POST http://localhost:8000/api/v1/import/csv -F "file=@datos.csv"
curl -X POST http://localhost:8000/api/v1/import/jsonl -F "file=@datos.jsonl"
```

### Integracion MCP (Model Context Protocol)

Si usas Claude Code u otro cliente MCP, UNCASE expone herramientas directamente:
- `list_templates` — Listar formatos de chat template
- `render_template` — Renderizar conversaciones
- `list_tools` — Listar herramientas registradas
- `simulate_tool` — Simular ejecucion de herramientas
- `validate_seed` — Validar seeds
- `list_domains` — Listar dominios soportados
- `get_quality_thresholds` — Obtener umbrales de calidad

---

## Instalacion

### Opcion 1: Git + uv (desarrollo)

```bash
git clone https://github.com/uncase-ai/uncase.git
cd uncase
uv sync                    # dependencias core
uv sync --extra dev        # + herramientas de desarrollo
uv sync --extra all        # todo (dev + ml + privacy)
```

### Opcion 2: pip

```bash
pip install uncase                      # core
pip install "uncase[dev]"               # + desarrollo
pip install "uncase[ml]"                # + machine learning
pip install "uncase[privacy]"           # + privacidad (SpaCy + Presidio)
pip install "uncase[all]"               # todo incluido
```

### Opcion 3: Docker

```bash
# API + PostgreSQL
docker compose up -d

# Con MLflow tracking
docker compose --profile ml up -d

# Con soporte GPU (NVIDIA)
docker compose --profile gpu up -d
```

---

## Inicio rapido

### CLI

```bash
uncase --help              # ver comandos disponibles
uncase --version           # ver version

# Sub-comandos principales
uncase seed --help         # gestion de seeds
uncase template --help     # templates de chat
uncase tool --help         # framework de herramientas
uncase import --help       # importacion de datos
```

### API

```bash
# Levantar servidor de desarrollo
make api
# o directamente:
uvicorn uncase.api.main:app --reload --port 8000

# Verificar que funciona
curl http://localhost:8000/health

# Documentacion interactiva
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
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
make format                # formatear codigo
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
| *(core)* | FastAPI, Pydantic, LiteLLM, structlog, Typer, SQLAlchemy... | Instalacion base |
| `[dev]` | pytest, ruff, mypy, factory-boy, pre-commit | Desarrollo y testing |
| `[ml]` | transformers, peft, trl, torch, mlflow, accelerate | Fine-tuning LoRA |
| `[privacy]` | spacy, presidio-analyzer, presidio-anonymizer | Deteccion/anonimizacion PII |
| `[all]` | dev + ml + privacy | Todo incluido |

---

## Arquitectura

UNCASE implementa el framework SCSF (Synthetic Conversational Seed Framework) con 5 capas:

```
Conversacion Real -> [Capa 0: Eliminacion PII] -> SeedSchema v1
    -> [Capa 1: Parsing + Validacion] -> Esquema interno
    -> [Capa 2: Evaluacion de calidad] -> Seeds validadas
    -> [Capa 3: Generacion sintetica] -> Conversaciones sinteticas
    -> [Capa 4: Pipeline LoRA] -> Adaptador LoRA listo para produccion
```

### Componentes implementados

```
uncase/
├── api/                    # FastAPI REST API (5 routers, 23 endpoints)
├── cli/                    # CLI con Typer (4 grupos de comandos)
├── core/
│   ├── seed_engine/        # Capa 0 — Motor de semillas
│   ├── parser/             # Capa 1 — Parser CSV/JSONL + deteccion de formato
│   ├── evaluator/          # Capa 2 — Evaluador de calidad
│   ├── generator/          # Capa 3 — Motor de generacion sintetica
│   └── lora_pipeline/      # Capa 4 — Pipeline LoRA
├── schemas/                # Modelos Pydantic (SeedSchema v1, Conversation, calidad)
├── templates/              # 10 chat templates para fine-tuning
├── tools/                  # Framework de herramientas (definicion, registro, ejecucion)
├── domains/                # Configuraciones por dominio
├── mcp/                    # Servidor MCP (9 herramientas)
├── db/                     # PostgreSQL async (SQLAlchemy + asyncpg)
└── services/               # Logica de negocio
```

---

## Dominios soportados

- `automotive.sales` — Dominio piloto (con 5 herramientas integradas)
- `medical.consultation`
- `legal.advisory`
- `finance.advisory`
- `industrial.support`
- `education.tutoring`

---

## Hoja de ruta

### Completado

- **Fase 0: Infraestructura base** — Esquemas, base de datos, gestion de organizaciones, servidor MCP, CI/CD
- **Fase 1: Templates, herramientas e importacion** — 10 chat templates, framework de herramientas con 5 tools automotrices, importacion CSV/JSONL, endpoints REST, comandos CLI, herramientas MCP. 228 tests, 86% cobertura

### Proximas 24 horas

- **Fase 2: Motor PII (Capa 0)** — Deteccion y eliminacion de PII con SpaCy + Presidio, motor de anonimizacion
- **Fase 3: Evaluacion de calidad (Capa 2)** — Metricas ROUGE-L, fidelidad factual, diversidad lexica, coherencia dialogica, score compuesto con gates de privacidad
- **Fase 4: Generacion sintetica (Capa 3)** — Integracion LiteLLM multi-proveedor, generacion guiada por seeds con restricciones de dominio, generacion con herramientas, loop de re-evaluacion

### En desarrollo activo

- **Fase 5: Pipeline LoRA (Capa 4)** — Preparacion de datasets desde conversaciones certificadas, pipeline LoRA/QLoRA (transformers + peft + trl), DP-SGD para entrenamiento con privacidad diferencial (epsilon <= 8.0), tracking con MLflow, evaluacion de modelos y pruebas de extraccion

### Futuro

- **Fase 6: Expansion multi-dominio** — Herramientas y templates especificos para salud, legal, finanzas, manufactura y educacion
- **Fase 7: Produccion** — Autenticacion API, rate limiting, almacenamiento persistente, colas asincronas, suite de privacidad expandida

---

## Desarrollo

```bash
# Configurar entorno
cp .env.example .env
make dev-all

# Workflow de desarrollo
make api                   # levantar servidor
make test                  # ejecutar tests
make check                 # verificacion completa pre-PR
```

Consulta [CLAUDE.md](CLAUDE.md) para las convenciones detalladas del proyecto.

---

## Deployment

```bash
./deploy.sh development    # desarrollo local
./deploy.sh preview        # preview en Vercel
./deploy.sh production     # produccion
```

---

## Licencia

[Apache License 2.0](LICENSE)
