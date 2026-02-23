# Prompt de Reproducibilidad — UNCASE Framework

> Este prompt está diseñado para ser utilizado con cualquier LLM capaz (Claude, GPT-4, Gemini, etc.) para recrear la arquitectura y estructura del proyecto UNCASE. Copia el prompt completo a continuación.

---

## Prompt

```
Eres un ingeniero de software senior especializado en Python, ML/NLP y privacidad de datos. Tu tarea es implementar desde cero el framework UNCASE (Unbiased Neutral Convention for Agnostic Seed Engineering), un sistema open-source de 5 capas para generar datos conversacionales sintéticos de alta calidad para fine-tuning de LoRA/QLoRA en industrias reguladas.

## CONTEXTO DEL PROYECTO

UNCASE resuelve un problema específico: las organizaciones con el conocimiento especializado más valioso (salud, finanzas, derecho, manufactura) son precisamente las que NO pueden usar sus datos reales para entrenar IA debido a restricciones de privacidad y regulación.

La solución: abstracción semántica — convertir conocimiento experto en estructuras parametrizadas ("semillas") sin datos sensibles, y luego generar datos sintéticos desde esas semillas para fine-tuning.

## STACK TECNOLÓGICO (obligatorio)

- Python >= 3.11
- FastAPI + Uvicorn (API REST)
- Pydantic v2 (validación de datos, schemas)
- LiteLLM (interfaz unificada a múltiples LLMs)
- structlog (logging estructurado JSON)
- Typer (CLI)
- pytest + pytest-asyncio + pytest-cov (testing)
- Ruff (linter + formatter)
- mypy (type checking estricto)
- SpaCy + Presidio (NER y detección de PII)
- transformers + peft + trl (fine-tuning LoRA)
- MLflow (experiment tracking)
- PostgreSQL + asyncpg + SQLAlchemy async (base de datos)
- uv (gestión de dependencias)
- Internacionalización: español y inglés desde el inicio

## ARQUITECTURA DE 5 CAPAS (SCSF — Synthetic Conversation Seed Framework)

### Capa 0 — Motor de Semillas (Seed Engine)
- Convierte conocimiento experto en SeedSchema v1 (JSON/YAML)
- La semilla es la unidad fundamental: contiene la estructura de una conversación sin datos sensibles
- CRUD completo con PostgreSQL
- Templates por dominio para acelerar creación

### Capa 1 — Parser y Validador Multi-formato
- 7 parsers: WhatsApp (.txt), JSON genérico, CSV turn-based, Transcript raw (Whisper), CRM Kommo, ShareGPT, OpenAI Chat
- ValidadorConversacional con 5 checks: roles consistentes (>=2), continuidad tópica, fidelidad factual vs semilla, PII residual (tolerancia=0), longitud objetivo
- PII Scanner multi-etapa: NER (SpaCy es/en) → Reglas heurísticas (CURP, RFC, CLABE, tarjetas) → Presidio → Flag para revisión humana
- Target: 10,000 conversaciones/hora

### Capa 2 — Evaluador de Calidad
- 6 métricas con umbrales:
  - ROUGE-L >= 0.65 (coherencia estructural)
  - Fidelidad Factual >= 0.90 (precisión de dominio, verificada por LLM-as-Judge)
  - Diversidad Léxica TTR >= 0.55 (Type-Token Ratio)
  - Coherencia Dialógica >= 0.85 (consistencia de roles)
  - Privacy Score = 0.00 (cero PII residual)
  - Memorización < 0.01 (extraction attack success rate)
- Fórmula compuesta: Q = min(ROUGE, Fidelidad, TTR, Coherencia) si privacy=0 Y memorización<0.01; sino Q=0
- Validación dual: automática + LLM-as-Judge
- Privacidad NO es negociable: si falla, Q=0 automáticamente

### Capa 3 — Motor de Reproducción Sintética
- 4 estrategias de diversificación: variación de persona, variación de flujo, inyección de herramientas (tool-calling), ruido controlado
- Modelos via LiteLLM: Claude Opus, Gemini, Qwen3-72B (para privacidad total on-premise), LLaMA-3.3-70B
- Ratio: 1 semilla → 200-500 conversaciones sintéticas
- Formatos de salida para training: ShareGPT, Alpaca, ChatML
- Canary injection para detectar memorización
- Deduplicación: ninguna conversación >3 veces en el dataset final
- Re-evaluación automática con Capa 2 post-generación

### Capa 4 — Pipeline LoRA Integrado
- Configuración estándar: r=16, lora_alpha=32, target_modules=["q_proj","v_proj","k_proj","o_proj","gate_proj"], lora_dropout=0.05, bias="none", task_type="CAUSAL_LM"
- Modelos base: Qwen3-14B, LLaMA-3.3-8B, Mistral
- DP-SGD con epsilon <= 8.0 durante fine-tuning
- Extraction attack testing post-entrenamiento (success rate < 1%)
- MLflow para tracking de experimentos
- Warm start: adaptador de un dominio como punto de partida para otro (reduce datos 40-60%)

## SEEDSCHEMA v1 (modelo central Pydantic)

```json
{
  "seed_id": "uuid-v4",
  "dominio": "automotive.sales",
  "esquema_version": "1.0",
  "tipo_interaccion": "consulta_financiamiento",
  "roles": ["agente_ventas", "cliente"],
  "parametros_factuales": {
    "entidades_clave": ["sedan_compacto", "enganche_20pct", "plazo_48_meses"],
    "restricciones": ["sin_historial_crediticio", "ingreso_informal"],
    "flujo_esperado": ["saludo", "identificacion_necesidad", "propuesta", "objecion", "cierre"]
  },
  "tono_objetivo": "consultivo_empatico",
  "pasos_turnos": {"turnos_min": 8, "turnos_max": 20},
  "herramientas_disponibles": ["calcular_financiamiento", "buscar_inventario"],
  "metricas_calidad": {"rouge_l_min": 0.65, "fidelidad_factual_min": 0.90},
  "privacidad": {"contiene_pii": false, "nivel_sensibilidad": "bajo"}
}
```

Campos obligatorios: seed_id, dominio, esquema_version, roles, parametros_factuales, privacidad
Campos opcionales: herramientas_disponibles, tono_objetivo, pasos_turnos

## 6 DOMINIOS SOPORTADOS (namespaces jerárquicos)

- automotive.sales (dominio piloto)
- medical.consultation
- legal.advisory
- finance.advisory
- industrial.support
- education.tutoring

## ESTRUCTURA DEL PROYECTO

```
uncase/
├── pyproject.toml
├── uncase/
│   ├── __init__.py
│   ├── __main__.py
│   ├── config.py              # pydantic-settings
│   ├── exceptions.py          # UNCASEError base
│   ├── logging.py             # structlog config
│   ├── schemas/
│   │   ├── seed.py            # SeedSchema v1
│   │   ├── conversation.py    # Modelo de conversación interna
│   │   ├── validation.py      # InformeValidacion
│   │   └── quality.py         # Métricas de calidad
│   ├── core/
│   │   ├── seed_engine/       # Capa 0
│   │   ├── parser/            # Capa 1 (7 parsers + ValidadorConversacional)
│   │   ├── evaluator/         # Capa 2 (6 métricas + LLM-as-Judge)
│   │   ├── generator/         # Capa 3 (4 estrategias)
│   │   └── lora_pipeline/     # Capa 4 (training + evaluation)
│   ├── api/
│   │   ├── main.py            # FastAPI app factory, versionado /api/v1/
│   │   ├── deps.py            # Dependency injection
│   │   └── routers/           # Un router por capa
│   ├── cli/                   # Typer commands
│   ├── domains/               # Config por dominio industrial
│   ├── i18n/                  # Español + Inglés
│   └── utils/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── privacy/               # OBLIGATORIOS antes de merge
├── examples/
│   └── automotive_sales/
└── docs/
```

## REGULACIÓN CUBIERTA

- GDPR (UE) — datos sintéticos no son datos personales
- HIPAA (EEUU) — ningún PHI transita por el pipeline
- LFPDPPP (México) — consentimiento innecesario para sintéticos
- AI Act (UE) — trazabilidad completa del pipeline
- CCPA (California) — sin recolección de datos del consumidor
- MiFID II (UE) — auditoría de comunicaciones con datos abstractos

## CONVENCIONES DE CÓDIGO

- Type hints obligatorios en toda función pública
- Docstrings Google style en español
- Logging con structlog (nunca print())
- Excepciones custom que heredan de UNCASEError
- Ruff como linter y formatter (line-length=120)
- Tests con pytest, cobertura >= 80% en core/, >= 90% en schemas/
- Async por defecto en endpoints FastAPI
- Nunca datos reales en tests — solo sintéticos/ficticios
- Nunca loguear contenido de conversaciones reales
- Toda conversación generada debe rastrear su seed_id de origen

## INSTRUCCIONES DE IMPLEMENTACIÓN

Implementa el framework siguiendo este orden:
1. Scaffolding: pyproject.toml, estructura de carpetas, config, logging, exceptions
2. SeedSchema v1 como modelo Pydantic con validaciones completas
3. FastAPI app factory con health check y OpenAPI docs
4. Capa 0: CRUD de semillas + CLI
5. Capa 1: Parsers (WhatsApp primero) + ValidadorConversacional + PII Scanner
6. Capa 2: 6 métricas + LLM-as-Judge + fórmula compuesta
7. Capa 3: Generación sintética con 4 estrategias via LiteLLM
8. Capa 4: Pipeline LoRA con DP-SGD + MLflow
9. Integración end-to-end + tests de privacidad + i18n

Prioriza siempre: privacidad primero, tests junto con implementación, i18n desde el día 1.
```

---

## Notas de uso

- Este prompt contiene toda la información necesaria de los whitepapers UNCASE v1.0 y SCSF v1.0.
- Puedes pasarlo completo a cualquier LLM con ventana de contexto >= 16K tokens.
- Para una sesión iterativa, divide por fases: pasa primero las secciones de contexto + stack + SeedSchema + la fase que quieras implementar.
- El prompt está en español pero incluye terminología técnica en inglés cuando es el estándar de la industria.
