# UNCASE Framework — Guión de Video Demo (Español)

**Duración:** ~20-25 minutos
**Formato:** Grabación de pantalla + voz en off
**Autor:** Mariano Morales

---

## INTRO [0:00 - 1:30]

Hola. Mi nombre es Mariano Morales y te voy a guiar a través del framework UNCASE.

La idea es mostrarte qué tan poderoso es. Y cómo acerca a las industrias reguladas — o a cualquier persona que trabaje con datos sensibles — a un fine-tuning especializado y de alta calidad.

¿Qué vamos a lograr hoy? Producir una cantidad importante de conversaciones certificadas. Específicas para tu industria. Matemáticamente validadas. Computacionalmente auditadas. En 10 formatos diferentes, listas para alimentar un proceso de fine-tuning.

Si te quedas hasta el final, te voy a mostrar cómo levantar una instancia de inferencia con vLLM usando el modelo resultante.

Pero antes de meternos de lleno, déjame darte el pitch de 30 segundos.

UNCASE significa Unbiased Neutral Convention for Agnostic Seed Engineering. Es un framework open source diseñado para generar datos conversacionales sintéticos. ¿Para qué? Para hacer fine-tuning de adaptadores LoRA y QLoRA. Específicamente pensado para industrias donde no puedes simplemente aventarle datos reales a un modelo. Salud, finanzas, legal, automotriz, manufactura. Si tus datos tienen PII o restricciones regulatorias, este es tu pipeline.

El framework sigue una arquitectura de cinco capas que llamamos SCSF. La Capa 0 elimina PII de conversaciones reales y las convierte en semillas. La Capa 1 parsea y valida. La Capa 2 evalúa calidad con seis métricas matemáticas. La Capa 3 genera conversaciones sintéticas usando cualquier proveedor de LLM a través de un gateway unificado. Y la Capa 4 se encarga del fine-tuning LoRA con privacidad diferencial integrada.

Cada conversación que sale de este pipeline es rastreable hasta su semilla de origen. Cada una está evaluada contra seis dimensiones de calidad. Y cada una está certificada con cero PII residual. Cero. No bajo. Cero.

Empecemos.

---

## INSTALACIÓN [1:30 - 4:00]

*[Pantalla: terminal]*

Vamos a instalar el framework. Voy a abrir mi terminal y copiar el comando de git clone para descargarlo en mi carpeta de Proyectos.

```
git clone https://github.com/uncase-ai/UNCASE.git
cd UNCASE
```

También puedes usar Docker o pip. Aunque si no vas a usar git, te recomiendo `uv`. Con pip sería `pip install uncase` para el core, o `pip install "uncase[all]"` para todo — dependencias de ML, herramientas de privacidad, tooling de desarrollo, todo el paquete. Con Docker, un simple `docker compose up -d` te levanta el servidor API más PostgreSQL.

Una vez descargado, voy a usar `uv` para configurar el entorno. `uv` es un gestor de paquetes de Python ultrarrápido. Piensa en pip pero con esteroides.

```
cd uncase
uv sync --extra all
```

*[Pantalla: uv instalando dependencias]*

Esto instala el core del framework más todos los extras. Incluye transformers, peft y trl para fine-tuning. SpaCy y Presidio para detección de PII. Pytest y ruff para desarrollo. MLflow para tracking de experimentos. El archivo `uv.lock` garantiza reproducibilidad. Todos en tu equipo van a tener exactamente el mismo entorno.

Ahora levanto el backend API.

```
uv run uvicorn uncase.api.main:app --reload --port 8000
```

Y en una segunda terminal, el dashboard frontend.

```
cd ../frontend
npm install
npm run dev
```

Listo. Ya debería poder visitar el framework abriendo mi navegador en localhost puerto 3000.

*[Pantalla: navegador abriendo localhost:3000]*

Ahí está. Esta es la landing page de UNCASE. Te da un panorama general del framework, la arquitectura, enlaces al whitepaper. Pero lo que nos interesa hoy es el dashboard. Voy a hacer clic en "App" en la navegación.

---

## PANORAMA DEL DASHBOARD [4:00 - 5:30]

*[Pantalla: página de overview del dashboard]*

Esto es el dashboard principal. En la barra lateral izquierda tienes el pipeline completo en orden. Seeds, Knowledge Base, Import, Evaluate, Generate, Export. Debajo tienes el Workbench — Conversations, Templates, Tools. Y al final, Insights para tus métricas de evaluación y Activity para el log de eventos.

La página de overview te muestra una representación visual del pipeline de 6 etapas. Tus estadísticas actuales — cuántas semillas has creado, cuántas conversaciones generadas, evaluaciones completadas. Y una guía de inicio rápido si es tu primera vez.

Algo importante que quiero señalar. Este dashboard funciona en dos modos. Si tu backend API está corriendo en el puerto 8000, todo se conecta a servicios reales — PostgreSQL, proveedores de LLM, el evaluador completo. Si el API no está disponible, el dashboard cae a localStorage — modo demo. Todo sigue funcionando, simplemente no tienes generación real con LLM. Para este demo, te voy a mostrar ambos.

Empecemos por donde empieza todo pipeline: con una semilla.

---

## CREACIÓN DE SEMILLAS [5:30 - 9:30]

*[Pantalla: página de Seeds]*

Esta es la Biblioteca de Semillas. Las semillas son el ADN de tus conversaciones sintéticas. Una semilla define todo sobre cómo debe verse una conversación. El dominio, los participantes, la estructura, las restricciones, los umbrales de calidad. Piensa en ella como un plano que el generador va a seguir para producir conversaciones coherentes y fundamentadas en hechos.

Voy a crear una. Le doy clic a "Create Seed."

*[Pantalla: wizard de creación de semilla]*

El wizard te guía en seis pasos.

Primero, **Información Básica**. Necesito elegir un dominio. El framework soporta seis namespaces de industria de fábrica: `automotive.sales`, `medical.consultation`, `legal.advisory`, `finance.advisory`, `industrial.support` y `education.tutoring`. Voy a elegir `automotive.sales` porque es nuestro dominio piloto.

Idioma — lo pongo en español, `es`. Y agrego unas etiquetas: "ventas", "financiamiento", "SUV".

Siguiente paso, **Roles**. Necesito al menos dos roles. Para ventas automotriz, eso es "vendedor" — el asesor de ventas — y "cliente". Para cada rol escribo una descripción. El vendedor es "Asesor de ventas certificado con conocimiento de inventario, financiamiento y proceso de entrega." El cliente es "Prospecto interesado en adquirir un vehículo nuevo, comparando opciones y condiciones de financiamiento."

Estas descripciones importan. Le dicen al generador cómo debe comportarse cada rol. Qué vocabulario usar. A qué conocimiento tiene acceso.

Paso tres, **Estructura de Turnos**. El objetivo — ¿qué debe lograr esta conversación? Escribo: "Guiar al cliente desde la consulta inicial hasta la cotización formal de un vehículo, abordando necesidades, presupuesto y opciones de financiamiento."

Tono: "profesional". Rango de turnos: mínimo 4, máximo 8. Y el flujo esperado — este es el esqueleto de la conversación. Defino: "saludo", "detección de necesidades", "presentación de opciones", "discusión de financiamiento", "cotización", "cierre". Este flujo le dice al generador cómo debe verse la conversación estructuralmente. Y después el evaluador va a medir la coherencia contra este flujo.

Paso cuatro, **Parámetros Factuales**. Aquí se pone específico por industria. Contexto: "Agencia automotriz premium con inventario de sedanes, SUVs y pickups. Temporada de ofertas de fin de año." Restricciones — estas son las reglas que la conversación debe seguir: "No mencionar descuentos superiores al 15%", "Siempre ofrecer prueba de manejo", "Mencionar garantía extendida en todas las cotizaciones." Herramientas disponibles: "cotizador", "inventario_consulta", "calculadora_financiamiento".

Paso cinco, **Configuración de Privacidad**. La eliminación de PII está habilitada por defecto usando Presidio con un umbral de confianza de 0.85. Esto viene preconfigurado. En la mayoría de los casos lo dejas como está.

Y paso seis, **Revisión**. Aquí ves la semilla completa antes de confirmar. Dominio, roles, estructura de turnos, restricciones, umbrales de calidad. Los umbrales vienen con los defaults del framework — ROUGE-L en 0.65, Fidelidad Factual en 0.90, Diversidad Léxica en 0.55, Coherencia Dialógica en 0.85. Puedes ajustarlos si quieres más estrictos. El score de privacidad está fijo en cero. No es negociable. Y la memorización debe mantenerse debajo de 0.01.

*[Clic en "Create"]*

Listo. Semilla creada. Puedes verla en la biblioteca con su ID único, la etiqueta de dominio, el rango de turnos, el preview del objetivo y todas las especificaciones técnicas. Voy a crear dos o tres semillas más rápidamente — una para un escenario de trade-in, una para compra de flotilla, y una para consulta exclusiva de financiamiento.

*[Avance rápido creando 3 semillas más]*

Ahora tengo cuatro semillas en mi biblioteca. Cada una define un escenario diferente de ventas automotriz. Con restricciones diferentes. Flujos diferentes. Requerimientos de herramientas diferentes. Esta es la base de datos sintéticos diversos y de alta calidad.

---

## BASE DE CONOCIMIENTO [9:30 - 11:00]

*[Pantalla: página de Knowledge Base]*

Antes de generar cualquier cosa, voy a alimentar al pipeline con conocimiento de dominio. Esta es la Base de Conocimiento. Te permite subir documentos que fundamentan tus conversaciones en hechos reales.

Tengo un catálogo de productos aquí — un archivo markdown con especificaciones de vehículos, niveles de precios, términos de financiamiento. Lo arrastro al área de carga.

*[Arrastrar y soltar archivo]*

El framework auto-fragmenta el documento. Puedes ver cómo lo dividió en fragmentos de aproximadamente 800 caracteres con 100 caracteres de traslape entre ellos. Cada fragmento recibe un tipo de conocimiento — tengo cuatro opciones: facts, procedures, terminology o reference. Le pongo "facts" y lo asocio con el dominio `automotive.sales`.

¿Por qué importa esto? Cuando el generador crea una conversación sobre una SUV, puede referenciar especificaciones reales de tu catálogo en lugar de alucinar números. La métrica de fidelidad factual en la Capa 2 va a verificar que la conversación generada se alinee con estos datos.

Subo uno más — un documento de procedimientos de financiamiento — y lo marco como "procedures".

Listo. Dos documentos subidos, fragmentados correctamente, listos para informar la generación.

---

## GENERACIÓN SINTÉTICA [11:00 - 14:30]

*[Pantalla: página de Generate]*

Aquí es donde se pone emocionante. La página de Generate es la Capa 3 — el Motor de Reproducción Sintética. Te lo explico paso a paso.

Primero, selecciono qué semillas usar. Marco las cuatro. Puedes ver cada semilla con su ID, etiqueta de dominio, idioma, roles, rango de turnos y objetivo.

Ahora, parámetros de generación. **Conversaciones por semilla**: lo pongo en 5. Eso significa 4 semillas por 5 conversaciones = 20 conversaciones en total. Para una corrida de producción real harías 50 o 100 por semilla. Pero 20 es suficiente para demostrar.

**Temperatura**: 0.7. Esto controla la creatividad del LLM. Más bajo es más determinista. Más alto es más variado. 0.7 es el punto ideal para datos conversacionales. Suficiente diversidad para evitar repetición. Suficiente control para mantenerse en línea.

**Override de idioma**: lo dejo en "Use seed default". Cada semilla ya especifica español.

**Evaluar después de generar**: esto lo activo. Le dice al pipeline que ejecute automáticamente la evaluación de calidad de la Capa 2 en cada conversación justo después de generarla. Si una conversación no cumple los umbrales, lo voy a saber de inmediato.

*[Revisar indicador de status del API]*

Puedo ver que el indicador del API muestra "API Connected". El backend está corriendo, así que esto va a usar el gateway real de LLM. El gateway soporta Claude, Gemini, Qwen, LLaMA — cualquier proveedor que hayas configurado a través de LiteLLM. Para este demo tengo Claude configurado.

Le doy a "Generate".

*[Clic en Generate, mostrar barra de progreso]*

Mira la barra de progreso. El generador está haciendo varias cosas por cada conversación. Toma la semilla. Construye un prompt específico del dominio con las descripciones de roles, el flujo esperado, las restricciones y los fragmentos de conocimiento de nuestro catálogo. Lo envía al LLM a través del interceptor de privacidad — que escanea el prompt por PII a la salida y escanea la respuesta al regreso. Después parsea la respuesta del LLM a nuestro formato estructurado de conversación. Valida el conteo de turnos. Verifica los roles. Y lo almacena.

*[Barra de progreso completa]*

Listo. 20 conversaciones generadas. Puedes ver el resumen: 20 generadas. Y como activamos "Evaluate after", ya corrió las revisiones de calidad. Mira: 18 pasaron, 2 fallaron. Score compuesto promedio de 0.87.

Las dos que fallaron — puedo ver las razones aquí. Una tuvo un ROUGE-L debajo de 0.65, lo que significa que su estructura se desvió demasiado del flujo esperado. La otra tuvo un problema de fidelidad — probablemente alucinó un precio que no coincide con nuestro catálogo.

Este es exactamente el punto. El pipeline no solo genera. Certifica. Esas dos conversaciones que fallaron no van a llegar al export a menos que las corrija o las marque como inválidas.

---

## EVALUACIÓN DE CALIDAD [14:30 - 17:30]

*[Pantalla: página de Evaluate]*

Vamos a profundizar en la evaluación. Este es el corazón de UNCASE. Lo que lo separa de simplemente promptear un LLM y cruzar los dedos.

Puedo ver las 20 conversaciones listadas aquí. Las que tienen una etiqueta verde de "Passed" cumplieron los seis umbrales. Las que tienen etiqueta roja de "Failed" no. Voy a hacer clic en una de las que pasaron para ver el desglose completo.

*[Clic en una fila de conversación]*

Mira esta gráfica de radar. Seis ejes. Seis métricas. Te explico cada una.

**ROUGE-L: 0.78.** Mide coherencia estructural. Qué tan bien la conversación sigue el flujo esperado definido en la semilla. El umbral es 0.65 y estamos en 0.78. Calcula la subsecuencia común más larga entre la estructura de la conversación generada y el patrón de flujo esperado. Después computa el F1 score.

**Fidelidad Factual: 0.93.** Revisa si la conversación acertó en los hechos. ¿El vendedor mencionó el nivel de precio correcto? ¿Siguió la restricción de no exceder el 15% de descuento? ¿Ofreció la prueba de manejo como se requiere? 0.93 significa que acertó en casi todos los marcadores factuales.

**Diversidad Léxica: 0.62.** Este es el Type-Token Ratio. Palabras únicas divididas entre palabras totales en todos los turnos. Queremos al menos 0.55 para asegurar que las conversaciones no sean repetitivas o formulaicas. 0.62 es saludable.

**Coherencia Dialógica: 0.89.** Mide si la conversación tiene sentido turno por turno. ¿Los roles alternan correctamente? ¿Cada turno referencia o construye sobre el anterior? ¿Hay una progresión lógica? 0.89 es sólido.

**Privacy Score: 0.00.** Cero. Exactamente donde debe estar. El scanner de Presidio corrió sobre cada turno de esta conversación y encontró cero PII residual. Sin nombres, sin teléfonos, sin emails, sin números de tarjeta, sin CURP, sin RFC. Esta es la compuerta dura. Si este número es cualquier cosa diferente de cero, la conversación entera falla. Sin importar qué tan buenas sean las otras métricas.

**Memorización: 0.00.** Esta métrica se vuelve crítica durante el fine-tuning en la Capa 4. Mide si al modelo se le puede engañar para regurgitar datos de entrenamiento. En tiempo de generación es cero por defecto. Pero durante el entrenamiento forzamos que se mantenga debajo de 0.01 usando privacidad diferencial con un epsilon de 8.0.

El **score compuesto** se calcula como el mínimo de las cuatro dimensiones de calidad. En este caso es 0.62, limitado por la diversidad léxica. Está por encima de cero. Privacidad limpia. Memorización limpia. Esta conversación **pasa**.

Ahora veamos una de las que fallaron.

*[Clic en una conversación fallida]*

¿Ves? ROUGE-L cayó a 0.58 — debajo del umbral de 0.65. Viendo la conversación, el generador se salió del guión. El flujo esperado era saludo, detección de necesidades, presentación, financiamiento, cotización, cierre. Pero esta conversación se saltó la detección de necesidades por completo y brincó directo a presentar un vehículo. Estructuralmente incoherente para nuestro caso de uso. El score compuesto colapsa a cero porque falló un umbral.

Esto es lo que quiero decir con matemáticamente guardrailed. No dependemos de intuición ni de revisión manual. Las matemáticas te dicen qué conversaciones están listas para producción y cuáles no.

Bajo al **Quality Gate Summary**. 18 de 20 pasaron. Eso es una tasa de aprobación del 90%. El score compuesto promedio del batch es 0.87. Desglose de fallas: 1 falla de ROUGE-L, 1 falla de fidelidad. Si quisiera mejorar esto, podría refinar las restricciones de mis semillas o ajustar la temperatura.

---

## CONVERSACIONES Y EDICIÓN [17:30 - 19:00]

*[Pantalla: página de Conversations]*

Voy a la página de Conversaciones. Aquí puedo ver las 20 conversaciones en una tabla. ID de conversación, dominio, idioma, número de turnos, si es sintética, y el status.

Puedo filtrar por dominio, por sintéticas o reales, y por status. Voy a filtrar para mostrar solo las que fallaron. Ahí están. Las dos que no pasaron evaluación. Para cada una tengo tres opciones en este dropdown: puedo editar la conversación, marcarla como inválida para que se excluya del export, o eliminarla por completo.

Voy a entrar a una para editarla.

*[Pantalla: página de detalle de conversación]*

Esta es la conversación completa. Cada turno mostrado como una burbuja de chat — rol, contenido, herramientas usadas si aplica. Puedo ver los metadatos a la derecha: ID de semilla, dominio, idioma, fecha de creación.

¿Ves ese turno donde el vendedor se saltó la detección de necesidades? Puedo hacer clic en el ícono de edición en cualquier turno. Modificar el contenido aquí mismo inline. Agregar la detección de necesidades faltante. Guardar. Y después re-evaluar. Para este demo simplemente la marco como inválida para que no contamine el export.

*[Clic en "Mark as Invalid"]*

Listo. Ahora tiene un banner de "Invalid". La etapa de export la va a excluir automáticamente.

---

## EXPORT [19:00 - 21:00]

*[Pantalla: página de Export]*

Ahora la parte divertida — empaquetar estos datos para fine-tuning. La página de Export es donde tus datos certificados se convierten en training-ready.

Necesito seleccionar qué conversaciones exportar. Filtro solo las que pasaron y están válidas. Eso me da 18. Seleccionar todas.

Ahora, el **template**. Aquí es donde UNCASE brilla por interoperabilidad. El framework viene con 10 templates de salida. Alpaca, ChatML, Llama 3/4, Mistral v3, OpenAI API, Qwen 3, Nemotron, Harmony de Cohere, MiniMax y Moonshot Kimi. Cada template estructura la conversación de manera diferente para diferentes frameworks de entrenamiento y familias de modelos.

Voy a seleccionar **ChatML**. Tiene soporte amplio en herramientas de training como Axolotl y LLaMA-Factory. Y soporta tool calls de manera nativa. El template va a formatear cada conversación con los tokens especiales `<|im_start|>` y `<|im_end|>`.

**Modo de tool calls**: "inline". Esto incrusta cualquier tool call directamente en el texto de la conversación. Es lo que la mayoría de los setups de LoRA esperan.

Le doy a "Export".

*[Clic en Export]*

Listo. 18 conversaciones exportadas. El archivo se descargó a mi máquina. Déjame abrirlo rápido en la terminal.

*[Cambiar a terminal]*

```
head -1 uncase_export_chatml.txt | python -m json.tool
```

*[Mostrar JSON formateado]*

Ahí está. Cada conversación formateada correctamente con el system prompt. Todos los turnos envueltos en tokens de ChatML. Tool calls inline. Metadata preservada. Este archivo está listo para alimentar directamente tu pipeline de fine-tuning.

---

## VISTA DEL PIPELINE [21:00 - 21:30]

*[Pantalla: página de Pipeline]*

Antes de pasar al fine-tuning, te muestro la página de Pipeline. Esta te da la vista panorámica del workflow completo de SCSF. Seis etapas conectadas en secuencia.

Seed Engineering → Knowledge Base → Data Import → Quality Evaluation → Synthetic Generation → Dataset Export.

Cada etapa muestra un indicador de preparación — cuántas semillas creadas, documentos subidos, conversaciones evaluadas. Y cada etapa te lleva directo a su página. Este es tu centro de control.

---

## FINE-TUNING CON LoRA [21:30 - 24:00]

*[Pantalla: terminal]*

Ahora vamos a tomar ese archivo exportado y hacer fine-tuning de un modelo de verdad. El framework UNCASE incluye todas las dependencias de ML que necesitas — transformers, peft, trl, bitsandbytes, accelerate. Todas son parte del extra `[ml]` que instalamos al inicio.

Para este demo voy a usar LLaMA 3.1 8B como modelo base con cuantización QLoRA de 4 bits. Tengo una A100 disponible, pero este setup funciona en una GPU de consumo con 24GB de VRAM también.

```
uv run python -c "
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset
import torch

# Configuración de cuantización 4-bit
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type='nf4',
    bnb_4bit_compute_dtype=torch.bfloat16,
)

# Cargar modelo base
model = AutoModelForCausalLM.from_pretrained(
    'meta-llama/Llama-3.1-8B-Instruct',
    quantization_config=bnb_config,
    device_map='auto',
)
tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-3.1-8B-Instruct')

# Configuración del adaptador LoRA
lora_config = LoraConfig(
    r=64, lora_alpha=128,
    target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj'],
    lora_dropout=0.05,
    task_type='CAUSAL_LM',
)

# Cargar nuestro export de UNCASE
dataset = load_dataset('json', data_files='uncase_export_chatml.txt')

# Entrenar
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset['train'],
    peft_config=lora_config,
    args=SFTConfig(
        output_dir='./adapters/automotive-v1',
        num_train_epochs=3,
        per_device_train_batch_size=4,
        learning_rate=2e-4,
    ),
)
trainer.train()
trainer.save_model('./adapters/automotive-v1')
"
```

Algunas cosas a notar. Estamos usando QLoRA con rank 64 y alpha 128. La cuantización NF4 de 4 bits mantiene bajo el uso de memoria. Y todo esto corre con las dependencias que UNCASE ya instaló a través del extra `[ml]` — transformers, peft, trl, bitsandbytes, accelerate.

Para privacidad diferencial, agregarías DP-SGD vía la librería `dp-transformers` con un epsilon de 8.0. Esto acota matemáticamente cuánto puede influir cualquier conversación individual en los pesos del modelo. Lo que previene la memorización.

MLflow puede trackear esta corrida si lo tienes configurado. Cada epoch, cada valor de loss, cada norma de gradiente — todo registrado y versionado.

*[Avance rápido del entrenamiento, mostrar curva de loss]*

Entrenamiento completo. El adaptador LoRA está guardado en `./adapters/automotive-v1`. Déjame fusionarlo con el modelo base para inferencia.

```
uv run python -c "
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

model = AutoPeftModelForCausalLM.from_pretrained('./adapters/automotive-v1')
merged = model.merge_and_unload()
merged.save_pretrained('./models/automotive-llama-8b-v1')
AutoTokenizer.from_pretrained('meta-llama/Llama-3.1-8B-Instruct').save_pretrained('./models/automotive-llama-8b-v1')
"
```

Esto fusiona los pesos del LoRA en el modelo base. El resultado es un directorio de modelo único listo para deployment.

---

## INFERENCIA CON vLLM [24:00 - 27:00]

*[Pantalla: terminal]*

Y ahora el resultado final. Voy a levantar una instancia de inferencia con vLLM usando nuestro modelo fusionado.

```
python -m vllm.entrypoints.openai.api_server \
  --model ./models/automotive-llama-8b-v1 \
  --host 0.0.0.0 \
  --port 8080 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.90
```

*[Mostrar vLLM arrancando]*

vLLM está corriendo. Expone un API compatible con OpenAI en el puerto 8080. Eso significa que cualquier aplicación que hable el formato de chat completions de OpenAI puede usar este modelo tal cual. Sin cambios de código.

Voy a probarlo con una petición curl.

```
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "automotive-llama-8b-v1",
    "messages": [
      {"role": "system", "content": "Eres un asesor de ventas automotriz profesional."},
      {"role": "user", "content": "Hola, estoy buscando una SUV familiar con buen financiamiento. ¿Qué opciones tienen?"}
    ],
    "temperature": 0.7,
    "max_tokens": 512
  }'
```

*[Mostrar respuesta]*

Mira esa respuesta. El modelo saluda al cliente de manera profesional. Pregunta sobre presupuesto y tamaño de familia. Exactamente el paso de detección de necesidades de nuestro flujo de semilla. Menciona el inventario de vehículos. Ofrece prueba de manejo — siguiendo la restricción que definimos. Referencia términos de financiamiento alineados con nuestra base de conocimiento. Y lo hace todo en español natural, apropiado para el dominio.

Esto no es un LLM genérico siendo prompt-engineered. Es un modelo que ha internalizado los patrones conversacionales. El vocabulario del dominio. Las restricciones regulatorias. Y la lógica de negocio de ventas automotrices. Todo a partir de 18 conversaciones sintéticas que generamos, evaluamos y certificamos en menos de 30 minutos.

Ahora imagina esto a escala. 500 semillas a través de seis dominios. 10,000 conversaciones certificadas. Adaptadores especializados para intake médico, consultas legales, asesoría financiera, soporte de manufactura. Cada uno entrenado con privacidad diferencial. Cada conversación rastreable a su semilla. Cada métrica auditable.

---

## CIERRE [27:00 - 28:00]

Eso es el framework UNCASE de principio a fin. De semilla a inferencia en un solo pipeline.

Te resumo lo que hicimos hoy. Creamos semillas que definen planos de conversaciones con restricciones de dominio y umbrales de calidad. Subimos documentos de conocimiento para fundamentar la generación en hechos reales. Generamos 20 conversaciones sintéticas usando Claude a través del gateway de LLM con interceptor de privacidad. Evaluamos cada una contra seis métricas matemáticas — ROUGE-L, fidelidad factual, diversidad léxica, coherencia dialógica, score de privacidad y tasa de memorización. Exportamos las 18 que pasaron en formato ChatML. Hicimos fine-tuning de LLaMA 3.1 8B con QLoRA usando transformers, peft y trl. Y lo desplegamos en vLLM para inferencia en producción.

Cada paso auditable. Cada conversación certificada. Cero PII. Matemáticamente guardrailed.

El framework es open source — el enlace está en la descripción. El whitepaper técnico cubre los fundamentos formales si quieres ir más profundo en las matemáticas. Y si estás en una industria regulada y esto resuena contigo, me encantaría saber de tu caso de uso.

Gracias por ver el video. Nos vemos en el siguiente.

---

## NOTAS DE B-ROLL Y GRABACIÓN DE PANTALLA

**Grabaciones de pantalla sugeridas:**
1. Terminal: git clone + uv sync + arranque del servidor
2. Navegador: Landing page → Dashboard overview
3. Navegador: Wizard de creación de semilla (los 6 pasos, ir despacio)
4. Navegador: Knowledge Base — arrastrar y soltar archivo
5. Navegador: Generate page — seleccionar semillas, configurar, generar (mostrar progreso)
6. Navegador: Evaluate page — gráfica de radar, tarjetas de métricas, badges de pass/fail
7. Navegador: Detalle de conversación con edición inline
8. Navegador: Export page — selección de template, descarga
9. Navegador: Pipeline page panorámica
10. Terminal: Training LoRA con curva de loss
11. Terminal: Merge del modelo con peft
12. Terminal: Arranque de vLLM + prueba con curl

**Notas de ritmo:**
- Ir despacio en la creación de semillas — ahí está la diferenciación
- Dejar la gráfica de radar en pantalla — es visualmente poderosa
- La respuesta del curl es el momento "wow" — dale una pausa
- Usar jump cuts para acciones repetitivas (crear varias semillas, esperar generación)
