# Guion de defensa oral — HUELLAS

**Duración total:** 5:00 · **Fecha prevista:** 13 de octubre · **Estructura:** 7 diapositivas.  
Cada texto de locución está pensado para ocupar aproximadamente 30–45 segundos. En la diapositiva 6 se reserva tiempo adicional para la demostración.

## Diapositiva 1 — El problema (00:00–00:35)

**Visual sugerido:** título HUELLAS; una imagen esquemática de avisos dispersos que convergen en una ficha de mascota.

**Speech:**  
«Buenas tardes. Presento HUELLAS, mi proyecto final para el curso de IA Generativa y Vibe Coding. El problema es sencillo y cotidiano: cuando una mascota se pierde, los avisos quedan repartidos entre redes, carteles y protectoras. Encontrar el aviso complementario depende de que alguien lo vea. El objetivo es ayudar a cruzar esa información localmente y priorizar posibles candidatos, sin sustituir la búsqueda humana.»

## Diapositiva 2 — MVP y solución (00:35–01:10)

**Visual sugerido:** captura de la página Inicio y tarjeta de una posible coincidencia, con imagen, porcentaje y señales.

**Speech:**  
«El MVP permite publicar avisos de pérdida o hallazgo y buscar casos compatibles por foto, descripción, fecha y zona. Devuelve un ranking explicable, un mapa y un detalle de las señales que han contribuido. El corpus de demostración contiene veinte avisos de Jerez. Una regla importante es que HUELLAS nunca afirma que dos fotos sean el mismo animal: presenta posibles coincidencias para que la persona responsable compruebe el caso y contacte.»

## Diapositiva 3 — Arquitectura técnica (01:10–01:50)

**Visual sugerido:** diagrama simple: Streamlit → Ingestor → Vision → Matcher + Geo → Notifier; debajo, SQLite y RAG.

**Speech:**  
«La interfaz está construida con Streamlit y la persistencia local con SQLite. Al procesar un aviso, el Ingestor normaliza sus campos; Vision obtiene atributos y una representación de la imagen; Matcher calcula el ranking; Geo incorpora la distancia; y Notifier registra las alertas. El RAG recupera candidatos con señales textuales. La arquitectura es deliberadamente pequeña: cinco agentes especializados, funciones de persistencia y scripts independientes de carga y evaluación. Así puedo probar cada parte y explicar de dónde sale un resultado.»

## Diapositiva 4 — Decisión técnica clave (01:50–02:30)

**Visual sugerido:** gráfico circular o barras con pesos 55/25/10/10 y tres umbrales: 65%, 80%, 95% visual.

**Speech:**  
«Una decisión clave fue dar mayor peso a la imagen, sin depender de un modelo pesado en todos los despliegues. El score combina 55% visual, 25% texto, 10% temporal y 10% geográfico; el texto mezcla atributos estructurados y similitud semántica. Desde 65% se lista un candidato y desde 80% se genera alerta; una similitud visual de 95% también activa aviso. En local puede usarse CLIP; en Cloud hay un fallback de histograma, más ligero pero menos discriminativo. Esa limitación está declarada.»

## Diapositiva 5 — Dirección humana de la IA (02:30–03:05)

**Visual sugerido:** fragmento de `requirements.md` junto a un test y un commit trazable `[REQ-…]`.

**Speech:**  
«La IA no decidió el producto por mí. Yo fijé el alcance, las reglas de privacidad y el criterio de no afirmar identidades; luego utilicé especificaciones SDD como contrato para guiar las tareas. Supervisé cada iteración con pruebas, ejecución de la demo y revisión de resultados. Cuando una propuesta móvil empeoró la experiencia, pedí revertirla. La IA aceleró implementación y diagnóstico, pero la aceptación, las prioridades y las decisiones finales siguieron siendo humanas.»

## Diapositiva 6 — Demostración en vivo (03:05–04:20)

**Visual sugerido:** captura del formulario Buscar; mantener abierta en otra pestaña la demo `https://huellas.streamlit.app`.

**Speech, 03:05–03:40:**  
«Voy a mostrar el flujo principal con una búsqueda de una mascota perdida. Para que la demostración sea ágil, dejo preparada la página Buscar con una foto del seed y los campos de especie, color, descripción y zona. Al lanzar la consulta, veremos los avisos encontrados, el porcentaje y el desglose de señales. Fíjense en que el resultado es una recomendación revisable, no una identificación automática.»

**Momento exacto de inicio de la demo: 03:40.**

**Acciones en vivo, 03:40–04:20 (40 segundos):**
1. Mostrar la pestaña de `huellas.streamlit.app` ya cargada en **Buscar**.
2. Usar el formulario preparado con una consulta tipo `lost_001` (foto `data/seed/images/gato 1.jpg`; canal «Entre avistamientos»; gato, color naranja y descripción correspondiente).
3. Pulsar **Buscar coincidencias**; señalar el candidato mejor clasificado y su desglose visual/textual/temporal/geográfico.
4. Recordar que `demo_check.py` valida en E2E que `found_011` sea top-1 con 80.8% en el escenario de prueba. El porcentaje de la interacción en vivo puede variar con fecha y zona.

**Preparación y contingencia:** abrir la demo antes de empezar, precargar la imagen y los campos antes de la diapositiva 6, y tener una captura del resultado por si falla la red o el despliegue.

## Diapositiva 7 — Validación y cierre (04:20–05:00)

**Visual sugerido:** cifras 92 tests, 9 páginas smoke, enlace al repositorio y demo; debajo, dos limitaciones conocidas.

**Speech:**  
«El proyecto termina con 92 pruebas automatizadas, evaluación del matching, una comprobación E2E y un smoke test de las nueve páginas. También quedan documentados límites importantes: los datos de Cloud son efímeros y el fallback visual es menos preciso que CLIP. Mi conclusión es que la IA resulta útil cuando se dirige con requisitos claros y se contrasta con evidencia. HUELLAS no sustituye a las personas: les ayuda a priorizar dónde mirar. Muchas gracias.»

**Nota de cronometraje:** los intervalos suman exactamente cinco minutos; la diapositiva 6 reserva 35 segundos de locución y 40 segundos de demostración.
