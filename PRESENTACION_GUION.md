# Guion de defensa — HUELLAS

**Defensa:** 13 de octubre · **Duración total:** 10:00 exactos · **Formato:** diapositivas de apoyo sincronizadas con demo en vivo. No es una exposición tradicional del MVP: los primeros cinco minutos combinan demo y decisión técnica; los cinco restantes defienden cómo dirigí al agente de IA.

## Preparación antes de iniciar el cronómetro

- Abrir `https://huellas.streamlit.app`, comprobar que está activa y dejar lista la página **Búsqueda de coincidencias**.
- Tener a mano `data/seed/images/lost_001.jpg` para subirla en la demo, y conocer los campos de prueba: gato, naranja, pequeño, sin collar, rayas y cola anillada; zona Centro/Plaza del Arenal.
- La búsqueda live con esta configuración obtuvo en la simulación Cloud **found_011 top-1 alrededor del 83%**. En la Fase 0, el par seed-a-seed `lost_001 → found_011` midió **84,5%**. Son escenarios distintos: durante la defensa se lee el porcentaje real que muestre la tarjeta, sin forzarlo al valor del ensayo.
- La app no muestra un cronómetro de inferencia. Medir con un cronómetro auxiliar el tiempo desde pulsar **Buscar coincidencias** hasta que aparezca el ranking. En el speech sustituir `[X]` por el valor observado y llamarlo latencia de extremo a extremo, no latencia aislada del modelo.
- La app presenta resultados en tarjetas ordenadas y barras de señales, no en una tabla HTML. La diapositiva 3 lleva una tabla-resumen de referencia; en la app se enseñan la tarjeta y el desglose reales.

---

# PARTE 1 — DEMO EN VIVO Y DECISIÓN TÉCNICA (00:00–05:00)

## Diapositiva 1 — HUELLAS en vivo (00:00–00:35)

**Diapositiva de apoyo:** HUELLAS + flujo sencillo «foto y descripción → ranking → mapa» y URL de la demo.

**Acción en pantalla / demo:** abrir `huellas.streamlit.app`; mostrar Inicio y seleccionar en el sidebar **Búsqueda de coincidencias**. Confirmar que se ve el título del análisis.

**Speech verbal exacto:**

> «Buenos días. Voy a demostrar HUELLAS desde la experiencia de quien ha perdido una mascota: aporta una foto, describe sus rasgos y consulta avisos compatibles por imagen, texto, fecha y zona. El sistema ordena posibles coincidencias para ayudar a decidir dónde mirar. No identifica animales de forma concluyente: la revisión final corresponde a las personas, que deben verificar cada posible resultado.»

## Diapositiva 2 — Preparar una búsqueda reproducible (00:35–01:25)

**Diapositiva de apoyo:** captura anotada del formulario: canal, foto, zona y descripción.

**Acción en pantalla / demo:**
1. En **Canal**, elegir **Entre avistamientos (perdí mi mascota)**: el sistema buscará avisos `found` frente al gato perdido.
2. En **Sube una foto de tu mascota**, cargar `data/seed/images/lost_001.jpg`.
3. Completar: **Gato**, color **naranja**, tamaño **pequeño**, sin collar, marcas **rayas, cola anillada** y descripción: «Gatito naranja atigrado perdido cerca de la plaza del Arenal. Tiene rayas marcadas y la cola anillada. Muy sociable».
4. Dejar la ubicación en Centro de Jerez (valor inicial reproducible); si está cargado el mapa, situarla cerca de Plaza del Arenal. Mostrar brevemente el mapa de zona: pines azules de perdidos y verdes de avistamientos.

**Speech verbal exacto:**

> «Uso un caso controlado para que podamos interpretar el resultado. Elijo buscar entre avistamientos, subo la foto de `lost_001` y describo gato naranja, pequeño, sin collar, con rayas y cola anillada. Sitúo la búsqueda en el centro de Jerez, cerca de Plaza del Arenal. El seed y la fecha de referencia de demo hacen que este recorrido se pueda repetir.»

## Diapositiva 3 — Inferencia, velocidad y ranking (01:25–03:15)

**Diapositiva de apoyo:** tabla-resumen de ensayo:

| Escenario ONNX | Top-1 | Score | Visual | Texto | Tiempo | Geo |
|---|---|---:|---:|---:|---:|---:|
| Query live reproducible → `found_011` | `found_011` | ≈83% | 0,77 | 0,89 | 0,83 | 0,99 |
| Par seed-a-seed medido en Fase 0 | `found_011` | 84,5% | — | — | — | — |

La primera fila es una referencia reproducible; la app en vivo es la fuente del valor definitivo de la sesión.

**Acción en pantalla / demo:** desplazarse al botón **Buscar coincidencias**. Iniciar el cronómetro auxiliar al pulsarlo y detenerlo cuando aparezcan resultados. Mostrar la animación de análisis, los contadores, la tarjeta destacada `found_011` y sus cuatro barras. Leer el porcentaje real de la tarjeta; no presentar la tabla de apoyo como si fuera una tabla HTML de la app.

**Speech verbal exacto:**

> «Pulso Buscar. Mientras se calcula el ranking, el cronómetro mide el recorrido completo desde el clic hasta los resultados. En este ensayo ha tardado **[X] segundos**; es tiempo de extremo a extremo, no solo del modelo. La tarjeta superior es `found_011`, con **[porcentaje mostrado]** y etiqueta de posible coincidencia destacada. En el ensayo reproducible del formulario llegó al top-1 alrededor del 83%; el 84,5% de la tabla corresponde a la medición Fase 0 del par seed-a-seed.»

## Diapositiva 4 — Folium y decisión técnica clave (03:15–05:00)

**Diapositiva de apoyo:** diagrama híbrido `Local: CLIP 512-d / Cloud: MobileNetV3 ONNX 576-d` y límites: 1 GB RAM, runtime ONNX ~10 MB RAM, mismo espacio de comparación.

**Acción en pantalla / demo:** abrir el mapa de candidatos Folium; señalar el marcador del caso consultado y el del candidato encontrado. Si hace falta, volver brevemente al mapa de zona para mostrar los pines azules y verdes. Luego señalar en la diapositiva el flujo CLIP local / ONNX Cloud.

**Speech verbal exacto:**

> «La decisión técnica clave fue separar la visión por entorno. CLIP con PyTorch ofrece el vector canónico de 512 dimensiones, pero cargar ese pipeline pesado puede superar el límite de aproximadamente 1 GB de RAM de Streamlit Cloud y provocar un OOM. Allí usamos MobileNetV3-Small exportado a ONNX: 576 dimensiones y alrededor de 10 MB de RAM. En la Fase 0 dio 84,5% en el par insignia y no produjo destacadas cruzadas en la matriz probada. Local conserva CLIP; cada búsqueda compara query y candidatos en el mismo espacio.»

---

# PARTE 2 — DEFENSA DE DIRECCIÓN DEL AGENTE DE IA (05:00–10:00)

## Diapositiva 5 — El rol del agente y el del responsable humano (05:00–06:15)

**Diapositiva de apoyo:** esquema de roles: **OpenCode** como entorno; agente IA como **arquitecto + desarrollador + auditor**; alumno como responsable de producto y aceptación.

**Acción en pantalla / demo:** mostrar un fragmento de `PROMPT-LOG.md` o una solicitud de trabajo estructurada; señalar objetivo, alcance y criterio de aceptación.

**Speech verbal exacto:**

> «No traté al agente como un generador autónomo. En OpenCode le asigné tres funciones: arquitecto para analizar alternativas, desarrollador para proponer cambios pequeños y auditor para buscar fallos y comprobar requisitos. Los modelos de IA, entre ellos Gemini y GPT-6, trabajaban sobre tareas delimitadas. Mi plantilla de prompt definía objetivo, contexto, archivos permitidos, restricciones, resultado esperado y verificación. Si faltaba información, prefería una pregunta antes que una suposición. También pedía separar hechos comprobados, supuestos y decisiones pendientes, y citar la prueba que validaba cada cambio. Si una propuesta afectaba a privacidad, alcance o a otra parte del sistema, el agente debía exponer alternativas y riesgos en vez de ejecutarla por su cuenta. En la práctica, OpenCode aportaba el contexto del repositorio; el modelo resolvía una tarea concreta y yo decidía si el diff entraba. Así evitaba delegar el criterio. Yo aportaba el contexto del producto, elegía prioridades y aceptaba o rechazaba cada resultado. La autoría de las decisiones críticas siempre fue humana.»

## Diapositiva 6 — Prompts estructurados y SDD (06:15–07:30)

**Diapositiva de apoyo:** ciclo `requisito → prompt con restricciones → cambio pequeño → test → revisión humana`; fragmentos de `requirements.md` y `architecture.md`.

**Acción en pantalla / demo:** enseñar una sección de requisitos y el commit asociado; señalar cómo los criterios de aceptación conectan la intención con el código.

**Speech verbal exacto:**

> «Trabajé con Spec-Driven Development. Antes de pedir código, concretaba el objetivo, los archivos afectados, lo que debía mantenerse intacto y cómo verificarlo. Después dividía el trabajo en cambios pequeños y pedía tests para el comportamiento relevante. Por ejemplo, la regla de persistencia del seed se convirtió en generador determinista, versión de seed y pruebas de carga desde una base vacía. También mantuve las especificaciones como contrato: una modificación no se daba por válida solo porque la interfaz pareciera correcta. Debía ser coherente con los requisitos, tener trazabilidad y superar una verificación reproducible. Cuando aparecía una ambigüedad, pedía comparar alternativas y probar una pequeña antes de ampliar el cambio. Al cerrar cada iteración comparaba el diff con los criterios y actualizaba README, arquitectura o bitácora si cambiaba el estado real. Así el prompt no sustituía la especificación: la ejecutaba y dejaba evidencia revisable.»

## Diapositiva 7 — Cómo detecté y corregí errores de IA (07:30–08:45)

**Diapositiva de apoyo:** evidencia de tests y tres casos: error de API/código, mezcla de espacios visuales y regresión de persistencia; cifra de 121 casos.

**Acción en pantalla / demo:** mostrar el resultado de `pytest` y, si se dispone de terminal preparada, `demo_check.py`. Aclarar el entorno de ejecución: 121/121 con PyTorch; instalación base, 119 pasadas y dos pruebas CLIP omitidas por requerir el extra opcional.

**Speech verbal exacto:**

> «No di por válida una respuesta porque sonara convincente. La contrasté con ejecución y pruebas. Detectamos, entre otros, un vector entregado donde se esperaba una puntuación, una comparación de embeddings en espacios incompatibles y cambios de seed que podían perderse al dormir Cloud. Añadimos regresiones para bloquear esos fallos. En la Fase 0 de visión medimos query, par insignia y cruces entre especies antes de integrar ONNX; también descartamos HSV porque daba falsas destacadas. Los tests pequeños comprueban unidades y regresiones, mientras los scripts E2E comprueban el ranking real y el smoke ejecuta las nueve páginas. Al final, cada error reproducido debía quedar protegido por un test para que no regresara en otra iteración. Hay 121 casos: con PyTorch instalado pasan 121 de 121; con la instalación ligera se omiten dos que requieren CLIP. La evidencia, no la seguridad retórica del modelo, decide si acepto un cambio.»

## Diapositiva 8 — Decisiones humanas y cierre (08:45–10:00)

**Diapositiva de apoyo:** matriz «decisión / evidencia / responsable» y tres siguientes pasos: recursos híbridos, routing V2, bot Telegram.

**Acción en pantalla / demo:** señalar decisiones firmadas por requisitos: no afirmar identidad, pesos 0,55/0,25/0,10/0,10, cambiar a ONNX solo tras medirlo, mantener la experiencia móvil sin modificaciones no autorizadas. Cerrar con el roadmap V2.

**Speech verbal exacto:**

> «Yo conservé el control de las decisiones de producto: el sistema solo comunica posibles coincidencias, los pesos se mantienen explícitos y la arquitectura ONNX se integró después de medirla frente a CLIP y revisar falsos positivos. Cuando otra variante mejoraba el recall pero confundía perros y gatos, no la acepté. También decidí congelar la fecha de referencia solo para las búsquedas contra el seed estático; publicar sigue guardando la fecha real. Delimité lo que quedaba fuera del MVP y qué cambios móviles no debían hacerse sin autorización. Esta separación permitió experimentar sin comprometer la demo y conservar lo medible y explicable. Para V2 propongo routing multipágina nativo y un bot bidireccional: publicar con foto y ubicación desde la calle y enviar alertas push al superar el 80%. La IA aceleró el trabajo, pero el juicio, la verificación y la responsabilidad final fueron humanas. Muchas gracias.»

---

## Control del tiempo

- Parte 1: 00:00–05:00 (5:00 exactos).
- Parte 2: 05:00–10:00 (5:00 exactos). Mantén el speech continuo mientras señalas los artefactos; las acciones no son pausas de silencio.
- Duración total: 10:00. Ensayar la búsqueda antes de la defensa y rellenar `[X]` con el tiempo real medido en Cloud. Si la red tarda, reducir la explicación del mapa; no omitir la decisión técnica ni la defensa del proceso.
