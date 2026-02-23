# Plan de Desarrollo — UNCASE Framework SCSF

> Ruta de implementación detallada para el framework SCSF (Synthetic Conversation Seed Framework).
> Versión 1.0 — Febrero 2026

---

## Principios guía

1. **Vertical funcional primero**: cada capa debe entregar valor de forma independiente antes de avanzar a la siguiente.
2. **Dominio piloto `automotive.sales`**: toda implementación se valida primero contra este dominio.
3. **Privacidad no es una feature, es un requisito**: los tests de privacidad se implementan junto con cada capa, no después.
4. **i18n desde el día 1**: todo string visible al usuario soporta español e inglés.
5. **Tests antes que código**: los modelos Pydantic y los contratos de API se definen primero, luego se implementa.

---

## Fase 0 — Infraestructura base (Sprint 1-2)

**Objetivo:** Tener un proyecto Python funcional con CI, API esqueleto, y SeedSchema validado.

### 0.1 Scaffolding del proyecto

```
uncase/
├── pyproject.toml              # uv, ruff, mypy, pytest config
├── uv.lock
├── .env.example
├── .github/
│   └── workflows/
│       └── ci.yml              # Ruff + mypy + pytest en cada PR
├── uncase/
│   ├── __init__.py
│   ├── __main__.py             # Entry point: python -m uncase
│   ├── config.py               # Settings con pydantic-settings
│   ├── exceptions.py           # UNCASEError base + excepciones custom
│   ├── logging.py              # Configuración structlog
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── seed.py             # SeedSchema v1 (Pydantic)
│   │   ├── conversation.py     # Modelos de conversación interna
│   │   ├── validation.py       # InformeValidacion
│   │   └── quality.py          # Métricas de calidad
│   ├── core/
│   │   ├── __init__.py
│   │   ├── seed_engine/        # Capa 0 (vacío, stubs)
│   │   ├── parser/             # Capa 1 (vacío, stubs)
│   │   ├── evaluator/          # Capa 2 (vacío, stubs)
│   │   ├── generator/          # Capa 3 (vacío, stubs)
│   │   └── lora_pipeline/      # Capa 4 (vacío, stubs)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app factory
│   │   ├── deps.py             # Dependencies
│   │   └── routers/
│   │       └── health.py       # GET /health
│   ├── cli/
│   │   └── __init__.py         # Typer app
│   ├── domains/
│   │   └── automotive/
│   │       └── config.py       # Configuración del dominio piloto
│   ├── i18n/
│   │   ├── es/
│   │   └── en/
│   └── utils/
│       └── __init__.py
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   └── schemas/
│   │       └── test_seed.py    # Validación exhaustiva de SeedSchema
│   ├── integration/
│   └── privacy/
└── examples/
    └── automotive_sales/
        └── sample_seeds.json   # 5 semillas de ejemplo
```

### 0.2 Dependencias iniciales

```toml
[project]
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.34",
    "pydantic>=2.10",
    "pydantic-settings>=2.7",
    "litellm>=1.55",
    "structlog>=24.4",
    "typer>=0.15",
    "httpx>=0.28",
    "python-i18n>=0.3",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3",
    "pytest-asyncio>=0.25",
    "pytest-cov>=6.0",
    "ruff>=0.9",
    "mypy>=1.14",
    "factory-boy>=3.3",
]
ml = [
    "transformers>=4.47",
    "peft>=0.14",
    "trl>=0.14",
    "datasets>=3.2",
    "mlflow>=2.19",
    "torch>=2.5",
]
privacy = [
    "spacy>=3.8",
    "presidio-analyzer>=2.2",
    "presidio-anonymizer>=2.2",
]
```

### 0.3 Entregables de Fase 0

- [ ] `pyproject.toml` configurado con todas las dependencias
- [ ] SeedSchema v1 implementado en Pydantic con todos los campos del whitepaper
- [ ] Tests para SeedSchema (campos obligatorios, opcionales, validaciones)
- [ ] FastAPI corriendo con `/health` y `/api/v1/docs`
- [ ] CI en GitHub Actions (ruff + mypy + pytest)
- [ ] structlog configurado
- [ ] .env.example con todas las variables
- [ ] 5 semillas de ejemplo para `automotive.sales`
- [ ] Configuración i18n base (es/en)
- [ ] CLI esqueleto con `--help`

---

## Fase 1 — Capa 0: Motor de Semillas (Sprint 3-4)

**Objetivo:** Crear, validar, almacenar y gestionar semillas conversacionales.

### Componentes

| Módulo | Responsabilidad |
|---|---|
| `seed_engine/creator.py` | Creación de semillas desde plantillas o manual |
| `seed_engine/repository.py` | CRUD de semillas (PostgreSQL) |
| `seed_engine/validator.py` | Validación de SeedSchema con reglas de negocio |
| `seed_engine/exporter.py` | Exportar semillas a JSON/YAML |
| `seed_engine/templates.py` | Plantillas por dominio para acelerar creación |

### API Endpoints

```
POST   /api/v1/seeds              # Crear semilla
GET    /api/v1/seeds              # Listar semillas (filtros: dominio, tipo)
GET    /api/v1/seeds/{seed_id}    # Obtener semilla
PUT    /api/v1/seeds/{seed_id}    # Actualizar semilla
DELETE /api/v1/seeds/{seed_id}    # Eliminar semilla
POST   /api/v1/seeds/validate     # Validar semilla sin persistir
GET    /api/v1/seeds/export       # Exportar batch (JSON/YAML)
GET    /api/v1/domains            # Listar dominios disponibles
```

### CLI

```bash
uncase seed create --domain automotive.sales --type consulta_financiamiento
uncase seed list --domain automotive.sales
uncase seed validate seed.json
uncase seed export --format yaml --output seeds/
```

### Entregables

- [ ] CRUD completo de semillas con PostgreSQL
- [ ] Validación con reglas de negocio (roles >= 2, flujo_esperado no vacío, etc.)
- [ ] Templates para dominio piloto `automotive.sales`
- [ ] CLI funcional para gestión de semillas
- [ ] Tests unitarios (>= 90% cobertura en schemas/)
- [ ] Documentación OpenAPI completa

---

## Fase 2 — Capa 1: Parser y Validador Multi-formato (Sprint 5-8)

**Objetivo:** Ingestar conversaciones de múltiples formatos y unificarlas al esquema interno.

### Parsers (prioridad de implementación)

| # | Parser | Clase | Prioridad |
|---|---|---|---|
| 1 | WhatsApp export (.txt) | `WhatsAppParser` | Alta |
| 2 | JSON genérico | `JSONConversationParser` | Alta |
| 3 | ShareGPT | `ShareGPTParser` | Alta |
| 4 | OpenAI Chat | `OpenAIChatParser` | Alta |
| 5 | CSV turn-based | `CSVDialogParser` | Media |
| 6 | Transcript raw (Whisper) | `TranscriptParser` | Media |
| 7 | CRM Kommo | `KommoExportParser` | Baja |

### Validador conversacional (`ValidadorConversacional`)

5 checks obligatorios:
1. `_check_roles_consistentes(conv)` — >= 2 participantes
2. `_check_continuidad_topica(conv)` — Coherencia temática
3. `_check_fidelidad_factual(conv, seed)` — Consistencia con semilla
4. `_check_pii_residual(conv)` — Detección PII (tolerancia = 0)
5. `_check_longitud_objetivo(conv, seed)` — Dentro del rango de turnos

### PII Scanner multi-etapa

1. NER con SpaCy (modelos español + inglés)
2. Reglas heurísticas (CURP, RFC, CLABE, tarjetas de crédito, coordenadas)
3. Presidio (Microsoft) para detección probabilística multi-idioma
4. Flag para revisión humana si score de riesgo excede umbral

### API Endpoints

```
POST   /api/v1/parse                    # Parsear archivo/texto
POST   /api/v1/parse/batch              # Parsear batch de archivos
POST   /api/v1/validate/conversation    # Validar conversación
GET    /api/v1/parse/formats            # Listar formatos soportados
POST   /api/v1/privacy/scan             # Escanear PII en texto
```

### Entregables

- [ ] WhatsAppParser funcional con tests
- [ ] JSONConversationParser + ShareGPTParser + OpenAIChatParser
- [ ] ValidadorConversacional con los 5 checks
- [ ] PII Scanner multi-etapa (SpaCy + Presidio)
- [ ] Reglas heurísticas para identificadores mexicanos (CURP, RFC, CLABE)
- [ ] Tests de privacidad (obligatorios)
- [ ] Capacidad target: 10,000 conversaciones/hora

---

## Fase 3 — Capa 2: Evaluador de Calidad (Sprint 9-11)

**Objetivo:** Sistema de métricas que certifica calidad de conversaciones.

### 6 métricas implementadas

| Métrica | Implementación |
|---|---|
| ROUGE-L (>= 0.65) | `rouge-score` library |
| Fidelidad Factual (>= 0.90) | LLM-as-Judge via LiteLLM |
| Diversidad Léxica TTR (>= 0.55) | Cálculo directo types/tokens |
| Coherencia Dialógica (>= 0.85) | Análisis de turnos + LLM-as-Judge |
| Privacy Score (= 0) | PII Scanner de Capa 1 |
| Memorización (< 0.01) | Extraction attack testing post fine-tuning |

### Fórmula compuesta

```python
def quality_score(metrics: QualityMetrics) -> float:
    if metrics.privacy_score > 0 or metrics.memorization >= 0.01:
        return 0.0
    return min(metrics.rouge_l, metrics.factual_fidelity,
               metrics.lexical_diversity, metrics.dialogic_coherence)
```

### LLM-as-Judge

- Prompt estandarizado que recibe semilla + conversación generada
- Evalúa fidelidad factual y coherencia dialógica
- Via LiteLLM para ser agnóstico al provider
- Correlación target con evaluación humana: r >= 0.87

### API Endpoints

```
POST   /api/v1/evaluate                 # Evaluar una conversación
POST   /api/v1/evaluate/batch           # Evaluar batch
GET    /api/v1/evaluate/metrics          # Métricas disponibles y umbrales
POST   /api/v1/evaluate/certify         # Certificar dataset completo
```

### Entregables

- [ ] Las 6 métricas implementadas con umbrales configurables
- [ ] Fórmula compuesta Q_UNCASE
- [ ] LLM-as-Judge con prompts estandarizados
- [ ] Dashboard de calidad (exportable como JSON/CSV)
- [ ] Tests con conversaciones de calidad conocida (golden set)
- [ ] Reporte de certificación para auditoría

---

## Fase 4 — Capa 3: Motor de Reproducción Sintética (Sprint 12-16)

**Objetivo:** Generar conversaciones sintéticas diversas a partir de semillas validadas.

### 4 estrategias de diversificación

| Estrategia | Módulo |
|---|---|
| Variación de persona | `generator/persona_variation.py` |
| Variación de flujo | `generator/flow_variation.py` |
| Inyección de herramientas | `generator/tool_injection.py` |
| Ruido controlado | `generator/noise_injection.py` |

### Integración LLM via LiteLLM

```python
# LiteLLM permite usar cualquier provider con la misma interfaz
response = await litellm.acompletion(
    model="anthropic/claude-opus-4-20250514",  # o "qwen/qwen3-72b", "meta-llama/llama-3.3-70b"
    messages=[{"role": "system", "content": generation_prompt}],
    temperature=0.8,
)
```

### Ratio de expansión

- 1 semilla → 200-500 conversaciones sintéticas
- Target: 1,000 conversaciones validadas por semilla por hora
- Re-evaluación automática con Capa 2 después de generación

### Formatos de salida para training

- ShareGPT format
- Alpaca format
- ChatML format

### API Endpoints

```
POST   /api/v1/generate                 # Generar desde una semilla
POST   /api/v1/generate/batch           # Generar desde batch de semillas
GET    /api/v1/generate/status/{job_id} # Estado de job de generación
POST   /api/v1/generate/export          # Exportar dataset (ShareGPT/Alpaca/ChatML)
GET    /api/v1/generate/models          # Listar modelos disponibles vía LiteLLM
```

### Entregables

- [ ] Las 4 estrategias de diversificación implementadas
- [ ] Generación async con jobs y status tracking
- [ ] Export a ShareGPT, Alpaca, ChatML
- [ ] Integración LiteLLM con al menos 3 providers
- [ ] Re-evaluación automática post-generación
- [ ] Canary injection para detección de memorización
- [ ] Deduplicación (ninguna conversación repetida >3 veces)

---

## Fase 5 — Capa 4: Pipeline LoRA Integrado (Sprint 17-22)

**Objetivo:** Fine-tuning automatizado con datos sintéticos certificados.

### Configuración LoRA estándar

```python
LoraConfig(
    r=16, lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj"],
    lora_dropout=0.05, bias="none", task_type="CAUSAL_LM"
)
```

### Modelos base soportados

- Qwen3-14B
- LLaMA-3.3-8B
- Mistral (versión más reciente)

### Privacy durante entrenamiento

- DP-SGD con epsilon <= 8.0
- Extraction attack testing post-entrenamiento
- Canary string verification

### Tracking con MLflow

- Cada run registra: hiperparámetros, métricas, dataset hash, modelo base, duración
- Comparación entre runs para mismo dominio
- Artifacts: adaptador LoRA, métricas de calidad, reporte de privacidad

### API Endpoints

```
POST   /api/v1/train                    # Iniciar entrenamiento
GET    /api/v1/train/status/{job_id}    # Estado del entrenamiento
GET    /api/v1/train/runs               # Listar runs (MLflow)
GET    /api/v1/train/runs/{run_id}      # Detalle de un run
POST   /api/v1/train/evaluate/{run_id}  # Evaluar adaptador post-training
```

### Entregables

- [ ] Pipeline de training LoRA/QLoRA funcional
- [ ] Integración MLflow para experiment tracking
- [ ] DP-SGD implementado con epsilon configurable
- [ ] Extraction attack testing automatizado post-training
- [ ] Benchmark automático vs modelo base
- [ ] Soporte para warm start (transfer entre dominios)
- [ ] Export de adaptador LoRA empaquetado

---

## Fase 6 — Integración, i18n, y Documentación (Sprint 23-26)

### Entregables

- [ ] Pipeline end-to-end funcional (Capa 0 → Capa 4)
- [ ] i18n completa (español y inglés) en CLI, API responses, logs, documentación
- [ ] Documentación API (OpenAPI auto-generada)
- [ ] Guía de quickstart
- [ ] Guía de seed engineering
- [ ] Guía de setup por dominio
- [ ] Piloto completo con dominio `automotive.sales`
- [ ] 50 semillas validadas en dominio piloto
- [ ] Benchmark comparativo vs. fine-tuning directo

---

## Dependencias entre fases

```
Fase 0 (Infraestructura) ──► Fase 1 (Capa 0: Semillas)
                                  │
                                  ▼
                             Fase 2 (Capa 1: Parsers)
                                  │
                                  ▼
                             Fase 3 (Capa 2: Evaluador) ◄──── PII Scanner de Fase 2
                                  │
                                  ▼
                             Fase 4 (Capa 3: Generador) ──► Re-evaluación con Capa 2
                                  │
                                  ▼
                             Fase 5 (Capa 4: LoRA)
                                  │
                                  ▼
                             Fase 6 (Integración + Piloto)
```

**Nota:** Los tests de privacidad se desarrollan incrementalmente en cada fase, no como una fase separada.
