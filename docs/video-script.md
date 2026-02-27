# UNCASE — 3-Minute Demo Video Script

**Target:** 3 minutes (~500 words narration + screen actions)
**Format:** Screen recording of production dashboard with voiceover
**URLs:** Backend API at `app.uncase.md`, Frontend dashboard on Vercel

---

## ENGLISH VERSION

### [0:00–0:15] — Opening Hook

**Screen:** Landing page → click "Get Started" → Dashboard overview loads.

> "If you work in healthcare, finance, legal, or automotive — you know the problem. You need to fine-tune an LLM on real customer conversations, but those conversations are full of PII, medical records, financial data. You can't send that to a cloud API. And anonymizing it destroys the domain patterns that make fine-tuning valuable in the first place. UNCASE fixes this. Let me show you."

### [0:15–0:50] — Dashboard Overview

**Screen:** Overview page — stats cards, domain breakdown chart, recent activity feed.

> "This is the UNCASE dashboard. At a glance: total seeds, generated conversations, quality scores, and active jobs. The system supports six regulated industries — automotive, medical, legal, finance, industrial, and education. This is important because each industry has completely different compliance requirements and vocabulary. Instead of building custom pipelines per domain, UNCASE gives you five built-in tools per industry — things like inventory lookup for automotive, or formulary check for medical — so the generated conversations actually sound like your domain, not generic chatbot filler."

### [0:50–1:20] — Creating a Seed

**Screen:** Navigate to Pipeline → Seeds. Click "Create Seed." Fill in the modal: domain `automotive.sales`, language `es`, objective "Customer negotiating financing for a certified SUV", tone "professional", roles [customer, sales_advisor], steps [Greeting, Vehicle inquiry, Financing options, Decision]. Pick tools. Submit.

> "Everything starts with a seed. Think of it as the DNA of a conversation — domain, objective, tone, roles, turn-by-turn steps — but with zero real data inside. This matters because seeds are what make everything traceable and reproducible. An auditor can inspect every seed without ever seeing real customer data. And if you regenerate from the same seed with the same config, you get consistent output — so you can version your training data the same way you version code."

*[Note to presenter: highlight the tools picker — show that domain tools are attached to the seed, not hardcoded.]*

### [1:20–1:50] — Generating Synthetic Conversations

**Screen:** Navigate to Pipeline → Generate. Select the seed, set count to 5, toggle "Evaluate after generation." Click Generate. Show the job appearing in the Jobs queue with progress, then results populating.

> "Now I send this seed to the generation engine. Under the hood, UNCASE routes through LiteLLM — so you can point it at Claude, GPT-4, Gemini, Groq, or a fully local model via Ollama or vLLM. You're never locked into a single provider. I'm generating five conversations and toggling automatic quality evaluation — which means the system will score every output before I even look at it. That's the kind of automation that saves hours of manual review on every batch."

### [1:50–2:20] — Reviewing Conversations & Quality

**Screen:** Navigate to Conversations. Open one conversation — show the chat view with correct role badges (customer/sales_advisor), tool call indicators, and the format compatibility tags (ChatML, Llama, Qwen, etc.). Then switch to Evaluations page — show the six quality metrics.

> "Here are the generated conversations. Each message is tagged by role, tool calls are clearly marked, and — this is where it gets useful — the compatibility badges automatically tell you which fine-tuning formats this conversation supports. So you could take this same conversation and export it as ChatML for Qwen, Llama 3 format for Meta models, or Mistral's format — without reformatting anything manually. On the Evaluations page, every conversation is scored on six metrics: ROUGE-L, factual fidelity, lexical diversity, dialogue coherence, a privacy score that must be exactly zero — meaning no PII leaked through — and a memorization rate below one percent to prevent extraction attacks. If any metric fails, the conversation is flagged and never makes it to export."

### [2:20–2:40] — Exporting for Fine-Tuning

**Screen:** Navigate to Pipeline → Export. Select conversations, pick Llama 3 template, click Export. Show download.

> "When quality passes, export to any of ten chat template formats — ready for LoRA or QLoRA fine-tuning. The template engine automatically handles role mapping, special tokens, BOS/EOS markers, and tool-use formatting for each target model. So you could train on Llama, switch to Mistral next week, and just re-export — no data pipeline rework. You can also preview every format on the Templates page before committing."

### [2:40–3:00] — Enterprise Features & Closing

**Screen:** Quick montage: Costs page (LLM spend tracking), Activity page (audit log), Plugins page (6 official plugins), Settings page (providers, compliance profiles).

> "For enterprise teams: LLM cost tracking per organization so you know exactly what each generation batch costs, a full audit trail for compliance — every action logged with who, what, and when — a plugin marketplace with six official plugins, and built-in compliance profiles for HIPAA, GDPR, SOX, and Mexico's LFPDPPP. It's open source under the BSD license. Deploy it on your infrastructure, keep all data on-premises, and fine-tune with confidence. Get started at uncase.md."

**Screen:** UNCASE logo + GitHub URL + "BSD License — Free for commercial use."

---

## VERSION EN ESPANOL

### [0:00–0:15] — Apertura

**Pantalla:** Landing page → clic en "Get Started" → Se carga el dashboard.

> "Si trabajas en salud, finanzas, legal o automotriz — ya conoces el problema. Necesitas hacer fine-tuning de un LLM con conversaciones reales de clientes, pero esas conversaciones están llenas de datos personales, historiales médicos, información financiera. No puedes enviar eso a una API en la nube. Y si lo anonimizas, pierdes los patrones de dominio que hacen que el fine-tuning valga la pena. UNCASE resuelve esto. Te muestro cómo."

### [0:15–0:50] — Vista General del Dashboard

**Pantalla:** Página de Overview — tarjetas de estadísticas, gráfico por dominio, feed de actividad reciente.

> "Este es el dashboard de UNCASE. De un vistazo: total de semillas, conversaciones generadas, scores de calidad y trabajos activos. El sistema soporta seis industrias reguladas — automotriz, médica, legal, financiera, industrial y educación. Esto es importante porque cada industria tiene requerimientos de cumplimiento y vocabulario completamente distintos. En vez de construir pipelines custom por dominio, UNCASE te da cinco herramientas integradas por industria — como búsqueda de inventario para automotriz, o verificación de formulario para médica — para que las conversaciones generadas suenen como tu dominio, no como relleno genérico de chatbot."

### [0:50–1:20] — Creando una Semilla

**Pantalla:** Navegar a Pipeline → Seeds. Clic en "Create Seed." Llenar el modal: dominio `automotive.sales`, idioma `es`, objetivo "Cliente negociando financiamiento para SUV certificada", tono "professional", roles [customer, sales_advisor], pasos [Saludo, Consulta del vehículo, Opciones de financiamiento, Decisión]. Seleccionar tools. Enviar.

> "Todo comienza con una semilla. Piensa en ella como el ADN de una conversación — dominio, objetivo, tono, roles, pasos turno a turno — pero con cero datos reales adentro. Esto importa porque las semillas son lo que hace todo trazable y reproducible. Un auditor puede inspeccionar cada semilla sin ver jamás datos reales de clientes. Y si regeneras desde la misma semilla con la misma configuración, obtienes resultados consistentes — así que puedes versionar tus datos de entrenamiento de la misma forma en que versionas código."

*[Nota para el presentador: resaltar el selector de herramientas — mostrar que las tools de dominio se adjuntan a la semilla, no están hardcodeadas.]*

### [1:20–1:50] — Generando Conversaciones Sintéticas

**Pantalla:** Navegar a Pipeline → Generate. Seleccionar la semilla, configurar cantidad en 5, activar "Evaluate after generation." Clic en Generate. Mostrar el job en la cola de Jobs con progreso, luego los resultados apareciendo.

> "Ahora envío esta semilla al motor de generación. Por debajo, UNCASE rutea a través de LiteLLM — así que puedes apuntarlo a Claude, GPT-4, Gemini, Groq, o un modelo completamente local vía Ollama o vLLM. Nunca estás atado a un solo proveedor. Estoy generando cinco conversaciones y activando la evaluación automática de calidad — lo que significa que el sistema va a calificar cada resultado antes de que yo siquiera lo vea. Ese tipo de automatización te ahorra horas de revisión manual en cada lote."

### [1:50–2:20] — Revisando Conversaciones y Calidad

**Pantalla:** Navegar a Conversations. Abrir una conversación — mostrar la vista de chat con badges de rol (customer/sales_advisor), indicadores de tool calls, y las etiquetas de compatibilidad de formato (ChatML, Llama, Qwen, etc.). Luego cambiar a Evaluations — mostrar las seis métricas de calidad.

> "Aquí están las conversaciones generadas. Cada mensaje está etiquetado por rol, las llamadas a herramientas están marcadas, y — aquí es donde se pone útil — los badges de compatibilidad te dicen automáticamente qué formatos de fine-tuning soporta esta conversación. Entonces podrías tomar esta misma conversación y exportarla como ChatML para Qwen, formato Llama 3 para modelos de Meta, o el formato de Mistral — sin reformatear nada manualmente. En la página de Evaluaciones, cada conversación se califica en seis métricas: ROUGE-L, fidelidad factual, diversidad léxica, coherencia dialógica, un score de privacidad que debe ser exactamente cero — o sea, que no se filtró ningún dato personal — y una tasa de memorización menor al uno por ciento para prevenir ataques de extracción. Si cualquier métrica falla, la conversación se marca y nunca llega a la exportación."

### [2:20–2:40] — Exportando para Fine-Tuning

**Pantalla:** Navegar a Pipeline → Export. Seleccionar conversaciones, elegir template Llama 3, clic en Export. Mostrar la descarga.

> "Cuando la calidad pasa los umbrales, exporta a cualquiera de diez formatos de chat template — listo para fine-tuning con LoRA o QLoRA. El motor de templates maneja automáticamente el mapeo de roles, tokens especiales, marcadores BOS/EOS, y el formato de tool-use para cada modelo destino. Entonces podrías entrenar con Llama, cambiar a Mistral la próxima semana, y simplemente re-exportar — sin rehacer el pipeline de datos. También puedes previsualizar cada formato en la página de Templates antes de comprometerte."

### [2:40–3:00] — Features Enterprise y Cierre

**Pantalla:** Montaje rápido: página de Costs (tracking de gasto LLM), página de Activity (audit log), página de Plugins (6 plugins oficiales), página de Settings (proveedores, perfiles de cumplimiento).

> "Para equipos enterprise: tracking de costos LLM por organización para que sepas exactamente cuánto cuesta cada lote de generación, un trail de auditoría completo — cada acción registrada con quién, qué y cuándo — un marketplace de plugins con seis plugins oficiales, y perfiles de cumplimiento integrados para HIPAA, GDPR, SOX y la LFPDPPP de México. Es open source bajo licencia BSD. Despliega en tu infraestructura, mantén todos los datos on-premises, y haz fine-tuning con confianza. Comienza en uncase.md."

**Pantalla:** Logo de UNCASE + URL de GitHub + "Licencia BSD — Libre para uso comercial."
