# El consejo es correcto. El supuesto que lo sustenta está equivocado.

Hay un ensayo circulando esta semana que describe con precisión lo que está pasando con la IA. Lo he leído dos veces. No porque me haya convencido de algo que no supiera, sino porque me incomodó de una manera muy específica: la que produce reconocer que alguien describe bien un incendio y al mismo tiempo entrega el manual equivocado de evacuación.

El autor no está equivocado. Los modelos lanzados en las primeras semanas de 2026 no son mejoras incrementales. He hecho suficientes corridas de entrenamiento — cientos de experimentos con LoRA y QLoRA, ajustando hiperparámetros sobre datasets que no puedo discutir públicamente, observando cómo un modelo transita de producir ruido a producir algo que yo no habría escrito mejor — para distinguir la diferencia entre hipérbole y una transición de fase. Esto es una transición de fase.

Pero hay una versión de esta conversación que me molesta cada vez más.

La que dice: *esto viene, viene rápido, y lo que tienes que hacer es suscribirte al tier de pago, aprender a hacer mejores prompts y dejar de ser tan especial con tu expertise.*

Ese consejo no es incorrecto para la mayoría de las personas. Es incorrecto para exactamente las personas que más necesitan una respuesta real.

---

## La médica en la sala

Esta semana salió una nota que no he podido sacudir: bajo una propuesta de reestructuración del sistema de salud rural en Estados Unidos, avatares de IA reemplazarían médicos en comunidades desatendidas. La IA haría la consulta. La IA haría el triage. La IA sería el primer — y en muchos contextos rurales, el único — punto de contacto entre un paciente y algo que se parezca al juicio clínico.

Quiero ser preciso porque la precisión importa: no creo que la IA sea categóricamente incapaz de apoyar la salud rural. Creo que desplegar un modelo genérico — entrenado sobre sistemas hospitalarios urbanos, sobre literatura médica escrita para especialistas, sobre datos que nunca han escuchado la forma particular en que un jornalero describe dolor de pecho — no es adopción de IA. Es negligencia rebautizada como eficiencia.

Esto es lo que pasa cuando tomas el consejo general — *la IA llegó, adóptala ya, deja de resistir* — y lo aplicas a dominios para los que nunca fue diseñado.

Frey y Osborne, en su estudio seminal de Oxford *The Future of Employment* (2013), identificaron que las profesiones con menor riesgo de automatización son precisamente aquellas que combinan percepción social, negociación y asistencia emocional de alta complejidad. La medicina rural de primer contacto es todas esas cosas al mismo tiempo. Un modelo entrenado en consenso estadístico no hereda esa complejidad. La simula. Y en el contexto equivocado, la diferencia entre simular y ejercer puede medirse en vidas.

---

## Las industrias que no pueden simplemente adoptarlo

Existe una categoría de organización que aparece en cada conversación sobre disrupción como ejemplo de lo que no hay que ser: *los resistentes*. Los despachos legales que dicen que no está listo. Los hospitales que dicen que es demasiado arriesgado. Los asesores financieros que dicen que el modelo no entiende el matiz. Los industriales que dicen que sus procesos son demasiado específicos.

Tratamos esa hesitación como miedo. Como ludismo moderno.

Quiero proponer algo distinto: que para un subconjunto significativo de estas organizaciones, la hesitación no es miedo a la tecnología. Es una lectura correcta de un problema que la conversación dominante se niega a nombrar directamente.

**Sus datos más valiosos — los que harían a una IA genuinamente útil — son exactamente los que tienen prohibición legal, ética y contractual de usar para entrenarla.**

Carlini et al. (2021), en *Extracting Training Data from Large Language Models*, demostraron que los modelos de lenguaje memorizan y reproducen fragmentos de sus datos de entrenamiento con tasas de extracción medibles. Eso no es un problema teórico. Es la razón por la que ningún hospital en su sano juicio debería enviar transcripciones de consultas a una API de ajuste fino en la nube, sin importar cuánto mejoren los modelos. El GDPR (Art. 9), la HIPAA, y en México la LFPDPPP (Art. 3 y 16) no son obstáculos burocráticos a sortear. Son el reconocimiento jurídico de que ciertos datos son inseparables de las personas que los generaron.

Un asesor financiero con veinte años de conversaciones de portafolio con clientes tiene la materia prima para uno de los asistentes de IA más valiosos imaginables. También tiene veinte años de información fiduciaria que no puede enviarse a ninguna plataforma externa bajo ninguna interpretación razonable de su marco regulatorio. MiFID II, CNBV, y la SEC en contexto internacional no son caprichos: son estructuras diseñadas porque el costo de equivocarse es asimétrico y cae sobre el cliente, no sobre el proveedor.

La hesitación de estas industrias no es irracionalidad. Es responsabilidad. Y tratarla como lo primero para promover lo segundo es un error que ya estamos pagando.

---

## Lo que nadie quiere decir en voz alta

Porque la honestidad también implica nombrar las fricciones que el entusiasmo tiende a omitir.

Si el 50% de los empleos de cuello blanco desaparece en cinco años — proyección de Amodei que muchos en la industria consideran conservadora — no se produce una economía de IA. Se produce un colapso deflacionario donde nadie tiene el capital para consumir lo que la IA está produciendo. Acemoglu y Restrepo (2020), en *Robots and Employment: Evidence from US Labor Markets*, documentaron ya este mecanismo: la automatización que beneficia a la concentración del capital sin transferencia de productividad a los trabajadores no genera equilibrio; genera divergencia. A mayor velocidad, mayor divergencia.

Las curvas exponenciales que se citan — capacidades duplicándose cada siete meses — están medidas en cómputo. El cómputo requiere electricidad. La electricidad requiere agua para enfriamiento. Estamos en un mundo donde los centros de datos ya compiten con el riego agrícola y el enfriamiento urbano por capacidad de red. El IMF, en su Staff Discussion Note *Gen-AI: Artificial Intelligence and the Future of Work* (2024), reconoce explícitamente que las restricciones de infraestructura física representan uno de los límites más significativos para la trayectoria de adopción proyectada. El techo es visible. No inminente, pero visible. Extrapolar exponenciales más allá de límites físicos no es análisis; es fe.

Y cuando la disrupción inducida por IA comience a amenazar materialmente la base fiscal — cuando los costos de desempleo, reentrenamiento y estabilización social superen lo que una economía concentrada en IA genera — los gobiernos van a intervenir. Los impuestos a robots, el nacionalismo de recursos, y las cuotas obligatorias de trabajo humano en industrias reguladas ya están en circulación en el Parlamento Europeo y en varios parlamentos latinoamericanos. El entorno regulatorio que hace que la adopción de IA parezca limpia hoy no va a verse igual en treinta y seis meses.

Digo esto no para argumentar que la disrupción no es real. Lo es. Lo digo porque las organizaciones a las que se les aconseja *"simplemente adóptalo"* suelen ser exactamente las que tienen suficiente complejidad operativa para entender que estas restricciones existen, y desestimar su cautela como ignorancia es injusto y contraproducente.

---

## Lo que sé desde adentro

Trabajo con ajuste fino. Específicamente con LoRA y QLoRA sobre datasets de dominio específico: conversaciones de ventas automotrices, logs de interacción con clientes, diálogos estructurados donde el objetivo es un modelo que hable el idioma particular de una operación particular en una región particular. He hecho suficientes corridas como para desarrollar intuiciones sobre qué hace bueno a un dataset, qué hace que un modelo sobreajuste, cuál es la diferencia entre un modelo que aprendió un dominio y uno que memorizó un artefacto.

También trabajo, con cuidado considerable, con datos que no puedo enviar a ningún lado.

Esta no es una observación abstracta. Es una realidad operativa cotidiana. Las conversaciones que harían mis modelos mejores son exactamente las conversaciones que tengo mayor obligación de proteger. La brecha entre *lo que puedo entrenar legalmente* y *lo que produciría el mejor modelo* no es un problema técnico. Es un problema estructural. Y los problemas estructurales requieren respuestas estructurales.

Hu et al. (2022) en *LoRA: Low-Rank Adaptation of Large Language Models* demostraron que es posible especializar un modelo masivo con adaptadores de bajo rango que representan una fracción mínima de sus parámetros — sin modificar el modelo base. Dettmers et al. (2023) en *QLoRA* extendieron esto a hardware de consumo. El costo de especialización bajó cuatro órdenes de magnitud. Lo que no bajó fue el problema de qué datos usar para hacerlo.

La respuesta que estoy desarrollando es un framework para abstraer el conocimiento de un dominio en estructuras semilla — representaciones paramétricas de patrones conversacionales que preservan la esencia factual y cualitativa de una interacción sin preservar ningún contenido sensible. De esas semillas se genera data sintética. De data sintética, se entrena. El modelo aprende el dominio desde el patrón, no desde la instancia.

El respaldo empírico existe. Li et al. (2023) demostraron con Phi-2 que un modelo de 2.7B parámetros entrenado exclusivamente con datos sintéticos de alta calidad supera en benchmarks a modelos entrenados con datos reales 25 veces más grandes. Johnson et al. (2016) demostraron con MIMIC-III Synthetic que registros clínicos pueden ser generados con suficiente fidelidad para investigación médica sin exponer un solo paciente real. El precedente existe. El método existe. Lo que no existe todavía es una arquitectura sistemática y auditada para aplicarlo al problema específico de organizaciones con datos sensibles y conocimiento de dominio que no pueden compartir.

A eso le llamo UNCASE — Unbiased Neutral Convention for Agnostic Seed Engineering Privacy-Sensitive Synthetic Asset Design Architecture. El nombre es largo. El problema que resuelve no es pequeño.

---

## La crisis real, enunciada con precisión

La crisis no es que la IA llegue rápido. Llega.

La crisis no es que algunas industrias resistan. Parte de esa resistencia es correcta.

La crisis es esta: las industrias con más que ganar de la especialización en IA — y más que perder si lo hacen mal — están recibiendo consejos diseñados para un problema diferente. Se les dice que adopten herramientas construidas sobre los datos de otros, desplegadas en infraestructura que no controlan, produciendo outputs que no pueden auditar completamente, para decisiones que implican responsabilidad que sus proveedores no comparten.

Y en la brecha entre *lo que la IA puede hacer* y *cómo hacerlo sin comprometer lo que te hace quien eres*, hay un avatar de IA sentado en una clínica rural, generando un diagnóstico desde un conjunto de entrenamiento que nunca ha escuchado la manera en que un paciente en Oaxaca describe falta de aire.

Esa brecha no es un problema tecnológico.

Es un problema de infraestructura.

Y los problemas de infraestructura requieren frameworks, no suscripciones.

---

*Estoy desarrollando UNCASE como respuesta estructural a este problema. Si trabajas en salud, derecho, finanzas, manufactura o cualquier sector donde tu conocimiento más valioso es también tu dato más protegido, me interesa escucharte.*

*Las conversaciones difíciles son las que valen la pena tener.*

