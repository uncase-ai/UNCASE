# Checklist de Validación — UNCASE contra Whitepapers

> Este checklist verifica que la implementación cumple con TODAS las especificaciones contenidas en los whitepapers UNCASE v1.0 y SCSF v1.0.
> Marca cada item solo cuando esté completamente implementado y testeado.

---

## 1. SeedSchema v1

### 1.1 Campos obligatorios
- [ ] `seed_id` — UUID v4
- [ ] `dominio` — String con namespace jerárquico (e.g., `automotive.sales`)
- [ ] `esquema_version` — String, inicialmente "1.0"
- [ ] `roles` — Lista de strings, mínimo 2 participantes
- [ ] `parametros_factuales` — Objeto con:
  - [ ] `entidades_clave` — Lista de strings
  - [ ] `restricciones` — Lista de strings
  - [ ] `flujo_esperado` — Lista de strings (pasos del diálogo)
- [ ] `privacidad` — Objeto con:
  - [ ] `contiene_pii` — Boolean
  - [ ] `nivel_sensibilidad` — String (bajo/medio/alto)

### 1.2 Campos opcionales
- [ ] `tipo_interaccion` — String descriptivo
- [ ] `tono_objetivo` — String
- [ ] `pasos_turnos` — Objeto con:
  - [ ] `turnos_min` — Int (default: 8)
  - [ ] `turnos_max` — Int (default: 20)
- [ ] `herramientas_disponibles` — Lista de strings
- [ ] `metricas_calidad` — Objeto con:
  - [ ] `rouge_l_min` — Float (default: 0.65)
  - [ ] `fidelidad_factual_min` — Float (default: 0.90)

### 1.3 Validaciones
- [ ] UUID v4 válido para seed_id
- [ ] Dominio pertenece a namespaces registrados
- [ ] roles tiene >= 2 elementos
- [ ] flujo_esperado tiene >= 1 elemento
- [ ] turnos_min < turnos_max
- [ ] contiene_pii = false si nivel_sensibilidad = "bajo"
- [ ] Formato JSON y YAML soportados para import/export
- [ ] Esquema es domain-agnostic (misma estructura para cualquier industria)

---

## 2. Capa 0 — Motor de Semillas

- [ ] Creación de semillas desde plantillas por dominio
- [ ] Creación manual de semillas
- [ ] Persistencia en PostgreSQL
- [ ] CRUD completo (crear, leer, actualizar, eliminar)
- [ ] Exportación a JSON/YAML
- [ ] Repositorio de semillas filtrable por dominio
- [ ] CLI funcional (`uncase seed create/list/validate/export`)
- [ ] API REST funcional
- [ ] Templates para dominio piloto `automotive.sales`
- [ ] 50 semillas validadas en dominio piloto (entregable de roadmap)

---

## 3. Capa 1 — Parser y Validador Multi-formato

### 3.1 Parsers (7 formatos)
- [ ] `WhatsAppParser` — Exportaciones WhatsApp (.txt)
- [ ] `JSONConversationParser` — JSON genérico (APIs, CRMs)
- [ ] `CSVDialogParser` — CSV turn-based
- [ ] `TranscriptParser` — Output de Whisper (audio→texto)
- [ ] `KommoExportParser` — Exportaciones CRM Kommo
- [ ] `ShareGPTParser` — Formato HuggingFace estándar
- [ ] `OpenAIChatParser` — Formato OpenAI Chat

### 3.2 Validador Conversacional
- [ ] `_check_roles_consistentes` — >= 2 participantes identificados
- [ ] `_check_continuidad_topica` — Coherencia temática entre turnos
- [ ] `_check_fidelidad_factual` — Consistencia con semilla de origen
- [ ] `_check_pii_residual` — Detección PII con tolerancia = 0
- [ ] `_check_longitud_objetivo` — Dentro del rango turnos_min..turnos_max
- [ ] Retorna `InformeValidacion` con resultados de todos los checks

### 3.3 PII Scanner Multi-etapa
- [ ] Etapa 1: NER con SpaCy (modelos entrenados para español e inglés)
- [ ] Etapa 2: Reglas heurísticas para:
  - [ ] CURP (México)
  - [ ] RFC (México)
  - [ ] CLABE (México)
  - [ ] Números de tarjetas de crédito
  - [ ] Coordenadas geográficas de precisión
- [ ] Etapa 3: Presidio (Microsoft) para detección probabilística multi-idioma
- [ ] Etapa 4: Flag para revisión humana si score de riesgo excede umbral
- [ ] Tolerancia PII en dataset final: **CERO**

### 3.4 Rendimiento
- [ ] Capacidad >= 10,000 conversaciones/hora con reporte automático

---

## 4. Capa 2 — Evaluador de Calidad

### 4.1 Métricas (6 con umbrales)
- [ ] ROUGE-L (ρ_ROUGE) >= 0.65 — Coherencia estructural con semilla de origen
- [ ] Fidelidad Factual (φ_fact) >= 0.90 — Precisión de entidades y datos verificables
- [ ] Diversidad Léxica (δ_TTR) >= 0.55 — Type-Token Ratio del corpus
- [ ] Coherencia Dialógica (κ_dial) >= 0.85 — Consistencia de roles inter-turno
- [ ] Privacy Score (π_priv) = 0 — Detecciones PII residual
- [ ] Memorización (μ_mem) < 0.01 — Extraction attack success rate post fine-tuning

### 4.2 Fórmula compuesta
- [ ] Q_UNCASE = min(ρ, φ, δ, κ) si π=0 AND μ<0.01
- [ ] Q_UNCASE = 0 si π>0 OR μ>=0.01
- [ ] Privacidad es gate binario: falla = calidad cero

### 4.3 Verificación dual
- [ ] Validación automatizada (métricas calculadas programáticamente)
- [ ] LLM-as-Judge (LLM evalúa fidelidad factual y coherencia)
- [ ] LLM-as-Judge usa prompt estandarizado que recibe semilla + conversación
- [ ] Correlación target con evaluación humana: r >= 0.87
- [ ] Reporte de certificación generado automáticamente

---

## 5. Capa 3 — Motor de Reproducción Sintética

### 5.1 Estrategias de diversificación (4)
- [ ] **Variación de persona**: Diferentes perfiles de interlocutor (experiencia, objeciones típicas, registro lingüístico)
- [ ] **Variación de flujo**: Happy path, objeciones tempranas, abandono y recuperación, escalación a humano
- [ ] **Inyección de herramientas**: Tool-calling con respuestas simuladas verificadas contra la semilla
- [ ] **Ruido controlado**: Correcciones, interrupciones, cambios de tema para robustez

### 5.2 Modelos de generación
- [ ] Claude Opus (Anthropic API) via LiteLLM
- [ ] Google Gemini via LiteLLM
- [ ] Qwen3-72B (local/on-premise para privacidad total) via LiteLLM
- [ ] LLaMA-3.3-70B via LiteLLM
- [ ] Interfaz agnóstica al provider (cambio de modelo sin cambio de código)

### 5.3 Formatos de salida para training
- [ ] ShareGPT format
- [ ] Alpaca format
- [ ] ChatML format

### 5.4 Ratio y calidad
- [ ] 1 semilla → 200-500 conversaciones sintéticas
- [ ] Target: 1,000 conversaciones validadas por semilla por hora
- [ ] Re-evaluación automática con Capa 2 post-generación
- [ ] Canary injection (strings únicos para detectar memorización)
- [ ] Deduplicación: ninguna conversación repetida >3 veces en dataset final

---

## 6. Capa 4 — Pipeline LoRA Integrado

### 6.1 Configuración LoRA estándar
- [ ] r = 16 (adapter rank)
- [ ] lora_alpha = 32 (learning scale)
- [ ] target_modules = ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj"]
- [ ] lora_dropout = 0.05
- [ ] bias = "none"
- [ ] task_type = "CAUSAL_LM"

### 6.2 Modelos base soportados
- [ ] Qwen3-14B
- [ ] LLaMA-3.3-8B
- [ ] Mistral (versión más reciente)

### 6.3 Herramientas de integración
- [ ] Unsloth (aceleración de fine-tuning)
- [ ] Axolotl (framework de training)
- [ ] MLflow (experiment tracking)

### 6.4 Métricas de eficiencia
- [ ] Tamaño del adaptador: 50-150 MB (vs. modelo base completo)
- [ ] Tiempo de entrenamiento: 2-8 horas en A100 (7B-14B)
- [ ] Costo de infraestructura: $15-45 USD por adaptador
- [ ] Soporte para GPUs consumer (RTX 3090/4090 via QLoRA)

### 6.5 Warm start
- [ ] Adaptador de un dominio sirve como punto de partida para otro
- [ ] Reducción documentada de datos necesarios: 40-60%

---

## 7. Privacidad — 3 capas de protección

### 7.1 Datos sintéticos certificados
- [ ] Las conversaciones se originan en el motor, no derivan de datos reales
- [ ] Las semillas NO contienen PII
- [ ] Reporte automático de certificación documenta cadena de custodia
- [ ] El reporte es auditable por terceros

### 7.2 Detección de PII residual
- [ ] NER para español e inglés (SpaCy, Flair)
- [ ] Reglas heurísticas: CURP, RFC, CLABE, tarjetas de crédito, coordenadas
- [ ] Presidio (Microsoft) para detección probabilística
- [ ] Revisión humana para conversaciones que excedan umbral de riesgo
- [ ] Tolerancia PII en dataset final: **CERO**

### 7.3 Auditoría de memorización del modelo
- [ ] Differential Privacy: DP-SGD con epsilon <= 8.0
- [ ] Extraction attack testing post-training: success rate < 1%
- [ ] Diversity forcing: ninguna conversación >3 repeticiones en dataset
- [ ] Canary injection: strings únicos para detección de memorización

---

## 8. Cumplimiento regulatorio

- [ ] GDPR (Art. 4(1), Art. 9) — Datos sintéticos no constituyen datos personales
- [ ] HIPAA — Ningún PHI transita por el pipeline
- [ ] LFPDPPP (Art. 3, México) — Consentimiento innecesario para datos sintéticos
- [ ] AI Act (Art. 10, UE) — Trazabilidad completa del pipeline de generación
- [ ] CCPA (1798.140(o), California) — Sin recolección de datos del consumidor
- [ ] MiFID II (UE) — Auditoría de comunicaciones con datos abstractos
- [ ] Toda conversación sintética referencia su seed de origen con metadatos (quién diseñó, cuándo, bajo qué parámetros)

---

## 9. Dominios soportados (6 verticales)

- [ ] `automotive.sales` — Financiamiento, inventario, negociación, lealtad (dominio piloto)
- [ ] `medical.consultation` — Triage, diagnóstico diferencial, seguimiento
- [ ] `legal.advisory` — Análisis de riesgo, due diligence, regulatorio
- [ ] `finance.advisory` — Crédito, rebalanceo de portafolio, AML
- [ ] `industrial.support` — Diagnóstico de fallas, mantenimiento predictivo
- [ ] `education.tutoring` — Evaluación adaptativa, remediación

---

## 10. Interfaces (API + CLI)

### 10.1 API REST (FastAPI)
- [ ] Versionado: `/api/v1/`
- [ ] Documentación OpenAPI auto-generada (`/api/v1/docs`)
- [ ] Health check: `GET /health`
- [ ] CRUD seeds: `POST/GET/PUT/DELETE /api/v1/seeds`
- [ ] Parsing: `POST /api/v1/parse`
- [ ] Validación: `POST /api/v1/validate/conversation`
- [ ] Evaluación: `POST /api/v1/evaluate`
- [ ] Generación: `POST /api/v1/generate`
- [ ] Training: `POST /api/v1/train`
- [ ] PII Scan: `POST /api/v1/privacy/scan`
- [ ] Responses tipadas con Pydantic models
- [ ] Error handling con excepciones custom → HTTP responses

### 10.2 CLI (Typer)
- [ ] `uncase seed create/list/validate/export`
- [ ] `uncase parse whatsapp/json/sharegpt`
- [ ] `uncase evaluate`
- [ ] `uncase generate`
- [ ] `uncase train`
- [ ] `uncase --help` funcional
- [ ] Output legible y colorizado

---

## 11. Infraestructura y calidad de código

### 11.1 Testing
- [ ] pytest como framework
- [ ] Tests unitarios en `tests/unit/`
- [ ] Tests de integración en `tests/integration/`
- [ ] Tests de privacidad en `tests/privacy/` (obligatorios antes de PR)
- [ ] Cobertura >= 80% para `core/`, >= 90% para `schemas/`
- [ ] Ningún dato real en tests

### 11.2 CI/CD
- [ ] GitHub Actions: ruff + mypy + pytest en cada PR
- [ ] Suite de privacidad incluida en CI

### 11.3 Logging
- [ ] structlog para logging estructurado (JSON)
- [ ] Nunca `print()`
- [ ] Contexto incluido en logs (seed_id, domain, etc.)
- [ ] Nunca loguear contenido de conversaciones reales

### 11.4 Internacionalización
- [ ] Español e inglés soportados
- [ ] CLI, mensajes de error, documentación en ambos idiomas
- [ ] Variable de entorno `UNCASE_DEFAULT_LOCALE` (es/en)

### 11.5 Documentación
- [ ] API auto-documentada con OpenAPI
- [ ] Guía quickstart
- [ ] Guía de seed engineering
- [ ] Guía de setup por dominio
- [ ] Docstrings Google style en español

---

## 12. Casos de uso del whitepaper (validación funcional)

### 12.1 Caso 1 — Concesionario Automotriz
- [ ] Parseo de exportaciones WhatsApp reales (con PII eliminado)
- [ ] Generación de semillas desde workshop con expertos
- [ ] 80 semillas → 40,000 conversaciones sintéticas
- [ ] Adaptador LoRA funcional en 12 semanas
- [ ] Costo de infraestructura < $3,500 USD

### 12.2 Caso 2 — Red de Atención Primaria
- [ ] Soporte para español coloquial regional
- [ ] Protocolos de triage en semillas
- [ ] Dominio `medical.consultation` funcional

### 12.3 Caso 3 — Firma de Asesoría Legal
- [ ] Privilegio abogado-cliente preservado (semillas sin datos reales)
- [ ] Patrones analíticos abstractos en semillas
- [ ] Dominio `legal.advisory` funcional

### 12.4 Caso 4 — Gestión Patrimonial
- [ ] Cumplimiento CNBV, SEC, MiFID II
- [ ] Arquetipos de conversación de asesoría
- [ ] Dominio `finance.advisory` funcional

---

## 13. Flywheel y feedback continuo

- [ ] Toda conversación en producción puede generar feedback
- [ ] El feedback alimenta nuevas semillas
- [ ] Ciclo: producción → feedback → semillas → síntesis → fine-tuning
- [ ] Pipeline MLOps para reentrenamiento (target: mensual automático)
- [ ] HITL (Human-in-the-Loop) asistido por IA

---

## Resumen de conteo

| Sección | Items |
|---|---|
| SeedSchema v1 | 20 |
| Capa 0 — Motor de Semillas | 10 |
| Capa 1 — Parser y Validador | 21 |
| Capa 2 — Evaluador de Calidad | 12 |
| Capa 3 — Motor Sintético | 16 |
| Capa 4 — Pipeline LoRA | 14 |
| Privacidad | 13 |
| Regulación | 7 |
| Dominios | 6 |
| Interfaces | 14 |
| Infraestructura | 16 |
| Casos de uso | 11 |
| Flywheel | 5 |
| **Total** | **~165 items** |
