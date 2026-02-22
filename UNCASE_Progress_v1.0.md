$$\Huge\textbf{UNCASE}$$

$$\large\textit{Unbiased Neutral Convention for Agnostic Seed Engineering}$$

$$\large\textit{Privacy-Sensitive Synthetic Asset Design Architecture}$$

---

$$\normalsize\text{Documento de Progreso — Framework Open Source}$$

$$\small\text{Versión 1.0 — 22 de febrero de 2026}$$

$$\small\text{Autor: UNCASE Contributors}$$

$$\small\text{Licencia: Por definir (Open Source)}$$

---

<br>

## $\textsf{Índice General}$

| $\textbf{§}$ | $\textbf{Sección}$ | $\textbf{Pág.}$ |
|:---:|:---|:---:|
| 1 | [Resumen Ejecutivo](#1-resumen-ejecutivo) | 2 |
| 2 | [Visión del Proyecto](#2-visión-del-proyecto) | 3 |
| 3 | [Arquitectura del Framework](#3-arquitectura-del-framework) | 4 |
| 3.1 | [Capa 0 — Motor de Semillas](#31-capa-0--motor-de-semillas-seed-engine) | 4 |
| 3.2 | [Capa 1 — Parser y Validador Multi-formato](#32-capa-1--parser-y-validador-multi-formato) | 5 |
| 3.3 | [Capa 2 — Evaluador de Calidad](#33-capa-2--evaluador-de-calidad) | 6 |
| 3.4 | [Capa 3 — Motor de Reproducción Sintética](#34-capa-3--motor-de-reproducción-sintética) | 7 |
| 3.5 | [Capa 4 — Pipeline LoRA Integrado](#35-capa-4--pipeline-lora-integrado) | 8 |
| 4 | [Estado Actual del Progreso](#4-estado-actual-del-progreso) | 9 |
| 4.1 | [Hitos Completados](#41-hitos-completados) | 9 |
| 4.2 | [En Desarrollo](#42-en-desarrollo) | 10 |
| 4.3 | [Roadmap Técnico](#43-roadmap-técnico) | 11 |
| 5 | [Especificación Técnica: SeedSchema v1](#5-especificación-técnica-seedschema-v1) | 12 |
| 6 | [Métricas de Calidad y Umbrales](#6-métricas-de-calidad-y-umbrales) | 13 |
| 7 | [Dominios Soportados](#7-dominios-soportados) | 14 |
| 8 | [Casos de Uso Validados](#8-casos-de-uso-validados) | 15 |
| 9 | [Cumplimiento Regulatorio](#9-cumplimiento-regulatorio) | 16 |
| 10 | [Estrategia Open Source](#10-estrategia-open-source) | 17 |
| 11 | [Cómo Contribuir](#11-cómo-contribuir) | 18 |
| 12 | [Referencias](#12-referencias) | 19 |
| A | [Apéndice: Glosario](#apéndice-a-glosario) | 20 |
| B | [Apéndice: Changelog](#apéndice-b-changelog) | 21 |

---

<br>

## $\S 1$ — Resumen Ejecutivo

> *"Las organizaciones con el conocimiento especializado más valioso son precisamente las que no pueden usarlo para entrenar IA."*

$$\boxed{\textbf{UNCASE} \text{ resuelve la paradoja datos-como-cuello-de-botella en industrias reguladas.}}$$

UNCASE es un **framework open source** para generar datos conversacionales sintéticos de alta calidad, diseñado específicamente para el fine-tuning mediante LoRA/QLoRA en industrias donde la privacidad de los datos es crítica.

El problema fundamental: el **73% de los proyectos de fine-tuning fracasan** debido a obstáculos de privacidad, calidad o regulación. Las industrias con mayor densidad de conocimiento especializado — salud, finanzas, derecho, manufactura — son las más restringidas para entrenar modelos de IA con sus propios datos.

UNCASE propone una solución en **5 capas** que permite a las organizaciones:

$$\text{Conocimiento Experto} \xrightarrow{\text{Abstracción}} \text{Semillas} \xrightarrow{\text{Generación}} \text{Datos Sintéticos} \xrightarrow{\text{Fine-tuning}} \text{Modelo Especializado}$$

Todo esto sin exponer un solo dato real de pacientes, clientes o usuarios.

---

<br>

## $\S 2$ — Visión del Proyecto

### $2.1$ — El Problema

La convergencia de cuatro fuerzas crea una ventana de oportunidad sin precedentes:

$$\begin{aligned}
&\textbf{(i)} \quad \text{LoRA/QLoRA reduce costos de fine-tuning por } 4 \text{ órdenes de magnitud} \\
&\textbf{(ii)} \quad \text{Modelos abiertos (Qwen3, LLaMA-3.3, Mistral, Phi-4) alcanzan masa crítica} \\
&\textbf{(iii)} \quad \text{Datos sintéticos validados empíricamente (Phi-2, Alpaca, MIMIC-III)} \\
&\textbf{(iv)} \quad \text{Regulación global se endurece (GDPR, HIPAA, AI Act, LFPDPPP)}
\end{aligned}$$

### $2.2$ — La Tesis Central

UNCASE defiende que la **abstracción semántica** — convertir conocimiento experto en estructuras parametrizadas sin datos sensibles — es la clave para democratizar el fine-tuning especializado.

### $2.3$ — Principios de Diseño

| $\textbf{Principio}$ | $\textbf{Descripción}$ |
|:---|:---|
| $\text{Privacidad por Diseño}$ | Ningún dato real transita por el pipeline |
| $\text{Agnóstico al Dominio}$ | El mismo núcleo sirve para salud, finanzas, derecho, etc. |
| $\text{Modular e Incremental}$ | Cada capa entrega valor independiente |
| $\text{Empíricamente Validable}$ | Métricas cuantificables en cada etapa |
| $\text{Open Source First}$ | Construcción pública desde el inicio |

---

<br>

## $\S 3$ — Arquitectura del Framework

$$\boxed{\text{SCSF — Synthetic Conversation Seed Framework}}$$

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA SCSF v1.0                       │
│                                                                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   │
│  │  CAPA 0  │──▶│  CAPA 1  │──▶│  CAPA 2  │──▶│  CAPA 3  │   │
│  │  Motor   │   │  Parser  │   │ Evaluador│   │  Motor   │   │
│  │  Semillas│   │ Validador│   │ Calidad  │   │ Sintético│   │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   │
│       │                                             │          │
│       │              ┌──────────┐                   │          │
│       └──────────────│  CAPA 4  │◀──────────────────┘          │
│                      │ Pipeline │                              │
│                      │   LoRA   │                              │
│                      └──────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

---

### $\S 3.1$ — Capa 0 — Motor de Semillas *(Seed Engine)*

$$\textit{Responsabilidad: Convertir conversaciones reales en estructuras semillas abstractas.}$$

El Motor de Semillas es el corazón de UNCASE. Transforma conversaciones con conocimiento experto en representaciones parametrizadas que capturan la **estructura y el razonamiento** sin retener datos identificables.

**Flujo:**

$$\text{Conversación Real} \xrightarrow[\text{PII}]{\text{Eliminación}} \text{Esquema Abstracto} \xrightarrow[\text{validación}]{\text{+}} \text{SeedSchema v1}$$

**Características clave:**

- Extracción de patrones de razonamiento experto
- Parametrización de entidades clave sin datos reales
- Definición de flujos conversacionales esperados
- Asignación de roles y tonos objetivo
- Formato de salida: `SeedSchema v1` (JSON/YAML)

---

### $\S 3.2$ — Capa 1 — Parser y Validador Multi-formato

$$\textit{Responsabilidad: Unificar múltiples formatos de entrada en el esquema interno SCSF.}$$

**Formatos soportados:**

| $\textbf{Formato}$ | $\textbf{Origen}$ | $\textbf{Estado}$ |
|:---|:---|:---:|
| Exportación WhatsApp (`.txt`) | Conversaciones móviles | $\checkmark$ Diseñado |
| JSON estructurado | APIs, CRMs | $\checkmark$ Diseñado |
| Registros CRM | Salesforce, HubSpot | $\circ$ Pendiente |
| Transcripciones | Llamadas, reuniones | $\circ$ Pendiente |
| Whisper output | Audio → texto | $\circ$ Pendiente |

**Validaciones:**

- Coherencia de roles ($\geq 2$ participantes identificados)
- Integridad temporal (secuencia lógica de turnos)
- Detección y eliminación de PII residual
- Normalización de formato hacia esquema interno

---

### $\S 3.3$ — Capa 2 — Evaluador de Calidad

$$\textit{Responsabilidad: Garantizar que solo conversaciones de alta calidad avancen al pipeline.}$$

**Sistema de métricas con umbrales:**

$$\begin{aligned}
\text{ROUGE-L} &\geq 0.65 \quad &\text{(coherencia estructural)} \\
\text{Fidelidad Factual} &\geq 0.90 \quad &\text{(precisión de dominio)} \\
\text{Diversidad Léxica (TTR)} &\geq 0.55 \quad &\text{(riqueza vocabulario)} \\
\text{Coherencia Dialógica} &\geq 0.85 \quad &\text{(consistencia de roles)} \\
\text{Privacy Score} &= 0.00 \quad &\text{(cero PII residual)} \\
\text{Model Memorization} &< 0.01 \quad &\text{(resistencia a extracción)}
\end{aligned}$$

**Método de verificación dual:**

$$\text{Validación Automatizada} + \text{LLM-as-Judge} = \text{Certificación de Calidad}$$

---

### $\S 3.4$ — Capa 3 — Motor de Reproducción Sintética

$$\textit{Responsabilidad: Generar conversaciones sintéticas diversas a partir de semillas validadas.}$$

**Estrategias de variación:**

| $\textbf{Estrategia}$ | $\textbf{Descripción}$ |
|:---|:---|
| Variación de persona | Altera perfil demográfico y contexto del usuario |
| Variación de flujo | Modifica secuencia y ramificación del diálogo |
| Inyección de herramientas | Integra tool-calling en puntos relevantes |
| Ruido controlado | Introduce interrupciones, malentendidos realistas |

**Modelos de generación:**

$$\text{Claude Opus} \quad | \quad \text{Qwen3-72B} \quad | \quad \text{LLaMA-3.3-70B}$$

**Ratio de expansión típico:**

$$1 \text{ semilla} \xrightarrow{\text{generación}} 200\text{–}500 \text{ conversaciones sintéticas}$$

---

### $\S 3.5$ — Capa 4 — Pipeline LoRA Integrado

$$\textit{Responsabilidad: Convertir datos sintéticos en adaptadores LoRA entrenados.}$$

**Formatos de salida:**

- ShareGPT
- Alpaca
- ChatML

**Configuración estándar LoRA:**

$$r = 16, \quad \alpha = 32, \quad \text{dropout} = 0.05$$

**Métricas de eficiencia:**

| $\textbf{Métrica}$ | $\textbf{Valor típico}$ |
|:---|:---|
| Tamaño del adaptador | $50 - 150$ MB vs. $28$ GB modelo base |
| Tiempo de entrenamiento | $2 - 8$ horas en A100 |
| Costo de infraestructura | $\$15 - \$45$ USD por adaptador |

---

<br>

## $\S 4$ — Estado Actual del Progreso

### $\S 4.1$ — Hitos Completados

$$\colorbox{black}{\color{white}\textbf{ FASE 0 — INVESTIGACIÓN Y DISEÑO CONCEPTUAL }}$$

| $\textbf{Hito}$ | $\textbf{Descripción}$ | $\textbf{Fecha}$ | $\textbf{Estado}$ |
|:---|:---|:---:|:---:|
| $H_{0.1}$ | Identificación del problema y tesis central | 2025 | $\checkmark$ |
| $H_{0.2}$ | Investigación de fundamentos teóricos | 2025 | $\checkmark$ |
| $H_{0.3}$ | Análisis de convergencia tecnológica | 2025 | $\checkmark$ |
| $H_{0.4}$ | Diseño de arquitectura SCSF de 5 capas | 2025 | $\checkmark$ |
| $H_{0.5}$ | Definición de SeedSchema v1 | 2025 | $\checkmark$ |
| $H_{0.6}$ | Definición de métricas y umbrales de calidad | 2025 | $\checkmark$ |
| $H_{0.7}$ | Mapeo de dominios industriales (6 verticales) | 2025 | $\checkmark$ |
| $H_{0.8}$ | Diseño de 4 casos de uso detallados | 2025 | $\checkmark$ |
| $H_{0.9}$ | Análisis regulatorio (GDPR, HIPAA, AI Act, LFPDPPP) | 2025 | $\checkmark$ |

$$\colorbox{black}{\color{white}\textbf{ FASE 1 — DOCUMENTACIÓN FUNDACIONAL }}$$

| $\textbf{Hito}$ | $\textbf{Descripción}$ | $\textbf{Fecha}$ | $\textbf{Estado}$ |
|:---|:---|:---:|:---:|
| $H_{1.1}$ | Ensayo estratégico UNCASE v1.0 (PDF, 15 pág.) | 2025 | $\checkmark$ |
| $H_{1.2}$ | Whitepaper técnico SCSF v1.0 (PDF) | 2025 | $\checkmark$ |
| $H_{1.3}$ | Post público Medium (inglés) | 2025 | $\checkmark$ |
| $H_{1.4}$ | Post público LinkedIn (español) | 2025 | $\checkmark$ |
| $H_{1.5}$ | Documento de progreso open source (este documento) | Feb 2026 | $\checkmark$ |

---

### $\S 4.2$ — En Desarrollo

$$\colorbox{black}{\color{white}\textbf{ FASE 2 — IMPLEMENTACIÓN DEL FRAMEWORK }}$$

| $\textbf{Hito}$ | $\textbf{Descripción}$ | $\textbf{Prioridad}$ | $\textbf{Estado}$ |
|:---|:---|:---:|:---:|
| $H_{2.1}$ | Repositorio público GitHub + estructura base | Alta | $\circ$ Próximo |
| $H_{2.2}$ | Implementación Capa 0 — Seed Engine (MVP) | Alta | $\circ$ Próximo |
| $H_{2.3}$ | Implementación Capa 1 — Parser WhatsApp + JSON | Alta | $\circ$ Próximo |
| $H_{2.4}$ | Implementación Capa 2 — Evaluador básico | Media | $\circ$ Pendiente |
| $H_{2.5}$ | Implementación Capa 3 — Generador sintético | Media | $\circ$ Pendiente |
| $H_{2.6}$ | Implementación Capa 4 — Pipeline LoRA | Media | $\circ$ Pendiente |
| $H_{2.7}$ | Suite de pruebas automatizadas | Alta | $\circ$ Pendiente |
| $H_{2.8}$ | CLI interactivo | Media | $\circ$ Pendiente |

$$\colorbox{black}{\color{white}\textbf{ FASE 3 — VALIDACIÓN Y PILOTO }}$$

| $\textbf{Hito}$ | $\textbf{Descripción}$ | $\textbf{Prioridad}$ | $\textbf{Estado}$ |
|:---|:---|:---:|:---:|
| $H_{3.1}$ | Piloto dominio `automotive.sales` | Alta | $\circ$ Pendiente |
| $H_{3.2}$ | Benchmark comparativo vs. fine-tuning directo | Media | $\circ$ Pendiente |
| $H_{3.3}$ | Auditoría de privacidad (extraction attack tests) | Alta | $\circ$ Pendiente |
| $H_{3.4}$ | Documentación técnica completa (API + guías) | Media | $\circ$ Pendiente |

---

### $\S 4.3$ — Roadmap Técnico

```
2025                          2026                          2027
──┬─────────────────────────────┬─────────────────────────────┬──
  │                             │                             │
  │  ████████████████████       │                             │
  │  Fase 0: Investigación      │                             │
  │  ✓ COMPLETADA               │                             │
  │                             │                             │
  │       ███████████████       │                             │
  │       Fase 1: Docs          │                             │
  │       ✓ COMPLETADA          │                             │
  │                             │                             │
  │                        ░░░░░░░░░░░░░░░░░░░               │
  │                        Fase 2: Implementación             │
  │                        ◌ EN PROGRESO                      │
  │                             │                             │
  │                             │    ░░░░░░░░░░░░░            │
  │                             │    Fase 3: Validación       │
  │                             │    ◌ PENDIENTE              │
  │                             │                             │
  │                             │              ░░░░░░░░░░░░░░░│
  │                             │              Fase 4: Release│
  │                             │              ◌ PENDIENTE    │
──┴─────────────────────────────┴─────────────────────────────┴──
```

---

<br>

## $\S 5$ — Especificación Técnica: SeedSchema v1

El `SeedSchema v1` es la estructura de datos fundamental de UNCASE. Define cómo se representan las semillas conversacionales.

```json
{
  "seed_id": "uuid-v4",
  "dominio": "automotive.ventas",
  "esquema_version": "1.0",
  "tipo_interaccion": "consulta_financiamiento",
  "roles": ["agente_ventas", "cliente"],
  "parametros_factuales": {
    "entidades_clave": [
      "sedan_compacto",
      "enganche_20pct",
      "plazo_48_meses"
    ],
    "restricciones": [
      "sin_historial_crediticio",
      "ingreso_informal"
    ],
    "flujo_esperado": [
      "saludo",
      "identificacion_necesidad",
      "propuesta",
      "objecion",
      "cierre"
    ]
  },
  "tono_objetivo": "consultivo_empatico",
  "pasos_turnos": {
    "turnos_min": 8,
    "turnos_max": 20
  },
  "herramientas_disponibles": [
    "calcular_financiamiento",
    "buscar_inventario"
  ],
  "metricas_calidad": {
    "rouge_l_min": 0.65,
    "fidelidad_factual_min": 0.90
  },
  "privacidad": {
    "contiene_pii": false,
    "nivel_sensibilidad": "bajo"
  }
}
```

**Campos obligatorios:** `seed_id`, `dominio`, `esquema_version`, `roles`, `parametros_factuales`, `privacidad`

**Campos opcionales:** `herramientas_disponibles`, `tono_objetivo`, `pasos_turnos`

---

<br>

## $\S 6$ — Métricas de Calidad y Umbrales

UNCASE define un sistema de métricas cuantificables para garantizar la calidad de los datos sintéticos en cada etapa del pipeline.

### $6.1$ — Tabla de Umbrales

| $\textbf{Métrica}$ | $\textbf{Símbolo}$ | $\textbf{Umbral}$ | $\textbf{Descripción}$ |
|:---|:---:|:---:|:---|
| Coherencia Estructural | $\rho_{\text{ROUGE}}$ | $\geq 0.65$ | ROUGE-L entre semilla y generación |
| Fidelidad Factual | $\phi_{\text{fact}}$ | $\geq 0.90$ | Precisión de hechos del dominio |
| Diversidad Léxica | $\delta_{\text{TTR}}$ | $\geq 0.55$ | Type-Token Ratio del corpus |
| Coherencia Dialógica | $\kappa_{\text{dial}}$ | $\geq 0.85$ | Consistencia inter-turno de roles |
| Puntuación de Privacidad | $\pi_{\text{priv}}$ | $= 0.00$ | Detecciones de PII residual |
| Memorización del Modelo | $\mu_{\text{mem}}$ | $< 0.01$ | Tasa de éxito de ataques de extracción |

### $6.2$ — Fórmula de Calidad Compuesta

$$Q_{\text{UNCASE}} = \begin{cases} \min\left(\rho, \phi, \delta, \kappa\right) & \text{si } \pi = 0 \land \mu < 0.01 \\ 0 & \text{en otro caso} \end{cases}$$

> Si la privacidad falla $(\pi > 0)$ o la memorización excede el umbral $(\mu \geq 0.01)$, la calidad compuesta es **cero**, independientemente de las demás métricas. La privacidad no es negociable.

---

<br>

## $\S 7$ — Dominios Soportados

SCSF v1 define namespaces jerárquicos para organizar semillas por industria y caso de uso.

| $\textbf{Industria}$ | $\textbf{Namespace}$ | $\textbf{Casos de Uso}$ |
|:---|:---|:---|
| Automotriz / Ventas | `automotive.sales` | Financiamiento, inventario, negociación, lealtad |
| Médico / Clínico | `medical.consultation` | Triage, diagnóstico diferencial, seguimiento |
| Legal / Asesoría | `legal.advisory` | Análisis de riesgo, due diligence, regulatorio |
| Financiero / Banca | `finance.advisory` | Crédito, rebalanceo de portafolio, AML |
| Industrial / Manufactura | `industrial.support` | Diagnóstico de fallas, mantenimiento predictivo |
| Educación / E-learning | `education.tutoring` | Evaluación adaptativa, remediación |

### $7.1$ — Dominio Piloto

$$\boxed{\texttt{automotive.sales} \text{ — Primer dominio de implementación y validación}}$$

**Justificación:** Mayor disponibilidad inmediata de datos conversacionales (WhatsApp), menor restricción regulatoria comparada con salud o finanzas, alto impacto medible (conversión de ventas).

---

<br>

## $\S 8$ — Casos de Uso Validados

### $\textbf{Caso 1}$ — Concesionario Automotriz (Norte de México)

$$\text{6 puntos de venta} \quad | \quad \text{150 vendedores} \quad | \quad \text{Miles de conversaciones WhatsApp}$$

| | |
|:---|:---|
| **Solución UNCASE** | Workshop de 2 días → 80 semillas → 40,000 conversaciones sintéticas → Adaptador LoRA |
| **Timeline** | 12 semanas hasta primer adaptador funcional |
| **Costo infraestructura** | \$3,500 USD |
| **Resultado esperado** | Onboarding acelerado de nuevos vendedores con asistente IA especializado |

### $\textbf{Caso 2}$ — Red de Atención Primaria (45 clínicas rurales)

$$\text{Escasez crónica de médicos de primer contacto}$$

| | |
|:---|:---|
| **Solución UNCASE** | Médicos experimentados → ingenieros de semillas → protocolos de triage sintéticos |
| **Resultado esperado** | Ampliación de capacidad de enfermería sin reemplazar médicos |

### $\textbf{Caso 3}$ — Firma de Asesoría Legal (20 años de práctica)

$$\text{Décadas de conversaciones protegidas por secreto profesional}$$

| | |
|:---|:---|
| **Solución UNCASE** | Semillas capturan patrones analíticos sin detalles de conversación |
| **Resultado esperado** | Modelo aprende rigor del dominio; privilegio permanece intacto |

### $\textbf{Caso 4}$ — Gestión Patrimonial (15 asesores, clientes HNW)

$$\text{Conversaciones de manejo de crisis sensibles a divulgación}$$

| | |
|:---|:---|
| **Solución UNCASE** | Semillas abstraen patrones de rebalanceo y comunicación de riesgo |
| **Resultado esperado** | Modelo especializado para comunicación consistente durante volatilidad |

---

<br>

## $\S 9$ — Cumplimiento Regulatorio

UNCASE está diseñado desde su concepción para cumplir simultáneamente con múltiples marcos regulatorios.

### $9.1$ — Marcos Regulatorios Cubiertos

| $\textbf{Regulación}$ | $\textbf{Jurisdicción}$ | $\textbf{Mecanismo UNCASE}$ |
|:---|:---|:---|
| GDPR (Art. 9) | Unión Europea | Datos sintéticos no constituyen datos personales |
| HIPAA | Estados Unidos | Ningún PHI transita por el pipeline |
| LFPDPPP | México | Consentimiento innecesario para datos sintéticos |
| AI Act | Unión Europea | Trazabilidad completa del pipeline de generación |
| CCPA | California | Sin recolección de datos del consumidor |
| MiFID II | Unión Europea | Auditoría de comunicaciones con datos abstractos |

### $9.2$ — Garantías de Privacidad

$$\text{Differential Privacy: DP-SGD con } \varepsilon \leq 8.0$$

$$\text{Cadena de certificación completa para auditores externos}$$

$$\text{Pruebas automatizadas de ataques de extracción (extraction attacks)}$$

---

<br>

## $\S 10$ — Estrategia Open Source

### $10.1$ — Motivación

UNCASE será publicado como framework open source por tres razones fundamentales:

$$\begin{aligned}
\textbf{(i)} \quad & \text{Transparencia: un framework de privacidad debe ser auditable públicamente} \\
\textbf{(ii)} \quad & \text{Adopción: la barrera de entrada para industrias reguladas debe ser mínima} \\
\textbf{(iii)} \quad & \text{Comunidad: la diversidad de dominios requiere contribuciones especializadas}
\end{aligned}$$

### $10.2$ — Estructura del Repositorio (Planeada)

```
uncase/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
├── docs/
│   ├── whitepaper/
│   │   ├── UNCASE_v1.0.pdf
│   │   └── SCSF_v1.0.pdf
│   ├── architecture/
│   ├── guides/
│   │   ├── quickstart.md
│   │   ├── seed-engineering.md
│   │   └── domain-setup.md
│   └── api/
├── src/
│   ├── core/
│   │   ├── seed_engine/        # Capa 0
│   │   ├── parser/             # Capa 1
│   │   ├── evaluator/          # Capa 2
│   │   ├── generator/          # Capa 3
│   │   └── lora_pipeline/      # Capa 4
│   ├── domains/
│   │   ├── automotive/
│   │   ├── medical/
│   │   ├── legal/
│   │   ├── finance/
│   │   ├── industrial/
│   │   └── education/
│   ├── schemas/
│   │   └── seed_schema_v1.json
│   └── utils/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── privacy/
├── examples/
│   ├── automotive_sales/
│   └── quickstart/
├── cli/
└── pyproject.toml
```

### $10.3$ — Stack Técnico Planeado

| $\textbf{Componente}$ | $\textbf{Tecnología}$ |
|:---|:---|
| Lenguaje principal | Python $\geq 3.11$ |
| Gestión de dependencias | `uv` / `poetry` |
| Framework de pruebas | `pytest` |
| Validación de esquemas | `pydantic` v2 |
| LLM integrations | `litellm` / SDKs nativos |
| Fine-tuning | `transformers` + `peft` + `trl` |
| CLI | `typer` / `click` |
| Documentación | MkDocs Material |

### $10.4$ — Licencia

$$\text{Por definir — Candidatas: Apache 2.0 } | \text{ MIT } | \text{ AGPL-3.0}$$

> La elección de licencia se definirá antes de la publicación del repositorio, priorizando máxima adopción con protección de atribución.

---

<br>

## $\S 11$ — Cómo Contribuir

> *Esta sección se activará cuando el repositorio sea público.*

### $11.1$ — Áreas de Contribución

| $\textbf{Área}$ | $\textbf{Perfil Ideal}$ | $\textbf{Prioridad}$ |
|:---|:---|:---:|
| Nuevos parsers (Capa 1) | Desarrolladores Python | Alta |
| Métricas de calidad (Capa 2) | Investigadores NLP | Alta |
| Dominios nuevos | Expertos de industria | Media |
| Pruebas de privacidad | Investigadores de seguridad | Alta |
| Documentación y guías | Technical writers | Media |
| Traducciones | Comunidad global | Baja |

### $11.2$ — Proceso de Contribución (Borrador)

```
1. Fork del repositorio
2. Crear rama feature/tu-contribucion
3. Implementar cambios con pruebas
4. Ejecutar suite de privacidad (obligatorio)
5. Pull request con descripción detallada
6. Code review por maintainers
7. Merge tras aprobación
```

---

<br>

## $\S 12$ — Referencias

$$\textbf{Bibliografía Técnica}$$

1. Hu, E. J., et al. (2021). *LoRA: Low-Rank Adaptation of Large Language Models.* arXiv:2106.09685.

2. Dettmers, T., et al. (2023). *QLoRA: Efficient Finetuning of Quantized Language Models.* arXiv:2305.14314.

3. Gunasekar, S., et al. (2023). *Textbooks Are All You Need.* Microsoft Research. (Phi-2)

4. Taori, R., et al. (2023). *Stanford Alpaca: An Instruction-following LLaMA Model.* Stanford University.

5. Carlini, N., et al. (2021). *Extracting Training Data from Large Language Models.* USENIX Security.

6. Acemoglu, D. & Restrepo, P. (2019). *Automation and New Tasks: How Technology Displaces and Reinstates Labor.* Journal of Economic Perspectives.

7. IMF (2024). *Gen-AI: Artificial Intelligence and the Future of Work.* IMF Staff Discussion Notes.

8. Johnson, A., et al. (2016). *MIMIC-III, a freely accessible critical care database.* Scientific Data.

$$\textbf{Marcos Regulatorios}$$

9. Reglamento General de Protección de Datos (GDPR), Unión Europea, 2018.

10. Health Insurance Portability and Accountability Act (HIPAA), Estados Unidos, 1996.

11. Ley Federal de Protección de Datos Personales en Posesión de los Particulares (LFPDPPP), México, 2010.

12. AI Act, Unión Europea, 2024.

13. California Consumer Privacy Act (CCPA), California, 2020.

---

<br>

## Apéndice A: Glosario

| $\textbf{Término}$ | $\textbf{Definición}$ |
|:---|:---|
| **UNCASE** | Unbiased Neutral Convention for Agnostic Seed Engineering |
| **SCSF** | Synthetic Conversation Seed Framework |
| **Semilla (Seed)** | Estructura abstracta que codifica conocimiento experto sin datos sensibles |
| **SeedSchema** | Formato estándar JSON/YAML para representar semillas |
| **LoRA** | Low-Rank Adaptation — técnica de fine-tuning eficiente |
| **QLoRA** | Quantized LoRA — LoRA con cuantización para reducir requisitos de hardware |
| **PII** | Personally Identifiable Information — datos personales identificables |
| **TTR** | Type-Token Ratio — medida de diversidad léxica |
| **ROUGE-L** | Métrica de similitud basada en subsecuencia común más larga |
| **DP-SGD** | Differentially Private Stochastic Gradient Descent |
| **Namespace** | Identificador jerárquico de dominio (e.g., `automotive.sales`) |
| **Adaptador** | Modelo LoRA entrenado, resultado final del pipeline |
| **LLM-as-Judge** | Uso de un LLM como evaluador de calidad de generaciones |

---

<br>

## Apéndice B: Changelog

### $\texttt{[2026-02-22]}$ — Documento de Progreso v1.0

- Creación del documento de progreso del framework
- Documentación de hitos completados (Fase 0 y Fase 1)
- Definición de roadmap técnico (Fases 2, 3, 4)
- Estructura de repositorio open source planeada
- Stack técnico definido
- Guía de contribución en borrador

### $\texttt{[2025]}$ — Fase Fundacional

- Publicación de ensayo estratégico UNCASE v1.0
- Publicación de whitepaper técnico SCSF v1.0
- Posts públicos en Medium (EN) y LinkedIn (ES)
- Diseño completo de arquitectura de 5 capas
- Especificación SeedSchema v1
- Mapeo de 6 dominios industriales
- 4 casos de uso detallados

---

<br>

$$\rule{12cm}{0.4pt}$$

$$\small\text{UNCASE — Framework Open Source para Datos Sintéticos en Industrias Reguladas}$$

$$\small\text{© 2025–2026 UNCASE Contributors. Todos los derechos reservados hasta publicación de licencia.}$$

$$\small\textit{Este documento se actualizará conforme avance el desarrollo del framework.}$$
