# MascotasLost&Found — requirements.md

> Metodología: Spec-Driven Development (SDD).
> Este documento es la fuente de verdad del MVP. Todo commit debe referenciar una sección (p.ej. `REQ-03`, `CU-02`).
> Estado: v1.0 — decisiones cerradas 23/09/2026 (13/13). Stack: Streamlit + Python + SQLite, 100% local. Sin código aún.

## 1. Objetivo (REQ-01)

Construir un MVP funcional que centralice avisos de mascotas perdidas (`lost`) y encontradas (`found`) en un corpus propio y controlado, y sugiera **posibles coincidencias** a partir de imagen, descripción textual, ubicación y fecha.

El valor no es identificar con certeza, sino **priorizar candidatos** para que el dueño revise visualmente y contacte.

Principio transversal: **el sistema nunca afirma "es el mismo animal"**. Siempre muestra "posible coincidencia" con porcentaje y señales que la sustentan. El aviso legal vive en un único apartado del sidebar ("Este análisis no promete una coincidencia inequívoca respecto al animal buscado. Una imagen no permite confirmar la identidad, verifique en persona.").

## 2. Problema que resuelve (REQ-02)

Cuando una mascota se pierde, los avisos quedan dispersos en redes sociales y protectoras sin forma de cruzarlos automáticamente. El sistema centraliza avisos y propone cruces lost ↔ found.

## 3. Alcance del MVP — qué SÍ hace (REQ-03)

- REQ-03.1: Acepta cualquier animal doméstico (`dog | cat | other`), no solo perros/gatos.
- REQ-03.2: Permite registrar avisos `lost` y `found` con foto + texto libre + ubicación (lat/lng) + fechas.
- REQ-03.3: Normaliza todo aviso al esquema **Entidad Aviso** (ver §6).
- REQ-03.4: Ejecuta pipeline de 5 agentes: Ingestor → Vision Analyst → Matcher (+ Geo) → Notifier (ver §7).
- REQ-03.5: Calcula `score_total` con fórmula y pesos cerrados (ver §8).
- REQ-03.6: Muestra ranking de posibles coincidencias con desglose por señales y aplica umbrales §9.
- REQ-03.7: Visualiza candidatos en mapa interactivo por proximidad geográfica.
- REQ-03.8: Funciona con corpus demo propio de 15-20 avisos cargados manualmente (seed data).

## 4. Alcance — qué NO hace (límites explícitos, REQ-04)

- REQ-04.1: **NO scraping en vivo** de Facebook, Instagram, protectoras ni ninguna fuente externa. Queda fuera del MVP como ampliación futura documentable en memoria/slides, no a construir.
- REQ-04.2: **NO afirma identidad**: prohibido el literal "es el mismo animal" en UI, logs o notificaciones.
- REQ-04.3: NO autenticación multi-usuario ni roles. Excepción v1.1: UN único administrador con contraseña para moderación básica (ver REQ-11).
- REQ-04.4: NO app móvil nativa. Solo web MVP ejecutable en local + despliegue simple.
- REQ-04.5: NO Telegram/webhook real. Notifier MVP = panel/tabla en Streamlit + log (decisión 9, 23/09/2026).
- REQ-04.6: NO genera cartel PDF "SE BUSCA" en MVP (ampliación propuesta fuera de alcance salvo decisión explícita posterior).

## 5. Casos de uso principales

### CU-01 — Registrar aviso `lost`
Actor: dueño. Flujo: sube foto + descripción + ubicación + fechas + contacto obligatorio (al menos un dato: móvil, correo o red social; sin contacto no se publica) → Ingestor normaliza → Vision Analyst extrae atributos y embedding → se persiste → Matcher lo compara contra corpus `found` activos → se muestran coincidencias >=65% y se notifica si >=80%. Campos obligatorios marcados con `*` en el formulario.

### CU-02 — Registrar aviso `found`
Actor: persona que encuentra / protectora. Flujo simétrico a CU-01 (contacto también obligatorio, marcado con `*`), comparando contra corpus `lost` activos.

### CU-03 — Búsqueda de coincidencias (sin registrar)
Actor: dueño o quien avista. Flujo: elige canal (avistamientos si perdió, perdidos si encontró: quien busca es el caso inverso) + foto + zona + descripción → Matcher cruza SOLO contra ese canal → ranking ≥65% con desglose. Campos obligatorios marcados con `*` (canal, foto, animal, tamaño, color principal, descripción). Transitoria: no persiste ni escribe alertas. Haya coincidencia o no, el botón PUBLICAR AVISO lleva a CU-01/CU-02 con foto, zona, descriptivos y tipo ya precargados (el tipo se infiere del canal). Las alertas persistentes nacen del cruce al publicar.

### CU-04 — Revisar detalle de posible coincidencia
Actor: dueño. Ve lado a lado fotos, distancia km, diferencia días, atributos coincidentes/divergentes, y aviso legal de no-identidad. Decide contactar fuera del sistema.

### CU-05 — Resolver / expirar aviso / reencuentro
Actor: dueño. Marca aviso como `resolved` mediante botón manual "Marcar como resuelto". Función `expire_old()` marca `expired` a los avisos con más de 30 días (invocable bajo demanda, sin cron). Los no-`active` no entran en matching.
Actor: cualquiera que presencie el reencuentro. En VOLVIÓ A CASA selecciona el perdido y/o avistamiento que se resuelve, sube fotos del reencuentro y lo notifica: queda pendiente y el administrador lo valida (resuelve los avisos y cierra el caso visible) o lo rechaza (posible vandalismo: los avisos siguen activos). Toda decisión queda en `data/admin.log`.

Fuera de MVP: CU-07 ingesta automática externa, CU-08 chat asistente, CU-09 impresión cartel.

### CU-06 — Moderar avisos (administrador)
Actor: administrador autenticado (contraseña). Flujo: entra en el apartado Administración del sidebar → filtra por tipo/texto → elimina duplicados o vandalismo (con confirmación) o marca resueltos → la acción queda en `data/admin.log`.

## 6. Esquema de datos — Entidad Aviso (REQ-05)

Todo aviso persiste con esta forma (decisión cerrada, no modificar sin nueva spec):

```json
{
  "id": "uuid",
  "type": "lost | found",
  "animal": "dog | cat | other",
  "breed_guess": "string (opcional, generado por el agente de visión)",
  "color_primary": "string",
  "color_secondary": "string (opcional)",
  "markings": ["string"],
  "size": "small | medium | large",
  "has_collar": "boolean",
  "collar_description": "string (opcional)",
  "description_text": "string (texto libre del usuario)",
  "location": { "lat": "number", "lng": "number", "address_text": "string opcional" },
  "date_reported": "ISO 8601 datetime",
  "date_last_seen": "ISO 8601 datetime (opcional)",
  "image_url": "string",
  "image_embedding": "vector (generado por el agente de visión, no por el usuario)",
  "contact_info": "string (opcional)",
  "status": "active | resolved | expired"
}
```

Reglas derivadas:
- REQ-05.1: `id` UUID v4 generado en ingesta.
- REQ-05.2: `breed_guess` e `image_embedding` solo los escribe Vision Analyst, nunca el usuario. `image_embedding`: CLIP `openai/clip-vit-base-patch32`, 512 dimensiones.
- REQ-05.3: Solo `status=active` participa en Matcher.
- REQ-05.4: El cruce es siempre `lost ↔ found`, nunca `lost ↔ lost` ni `found ↔ found`.
- REQ-05.5: `image_url`: ruta local relativa `data/seed/images/<fichero>`.
- REQ-05.6: Conflicto Ingestor vs Vision (decisión 10): manda Vision Analyst para `color_primary` y resto de atributos visuales; `description_text` conserva intacto el texto original del usuario.
- REQ-05.7: Si `animal="other"`: obligatorios `color_primary`, `size`, `description_text`; opcionales `markings`, `has_collar`/`collar_description`; `breed_guess` se omite (NULL).
- REQ-05.8: `location`: lat/lng capturados por mapa clicable Leaflet; ciudad seed fija: Jerez de la Frontera.
- REQ-05.9: Idioma UI y textos: solo español.

## 7. Agentes y responsabilidades (REQ-06, decisión cerrada)

1. **Ingestor**: recibe foto + texto + ubicación + fecha de un aviso nuevo y lo normaliza al esquema §6. No calcula scores. Preserva `description_text` intacto.
2. **Vision Analyst**: procesa la imagen y extrae especie, raza aproximada, color, manchas, collar, tamaño, y genera el embedding visual CLIP 512-dim. Tiene precedencia sobre atributos visuales (decisión 10).
3. **Matcher**: compara un aviso contra el resto del corpus y calcula score (ver §8).
4. **Geo**: calcula distancia haversine y aplica `max(0, 1 - distancia_km / 15)`, radio_máximo fijo 15 km.
5. **Notifier**: si `score >= 80%`, registra en tabla `notifications` + log y muestra destacada en panel Streamlit. Sin Telegram real.

> Conflicto Ingestor vs Vision resuelto 23/09/2026: manda Vision para `color_primary`; texto usuario intacto en `description_text`.

## 8. Motor de matching — fórmula y pesos (REQ-07)

```
score_total = (0.40 × similitud_visual)
            + (0.30 × similitud_texto)
            + (0.20 × proximidad_temporal)
            + (0.10 × proximidad_geográfica)
```

v1.2 (24/09/2026, decisión del alumno S51): geo 0.30→0.10, texto 0.20→0.30,
temporal 0.10→0.20. Motivo: la ubicación lejana penalizaba demasiado.

- `similitud_visual`: similitud coseno entre embeddings CLIP `openai/clip-vit-base-patch32` 512-dim (0-1). Sin torch (Cloud), query y candidatos se comparan en histograma de color: lo que importa es que ambos lados usen el MISMO espacio (S49; mezclarlos da ~0.09 y vacía el ranking).
- `proximidad_geográfica`: max(0, 1 - distancia_km / 15), radio_máximo fijo = 15 km.
- `similitud_texto`: 0.70 × estructurado + 0.30 × semántico. Estructurado: coincidencia campo a campo de `color_primary`, `markings`, `has_collar`, `size`. Semántico: coseno con `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` sobre `description_text`.
- `proximidad_temporal`: max(0, 1 - dias_diferencia / 30), ventana 30 días. Fecha usada: `date_last_seen` si existe, si no `date_reported`.

Restricciones: los 4 pesos suman 1.0. No se reponderan sin nueva spec.

## 9. Umbrales de notificación (REQ-08, `>=`)

v1.2 (24/09/2026, decisión del alumno S51): alerta 85%→80%.

- Score >= 80%: notificación automática (panel + log) + se muestra como "posible coincidencia" destacada.
- Score 65-79.99%: aparece en el listado, sin notificación.
- Score < 65%: no se muestra como coincidencia, pero queda indexado.

## 10. Requisitos no funcionales (REQ-09)

- REQ-09.1: Ejecución local en 1 comando documentado en README para que el profesor evalúe sin nube.
- REQ-09.2: Despliegue simple opcional (Streamlit Cloud / similar) con enlace en README.
- REQ-09.3: SQLite / ficheros locales para seed; sin servicios externos obligatorios.
- REQ-09.4: Explicabilidad: todo match muestra sus 4 sub-scores.
- REQ-09.5: Privacidad mínima: `contact_info` obligatorio al publicar (al menos un dato, v1.4 24/09/2026), visible solo en detalle.
- REQ-09.6: Trazabilidad SDD: commit → sección de spec.

## 11. Criterios de éxito del MVP (REQ-10)

- ÉXITO-01: Con seed de 15-20 avisos, un `lost` de prueba recupera al menos 1 `found` relevante >65% con desglose correcto.
- ÉXITO-02: Ninguna pantalla/log/notificación contiene "es el mismo animal".
- ÉXITO-03: Matcher respeta fórmula/pesos/umbrales auditables (test con vectores fijos).
- ÉXITO-04: Profesor ejecuta en local siguiendo README en <10 min sin claves obligatorias.
- ÉXITO-05: Repo GitHub con historial progresivo + PROMPT-LOG.md + sesiones Engram + informe reflexión.
- ÉXITO-06: Demo 5 min: registro → ranking → mapa → detalle explicable.

## 12. Administración (REQ-11, añadido v1.1)

- REQ-11.1: Un único administrador; acceso por contraseña (Secrets `ADMIN_PASSWORD` en Cloud, variable `HUELLAS_ADMIN_PASSWORD` o defecto documentado `huellas123` en local).
- REQ-11.2: Puede listar con filtros, eliminar (borra aviso + notificaciones ligadas + foto subida, nunca seed) y resolver.
- REQ-11.3: Toda acción se registra en `data/admin.log` con fecha.
- REQ-11.4: El admin puede editar cualquier campo del aviso (con validación del esquema y log de campos cambiados).
- REQ-11.5: El admin revisa los reencuentros pendientes (fotos + avisos): validar resuelve los avisos y publica el cierre; rechazar los deja activos.

## 14. Navegación e Inicio (REQ-UI-01..06, añadido v1.2 24/09/2026)

No toca matching, agentes, RAG ni BD (solo UI en `app.py` + nuevo `ui_home.py` puro).

- REQ-UI-01 — Pantalla Inicio por defecto: al abrir la app `session_state.page="inicio"`.
  Muestra hero + carrusel en movimiento + 3 contadores. El logo y el header quedan intactos.
  El hero no repite la ciudad (Jerez ya está en el header).
- REQ-UI-02 — Barra lateral, 6 elementos en este orden (v1.6 24/09/2026):
  `INICIO` (botón rojo grande, icono casa Material, activo con barra blanca + fondo oscuro),
  `FUNCIONALIDADES` (plegable rojo, icono apps, único abierto por defecto: agrupa
  Publicar aviso + Búsqueda de coincidencias como botones secundarios negros
  tabulados a la derecha),
  `PUNTUALIZACIONES WEB` (plegable rojo, icono aviso: despliega Cómo puntúa + Aviso legal,
  ambos expanders cerrados hasta clicar, contenidos tabulados),
  `DATOS DEMO` (plegable rojo, icono stats: seed + expirar como secundarios negros tabulados),
  `MÁS` (plegable rojo con `+`: despliega Protectoras y Tiempo en Jerez, también
  secundarios negros tabulados, con sus iconos),
  `ADMINISTRACIÓN` (plegable rojo, icono llave: panel tabulado con login + moderación +
  reencuentros).
  Sin Perdidos/Avistamientos/Volvió a casa en el sidebar (se llega vía Inicio).
  Plegables = botón rojo que alterna `session_state` (al abrir la app, solo
  FUNCIONALIDADES desplegada; la navegación reabre FUNCIONALIDADES +
  `initial_sidebar_state` en expanded). La auto-apertura del PANEL al cambiar de
  pestaña se descartó (v1.11): Streamlit no expone API y los trucos (iframe de
  componente o `st.html` con JS) quedan bloqueados por el sanitizador.
  Botones a todo el ancho (`block-container` con `padding` lateral
  mínimo). Sin caption de conteo bajo "Animales perdidos activos".
  Cambiar de sección es un rerun Streamlit: conserva `session_state` (no pierde filtros).
- REQ-UI-03 — CTAs en el hero de Inicio y agrupados en FUNCIONALIDADES del sidebar
  (v1.4 24/09/2026): `Publicar aviso` y `Búsqueda de coincidencias`, ambos rojo sólido
  `#E30613` idénticos y grandes (visibles en móvil).
  `Publicar` → `page="publicar"`; `Búsqueda` → `page="buscar"`.
- REQ-UI-04 — Estilo botones (solo CSS, sin librerías): esquinas 6px,
  `transition: transform .2s, background .2s`, hover con `translateX(3px)` + fondo
  `rgba(227,6,19,.85)`, sin aspecto de blog. Hero: los 2 CTAs en rojo sólido idéntico
  con pulso suave (anillo `::after` que se expande `scale 1 → 1.12,1.4` y se
  desvanece, `2.2s ease-out infinite`).
  Sidebar: botones principales rojos grandes (`#E30613`, texto `#FFFFFF`, `padding .95rem 1rem`,
  `1.08rem` negrita, juntos con `gap 6px`) y secundarios negros tabulados (`#23201B`,
  `margin-left 1.25rem`), con iconos Material, sin emojis, a todo el ancho
  (`block-container` con `padding` lateral mínimo). Sin estirado flex (v1.8: se probó
  en v1.7 y empeoraba la estética). Bocadillos `help=` + CSS sobre
  `[data-testid="stTooltipContent"]`: sin captura de puntero y auto-ocultado a los
  4s aunque Streamlit los deje pillados (v1.6).
- REQ-UI-05 — Hero Inicio: titular `ESTOS PELUDOS QUIEREN VOLVER A CASA` en 2 líneas con
  `fade-up` (una vez, `both .7s`, segunda línea con `delay .25s`); palabra `CASA` en rojo
  `#E30613` con subrayado que se dibuja (`::after` animado); corazón SVG con latido suave
  (`scale 1 → 1.25`, `1.4s infinite`); subtítulo `Mira quién te está esperando…`.
- REQ-UI-06 — Carrusel infinito + contadores con navegación interna (v1.4 24/09/2026):
  fotos de avisos `active` (`lost`+`found`), máx. 12 (más recientes por `date_reported`),
  tarjeta = foto + `Especie · color` + zona (`address_text`) + etiqueta `Perdido/Avistado`.
  NUNCA `contact_info`/teléfono (test dedicado). Foto en letterbox crema (`300×208`,
  animal entero centrado sin recortes, JPEG q65, data URI) con `st.cache_data(ttl=120)`.
  Movimiento continuo CSS marquee (`32s linear infinite`, pista duplicada `-50%`),
  pausa en hover, clic en tarjeta → `?aviso=<id>` → salta a su aviso y lo resalta.
  `@media (prefers-reduced-motion: reduce)`: sin animaciones.
  Vacío → estado con invitación a publicar el primero. Debajo, 3 contadores como
  `st.button` (navegación interna en la misma pestaña, sin pestañas externas):
  perdidos → `perdidos`, avistamientos → `encontrados`, reencuentros → `reencuentro`
  (`?page=` sigue soportado como deep-link de compatibilidad).

Restricciones: reutiliza paleta/tipografía/logo/fondo existentes (`#E30613/#23201B/#FFFFFF/
#F5F1EA/#57503F`, Inter+Montserrat); sin colores nuevos; animaciones solo CSS
(`st.markdown(unsafe_allow_html)` / `components.html`); sin dependencias nuevas.

## 15. Tanda UI v1.12 (24/09/2026, a petición del alumno; solo UI, sin tocar matching/agentes/RAG/BD)

- REQ-UI-07 — Mapa de Buscar: la leyenda dice AVISTAMIENTOS (nunca ENCONTRADOS) y
  muestra AMBOS lados (TU CASO + PERDIDOS + AVISTAMIENTOS). El mapa de zona es de
  referencia: pinta perdidos (azules) y avistamientos (verdes) con `pin_color()` vía
  `get_active_opuestos()` en dos `MarkerCluster`. El cruce sí va solo contra el canal
  elegido. `leyenda_mapa()` acepta `mostrar_perdidos/mostrar_avist` para el mapa de
  resultados (`render_mapa_avistados()` la infiere de los tipos visibles).
- REQ-UI-08 — Buscar se titula ANÁLISIS PRELIMINAR DE SIMILITUDES RESPECTO AL REGISTRO
  y se reenumera: 1. ¿Dónde buscas? · 2. Foto actual · 3. Zona · 4. Descripción ·
  5. Lanza la búsqueda.
- REQ-UI-09 — Barrido rojo continuo en los títulos de Publicar
  (`Publica un aviso de perdido o avistamiento`) y Buscar (REQ-UI-08): letras con
  degradado negro→rojo→negro que barre de izquierda a derecha y viceversa
  (`.huellas-barrido`, `huellas-sweep 3.2s ease-in-out infinite`).
- REQ-UI-10 — Renombres: `Animales perdidos activos` → MASCOTAS DESAPARECIDAS y
  `Avistamientos` → RASTROS COMPARTIDOS (subheaders + `stat_box` + infos).
- REQ-UI-11 — Huella roja de perímetro en MASCOTAS DESAPARECIDAS, RASTROS COMPARTIDOS y
  VOLVIÓ A CASA (`.huellas-perimetro` + `.huellas-perimetro-paw` con SVG de huella
  `#E30613`, `huellas-peri 6s linear infinite`, velocidad media).
- REQ-UI-12 — Fuera bocadillos: eliminado todo `help=` (hero, sidebar, sliders) + CSS de
  `stTooltipContent`, y fuera el `title=` del carrusel (`ui_home.build_carousel_html`)
  que repetía el texto en negro al pasar el cursor.
- Accesibilidad: `prefers-reduced-motion` apaga también `huellas-sweep` y `huellas-peri`.
- Regla CSS crítica (S76): las propiedades animadas por keyframes (`background-position`
  del barrido, `top/left` de la huella) van SIN `!important` en la base — con `!important`
  la base gana a los keyframes en la cascada y la animación queda congelada en el
  fotograma inicial (verificado en Edge headless: reloj avanzando, valores fijos).

## 16. Publicar con vida + cascada global (v1.13 25/09/2026, solo UI)

- REQ-UI-13 — Cascada global: en todas las pestañas, las hijas directas del bloque
  principal entran con fade-up escalonado de 60 ms (`huellas-cascade .45s`, delays
  0–.60 s, `both`). Juega una sola vez al montar (los reruns conservan el DOM).
- REQ-UI-14 — Foto en Publicar: zona con borde discontinuo rojo + huella flotante;
  al subir imagen, miniatura con línea de escaneo roja (~1,5 s, `huellas-scan`) y
  después la etiqueta "Foto analizada" (fade con retardo 1,5 s).
- REQ-UI-15 — Botón "Confirmar y publicar": pulso suave (anillo) cuando el
  formulario está completo; si faltan campos, se sacude (shake 400 ms, con remontaje
  por clave `confirm_pub_{n}` para que repita) y lista qué falta (`faltantes_publicar`
  pura y testeada en `ui_home.py`).
- REQ-UI-16 — Al publicar: bloque "Cruzando con N avisos…" con puntos que rebotan y
  barra de progreso (mínimo 1,5 s, real si tarda más). Con coincidencia ≥80%: tarjeta
  que entra deslizándose con anillo que barre 0→real y dígitos que ruedan 0→real
  (`steps(pct)`) + botón "Ver aviso y contactar". Sin coincidencia: check verde que se
  dibuja solo + "Te avisaremos si aparece algo".
- Regla CSS crítica (S77): NADA de `@property`/contadores CSS para el conteo — en
  Chromium `var()` dentro de `counter-reset` invalida la declaración (cae a `none`) y
  con `inherits:false` el SVG ni hereda: todo se quedaba en 0. Los keyframes se generan
  con valores FIJOS por tarjeta (`huellas-ringfill-<pct>`, `huellas-strip-<pct>` con
  pista interior `.huellas-track`: animar el propio contenedor con `overflow:hidden`
  desplaza la ventana entera y no se ve nada).

## 17. Obligatorios completos + foto despejada + autocompletado (v1.14 25/09/2026, solo UI)

- REQ-UI-17 — En Publicar, color principal y descripción pasan a obligatorios de verdad:
  etiqueta con `*`, validación en `faltantes_publicar()` (pulso/shake incluidos) y tests.
- REQ-UI-18 — Foto despejada: fuera la huella flotante y el caption
  "Sube una foto… (40%)"; el cuadro del uploader crece (`min-height:190px`) para ocupar
  el hueco.
- REQ-UI-19 — Autocompletado en Ubicación exacta (Publicar): al escribir (3+ letras),
  sugerencias clicables vía Nominatim (`sugerir_direcciones()`, caché 1 h, sesgo Jerez);
  elegir una centra el mapa. Sin red o sin texto, no aparece nada (sin romper).

## 18. Desplegable de sugerencias + etiqueta lateral (v1.15 25/09/2026, solo UI)

- REQ-UI-20 — Las sugerencias salen como lista emergente pegada al recuadro (filas
  blancas `addr_sug_{i}` con chincheta CSS y borde rojo en hover), no como radio:
  un toque centra el mapa. Se refrescan al confirmar el texto (límite de Streamlit:
  los widgets no emiten por cada tecla, solo al confirmar; sin JS).
- REQ-UI-21 — "Foto analizada" a la DERECHA de la imagen (fila flex `.huellas-scanrow`
  que aprovecha el hueco lateral), no debajo.

## 19. Ajustes foto + revert sugerencias (v1.16 25/09/2026, solo UI)

- REQ-UI-22 — "Foto analizada" más grande (1rem) y centrada en el hueco lateral
  (`.huellas-scanbadge` flex); imagen algo más pequeña (máx. 300px) con aire inferior
  (`.huellas-scanrow` con `margin-bottom`) para no rozar el cuadro de abajo.
- REQ-UI-23 — Revert total del autocompletado (REQ-UI-19/20): fuera sugerencias, CSS,
  `sugerir_direcciones()` y `short_addr()`; Ubicación exacta vuelve a botón de
  geocodificado + clic en mapa + ajuste manual.

## 21. Buscar con vida + Perdidos/Avistamientos (v1.18 25/09/2026, solo UI)

- REQ-UI-26 — Foto en Buscar: miniatura con línea de escaneo + esquinas de encuadre
  (`build_foto_scan_html()` con `esquinas=True`) y etiqueta "Foto lista".
- REQ-UI-27 — Mapa de Buscar: círculo rojo de 2 km (radio de búsqueda) alrededor de tu
  zona + chip de confirmación al elegir punto (chincheta que cae con rebote y anillo
  pulsante, una sola vez por clic).
- REQ-UI-28 — Botón "Buscar coincidencias": radar (anillos + barrido giratorio + pings,
  mínimo 1,5 s real) mientras procesa; si faltan campos, shake 400 ms + lista
  (`faltantes_buscar()` pura, remontaje `b_buscar_{n}`).
- REQ-UI-29 — Resultados en cascada (envoltorio `.huellas-res`, 80 ms por tarjeta):
  anillo que cuenta hasta el % real + 4 barras (Visual/Zona/Texto/Fecha, relleno
  600 ms con keyframes fijos `huellas-bar-<uid>-<k>`); la mejor, con borde rojo y
  pulso suave (`.huellas-res-top`). Fotos y desglose intactos debajo.
- REQ-UI-30 — Sin resultados: "Sin coincidencias por ahora" + "Guardar como aviso"
  (mismo prefill) con rebote suave continuo.
- REQ-UI-31 — Contacto oculto en Perdidos y Avistamientos: botón "Ver contacto" que lo
  despliega con transición de altura 300 ms (`bloque_contacto()` + `contacto_html()`
  escapado); nunca visible por defecto.
- REQ-UI-32 — Chip "N días perdido" con urgencia (verde ≤2, ámbar 3-6, rojo ≥7) desde
  la fecha efectiva.
- REQ-UI-33 — Etiqueta "Nuevo" con punto pulsante (<48 h).
- REQ-UI-34 — Avistamientos: mismo contacto bajo demanda y "Nuevo"; chip neutro
  "Visto hace N días" en vez del de urgencia.

## 22. Pulido Buscar/Publicar/Perdidos (v1.19 25/09/2026, solo UI)

- REQ-UI-35 — "Foto lista" en grande a la derecha de la foto (fila flex, como en
  Publicar) + relleno verde parpadeante consistente en ambas miniaturas
  (`.huellas-flash`, infinito suave).
- REQ-UI-36 — Fechas del seed aleatorias reproducibles entre el 25/08 y el 25/09
  (`make_seed.py` con semilla; la pareja E2E conserva las suyas) + `SEED_VERSION` 7;
  formato de muestra siempre DD/MM/AA (`fmt_corta()`, la BD sigue en ISO).
- REQ-UI-37 — Leyenda y chinchetas (ambos lados) también en el mapa de Publicar.
- REQ-UI-38 — Fix mapa Buscar: la dirección del clic se aplica ANTES de instanciar el
  widget (clave `q_addr_pending`; asignarla después reventaba) + caché 30 días en
  geocodificado directo e inverso (el mapa ya no se arrastra por la red).
- REQ-UI-39 — Contacto con `<details>` nativo: abre y recoge fluido (transición de
  filas 300 ms reversible) sin rerun; el resumén alterna Ver/Ocultar solo con CSS.

## 20. Boli en el hueco + imagen admin contenida (v1.17 25/09/2026, solo UI)

- REQ-UI-24 — Al subir foto en Publicar, la columna izquierda crece y deja hueco abajo
  a la derecha: lo rellena un boli escribiendo trazos en bucle (`build_pen_html()` en
  `ui_home.py`, al final de la columna derecha, SOLO si hay foto o precarga). Formato
  alto (`min-height:240px`, SVG 300×150) hasta la altura de "Cómo lo perdiste", con fondo
  translúcido (`rgba(255,255,255,0.45)`) que deja ver el patrón de la web y sin marco
  (`border:none`, S83).
- REQ-UI-25 — La foto del visor del administrador no desborda el sidebar: `show_image()`
  con `width=220` (letterbox centrado, animal entero) + guarda CSS
  (`max-width:100%` a las imágenes del sidebar).

## 13. Decisiones cerradas 23/09/2026 (13/13 — bloquean inicio de código)

1. Stack: Streamlit + Python + SQLite, 100% local. ✅
2. `image_embedding`: CLIP `openai/clip-vit-base-patch32`, 512-dim. ✅
3. `similitud_texto`: 70% estructurado (`color_primary`, `markings`, `has_collar`, `size`) + 30% semántico (`paraphrase-multilingual-MiniLM-L12-v2` sobre `description_text`). ✅
4. `proximidad_temporal`: `max(0, 1 - dias/30)`, ventana 30d, fecha = `date_last_seen` si existe si no `date_reported`. ✅
5. `radio_máximo`: 15 km fijos. ✅
6. Umbrales: `>=` en ambos (85 y 65). ✅
7. Ubicación: mapa Leaflet clicable + seed Jerez de la Frontera. ✅
8. `image_url`: ruta local `data/seed/images/`. ✅
9. Notifier: panel/tabla Streamlit + log, sin Telegram. ✅
10. Conflicto: manda Vision para `color_primary`; `description_text` intacto. ✅
11. `status`: botón "Marcar como resuelto" + `expire_old()` 30d bajo demanda, sin cron. ✅
12. `other`: obligatorios `color_primary`, `size`, `description_text`; opcionales `markings`, `has_collar`; `breed_guess` NULL. ✅
13. Idioma: solo español. ✅
