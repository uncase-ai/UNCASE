# UNCASE — Video Overview para Landing Page (3 min)

> **Duración:** ~3 minutos
> **Formato:** Grabación de pantalla con voz en off
> **Propósito:** Overview rápido del dashboard para la landing page. No se crea nada desde cero — ya hay seeds, conversaciones y evaluaciones cargadas.
> **Tono:** Ágil, directo, seguro. Como si le mostraras algo a un colega en 3 minutos.
>
> `[HACER]` = acción en pantalla (no se dice)
> `[ESPERAR X]` = pausar X segundos
> Líneas sin marcador = narración en voz alta

---

## Intro (0:00–0:20)

`[HACER] Dashboard abierto en /dashboard. Overview con datos ya cargados — seeds, conversaciones, evaluaciones.`
`[ESPERAR 2]`

Este es el dashboard de UNCASE. Desde aquí manejas todo el pipeline para generar datos conversacionales sintéticos — los que usarías para hacer fine-tuning de un modelo de lenguaje sin exponer datos reales.

`[HACER] Mover el cursor lentamente por el diagrama del pipeline.`

Seis etapas, en secuencia. Seeds, conocimiento, importación, evaluación, generación y exportación. Vamos a recorrerlas.

---

## Seeds (0:20–0:55)

`[HACER] Click en "Seeds" en el sidebar. La biblioteca de seeds se muestra con varios seeds ya creados.`
`[ESPERAR 2]`

Aquí están los seeds — los blueprints de cada conversación. Cada seed define el dominio, los roles, el objetivo, el tono y los umbrales de calidad que debe cumplir cada conversación generada.

`[HACER] Click en un seed de "Automotive Sales" para ver el detalle.`
`[ESPERAR 2]`

Por ejemplo, este seed es para ventas automotrices. Tiene dos roles — cliente y vendedor — un rango de turnos, y umbrales mínimos para cada métrica de calidad. Si la conversación generada no cumple con estos números, no pasa.

`[HACER] Señalar brevemente los umbrales de calidad — ROUGE-L, Fidelidad, TTR, Coherencia.`
`[ESPERAR 1]`

Y el privacy score siempre debe ser cero. Cero PII en la salida final. Eso no es configurable — es un requisito fijo.

---

## Generación (0:55–1:25)

`[HACER] Click en "Generate" en el sidebar. La página muestra seeds seleccionados y configuración.`
`[ESPERAR 2]`

En la página de generación seleccionas los seeds que quieres usar, ajustas la temperatura y el número de conversaciones por seed.

`[HACER] Señalar los seeds seleccionados a la izquierda, la configuración a la derecha.`

El sistema se conecta a tu proveedor de LLM — Claude, GPT, Gemini, Ollama, lo que tengas configurado — y genera las conversaciones pasándolas por un interceptor de privacidad que escanea cada prompt y cada respuesta.

`[HACER] Señalar el resumen de generación y el historial de ejecuciones previas.`
`[ESPERAR 1]`

Aquí puedes ver ejecuciones anteriores. Cada una registra cuántas conversaciones se generaron, con qué temperatura, y en qué modo.

---

## Evaluación (1:25–2:00)

`[HACER] Click en "Evaluations" en el sidebar. La página carga con datos.`
`[ESPERAR 3]`

Cada conversación generada se evalúa automáticamente contra seis métricas.

`[HACER] Señalar las tarjetas de resumen — total, tasa de aprobación, score compuesto, violaciones de privacidad.`

Tasa de aprobación, score compuesto promedio, y violaciones de privacidad — que deben ser cero.

`[HACER] Señalar el histograma.`
`[ESPERAR 1]`

Este histograma muestra la distribución de scores. Azul son las que pasaron, gris las que no.

`[HACER] Señalar el radar chart.`
`[ESPERAR 2]`

Y el radar compara lo que obtuviste contra lo mínimo aceptable. Si algún eje baja del umbral, sabes exactamente qué corregir.

---

## Conversaciones (2:00–2:30)

`[HACER] Click en "Conversations" en el sidebar. Vista de panel dividido con lista a la izquierda y detalle a la derecha.`
`[ESPERAR 2]`

Desde aquí puedes explorar cada conversación. Filtrar por dominio, por estado, por rating.

`[HACER] Click en una conversación. El detalle se muestra a la derecha con mensajes coloreados por rol.`
`[ESPERAR 2]`

Cada turno es editable. Puedes refinar el texto, insertar tool calls con autocompletado de herramientas del dominio, agregar tags, calificar de una a cinco estrellas, y marcar como válida o inválida. Solo las válidas entran al export.

`[HACER] Click rápido en un mensaje para mostrar el modo edición, luego cancelar.`
`[ESPERAR 1]`

---

## Exportación (2:30–2:50)

`[HACER] Click en "Export" en el sidebar. La página de exportación carga.`
`[ESPERAR 2]`

La etapa final. Eliges un template — ChatML, Llama 3, Mistral, OpenAI, Qwen — y el sistema formatea todas tus conversaciones en ese formato, listas para fine-tuning.

`[HACER] Señalar el panel de certificación de calidad a la derecha.`
`[ESPERAR 2]`

Y además genera un certificado de calidad con trazabilidad completa de seeds, métricas, cumplimiento regulatorio y garantía de cero PII. Descargable como documento HTML para auditoría.

---

## Cierre (2:50–3:00)

`[HACER] Volver al Overview.`
`[ESPERAR 2]`

De seed a dataset certificado, en minutos. Sin datos reales. Calidad medida, no asumida. Open source y en GitHub.

`[HACER] Mantener el overview 3 segundos.`
`[ESPERAR 3]`

---

## Referencia de tiempos

| Sección | Inicio | Duración |
|---------|--------|----------|
| Intro | 0:00 | 20s |
| Seeds | 0:20 | 35s |
| Generación | 0:55 | 30s |
| Evaluación | 1:25 | 35s |
| Conversaciones | 2:00 | 30s |
| Exportación | 2:30 | 20s |
| Cierre | 2:50 | 10s |
| **Total** | | **~3:00** |

---

## Notas de grabación

- El dashboard debe tener datos ya cargados antes de grabar — seeds, conversaciones generadas, evaluaciones completadas
- Usar modo oscuro — se ve mejor en video
- No pausar demasiado en ninguna sección — esto es un overview, no un tutorial
- El radar chart es el momento visual más fuerte — dejar que respire 2 segundos
- Terminar en el overview para cerrar el ciclo visualmente
