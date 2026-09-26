# PROMPT-LOG — MascotasLost&Found

Memoria de sesiones con IA (entregable EOI). Cada entrada: fecha, objetivo, prompts clave, decisiones, verificación.

## S01 — 23/09/2026 — Specs SDD (OpenCode)
- Objetivo: formalizar `requirements.md` + `architecture.md` sin inventar decisiones.
- Prompts: borrador requirements con esquema Aviso, 5 agentes, fórmula cerrada 0.40/0.30/0.20/0.10, umbrales.
- Decisiones del alumno (13/13): Stack Streamlit+SQLite 100% local · CLIP `openai/clip-vit-base-patch32` 512-dim · texto 70/30 MiniLM `paraphrase-multilingual-MiniLM-L12-v2` · temporal `max(0,1-dias/30)` con `last_seen→reported` · radio 15 km · umbrales `>=` · Leaflet + Jerez seed · `image_url` local · Notifier panel+log · manda Vision en color, texto intacto · botón resolver + `expire_old()` sin cron · `other` sin `breed_guess` · solo español.
- Verificación: specs v1.0, huecos H-01..H-10 cerrados. Commits `docs(spec)`.

## S02 — 23/09/2026 — Scaffolding + tests (OpenCode)
- Objetivo: núcleo ejecutable trazable a spec.
- Prompts: "arranca scaffolding con commits trazables".
- Resultado: `agents/geo,ingestor,matcher,vision,db,notifier` + `rag/embeddings,retrieval` + seed Jerez 17 avisos (5 lost+12 found) + `app.py` + `tests` 13/13 + `eval_match.py` OK.
- Correcciones IA detectadas por el alumno: `sys.path.insert` (scripts), floor negativo de `timedelta.days` → comparar `.date()`, assert float con tolerancia.
- Commits `feat(matcher|rag)`, `data(seed)`, `feat(app)`.

## S03 — 23/09/2026 — GitHub + README + smoke test (OpenCode)
- Identidad git fijada a Mario Camacho; 6 commits reescritos a su autoría (previo al primer push) y rama `master→main`.
- Remoto `origin` https://github.com/mpn1706/HUELLAS-ProyectoFinalEOI, push `main` OK.
- `README.md` con problema, funcionalidades, fórmula, stack, ejecución <10 min y estado de despliegue.
- Corrección IA: `retrieve` pasaba vectores al matcher (TypeError) → coseno movido a retrieval + fallback visual por bytes de imagen.
- Verificación: pytest 13/13, `demo_check.py` E2E (found_001 top-1 96.3%), `smoke_app.py` AppTest headless sin excepciones (3 tabs).

## S04 — 23/09/2026 — Informe de reflexión (OpenCode)
- `INFORME.md`: qué ejecutó la IA, 13 decisiones propias supervisadas, 5 errores IA detectados por ejecución y corregidos (sys.path, timedelta floor, float tol, vectores-vs-float en retrieval, AppTest path) + limitación documentada del fallback visual.

## S05 — 23/09/2026 — Autoseed para deploy cloud (OpenCode)
- `ensure_db()` auto-carga los 17 JSON del seed si la DB está vacía (filesystem efímero en Streamlit Cloud, `huellas.db` gitignored).
- Verificación: DB borrada → smoke AppTest OK → E2E found_001 top-1 96.3%. README actualizado con pasos de deploy.

## S06 — 23/09/2026 — Fix post-deploy Cloud (OpenCode)
- Reporte desde https://huellas.streamlit.app/: `use_column_width` obsoleto (TypeError), sin preview en Buscar, selectbox truncado.
- Fix: `use_container_width` + `show_image()` con placeholder si falta el fichero; uploader con vista previa en Buscar (su embedding sustituye al registrado) y en Registrar; cabecera 🐾 HUELLAS; selectbox corto `[id] animal · color · tamaño` + tarjeta completa debajo.
- Verificación: 0 restos de `use_column_width`, pytest 13/13, smoke OK, E2E OK.

## S07 — 23/09/2026 — Rediseño visual de la interfaz (OpenCode)
- La imagen adjunta por el alumno no era un logo (foto de producto Lacoste): no se usa; hueco `assets/logo.png` con fallback 🐾.
- Nueva UI: cabecera con logo, métricas (lost/found/alertas), Buscar en 3 pasos (aviso→foto→filtros), tarjetas con borde, barra de score, sub-scores en métricas, mapa, Registrar en 2 columnas con preview, Alertas con log plegable.
- Lógica intacta: pytest 13/13, smoke OK, E2E found_001 top-1 96.3%.

## S08 — 23/09/2026 — Integración del logo (OpenCode)
- Logo real del alumno (brújula + huella + wordmark HUELLAS). Cabecera adaptativa: con logo no se duplica el título; `page_icon` usa el logo; sidebar sin cabecera redundante.
- Pendiente: el alumno guarda el PNG en `assets/logo.png` (la app lo detecta sola).
- Logo recibido y publicado como `assets/logo.png` (PNG 1262×832): cabecera, sidebar y favicon lo usan; se retira `assets/README-logo.md`.

## S09 — 23/09/2026 — Logo sin fondo + tagline (OpenCode)
- `get_logo_img()`: blancos >240 a transparente (94% píxeles) para fundirse con sidebar/cabecera.
- Tagline "Agente de Búsqueda y Comparativa Visual de Animales Perdidos" en header y sidebar; subtítulo "…avisos de avistamientos en Jerez de la Frontera" (aviso legal sigue en resultados, alertas y log).
- Verificación: pytest 13/13, smoke OK con logo real.

## S10 — 23/09/2026 — Fondo patrón (OpenCode)
- `inject_background()`: `assets/fondo.png` como fondo de app + sidebar con velo blanco (legibilidad), base64 inline, sin dependencias; inactivo si falta el archivo.
- Pendiente: el alumno guarda el patrón en `assets/fondo.png`.
- Fondo recibido y publicado (`assets/fondo.png`, PNG 1262×832): mosaico en app + sidebar con velo blanco; smoke OK con fondo activo.

## S11 — 23/09/2026 — Patrón también en la barra superior (OpenCode)
- La barra `stHeader` (Share/⋮) trae fondo propio del tema: se le aplica el mismo mosaico + velo. Smoke OK.

## S12 — 23/09/2026 — Tema claro forzado (OpenCode)
- En dark mode el texto blanco sobre nuestro fondo claro era ilegible: `.streamlit/config.toml` fija `base="light"` + paleta cálida acorde al patrón. Smoke OK, pytest 13/13.

## S13 — 23/09/2026 — Contraste de widgets (OpenCode)
- Selects, inputs, file uploaders, sliders, expanders y botones secundarios con tarjeta blanca sólida + borde `#C9BFAE` + sombra sutil; botones primary intactos. Smoke OK.

## S14 — 23/09/2026 — Tarjetas oscuras (OpenCode)
- Corrección del alumno: las quería negras, no blancas. Tarjeta `#23201B` + etiquetas/valores en `#F5F1EA` (scopeado por widget para no romper checkbox/código), botones secundarios oscuros con hover. Smoke OK.

## S15 — 23/09/2026 — Divisores oscuros (OpenCode)
- `st.divider` en `#23201B` 2px para la misma línea visual. Smoke OK.

## S16 — 23/09/2026 — Todas las líneas en negro + pin de versiones (OpenCode)
- El alumno no veía cambios: el `st.divider` no tiene testid propio en 1.64 → regla sobre `hr`; tarjetas con borde nativo vía `border-color` en `stVerticalBlock` (verificado en el bundle: el borde sale del tema, sin testid propio); filete bajo pestañas vía `stTabs [role=tablist]`.
- `requirements.txt` fija `streamlit==1.64.0` y `streamlit-folium==0.27.4` para que Cloud sea idéntica al local. Smoke OK, pytest 13/13.

## S29 — 23/09/2026 — Fix clic en mapa (OpenCode)
- Causa en la doc de streamlit-folium: sin `key`, al reconstruir el mapa con otro centro el componente se re-monta y el clic se pierde (el arrastre, client-side, sí funcionaba). Fix: `key` estable + `center/zoom` dinámicos en ambos mapas. Smoke OK, pytest 13/13.

## S30 — 23/09/2026 — Celebración con lupas y huellas (OpenCode)
- Fuera `st.balloons()`: `celebrate_search()` con 8 SVG (huella negra + lupa roja) flotando 3s, solo CSS efímero, sin emojis. Smoke OK, pytest 13/13.

## S31 — 23/09/2026 — Pestaña Encontrados (OpenCode)
- Nueva pestaña con tarjetas foto+dato+viñetas y filtro por animal; métrica "Encontrados" (sin "activos"). Smoke OK (4 tabs), pytest 13/13.

## S32 — 23/09/2026 — Administrador (OpenCode)
- Cambio de alcance formal (spec v1.1: REQ-04.3 excepcionado, CU-06, REQ-11). `agents/admin.py`: login por contraseña (Secrets/env/defecto), borrado con confirmación + limpieza de notifs/foto, resolver, `admin.log`. Pestaña Administrar. Pytest 17/17, smoke OK (5 tabs).

## S33 — 23/09/2026 — Admin al sidebar + reorden de pestañas (OpenCode)
- Administración compacta bajo DATOS DEMO con divisor; orden: Publicar, Buscar, Encontrados, Alertas. Spec CU-06 actualizada. Pytest 17/17, smoke OK (4 tabs).

## S34 — 23/09/2026 — NameError con alertas (OpenCode)
- `logp` quedó indentado en el `else`: crash justo cuando HAY notificaciones (reproducido en Cloud tras buscar). Fix + test con fila real + limpieza. Pytest 17/17, smoke OK.

## S35 — 23/09/2026 — Alertas sin duplicados + flujo fotos reales (OpenCode)
- Notifier con upsert por par (misma score se ignora, distinta se actualiza) + 4 tests. Infra fotos: `backfill_embeddings()` + `compute_embeddings.py` (torch solo local) + `embeddings.json` versionado; README con flujo y nota de licencias. Pytest 21/21, E2E 96.6%, smoke OK.

## S36 — 24/09/2026 — Seed v2 con fotos reales + admin editable (OpenCode)
- 16 fotos del alumno (9 perros, 6 gatos, 1 loro): seed nueva 6 lost + 10 found con rasgos visibles y pool de ubicaciones reciclado; placeholders viejos eliminados.
- Hallazgos: histograma insuficiente (fondos dominan) y rama CLIP rota (`BaseModelOutputWithPooling` → `pooler_output`); CLIP real da 0.63-0.75 en parejas. `embeddings.json` con 16 vectores versionado.
- Admin edita cualquier campo (validado + log). Smoke con timeout 60s (árbol grande). Pytest 27/27, parejas 5/5 ≥65%, E2E OK.

## S37 — 24/09/2026 — Seed versionado (OpenCode)
- Cloud mostraba datos viejos con código nuevo: la DB sobrevive al redespliegue y el autoseed solo cargaba si vacía. `PRAGMA user_version` + `SEED_VERSION=2`: al subir, wipe + recarga + avisos frescos (también limpia fantasmas found_011/012 en local). Pytest 27/27, E2E y smoke OK.

## S38 — 24/09/2026 — Evidencia Engram (OpenCode)
- Engram CLI localizado (`engram.exe`, sin proyecto HUELLAS previo: esta sesión no estaba conectada). 6 hitos guardados con `--project HUELLAS` (#56-61) + exportado a `docs/engram/` (6 notas + hub). Verificado contenido.

## S39 — 24/09/2026 — Captura automática Engram (OpenCode)
- `engram setup opencode` ejecutado: plugin en `.config/opencode/plugins/engram.ts`. Requiere reiniciar OpenCode; desde entonces las sesiones se registran solas (+hito #62). Lo previo queda cubierto por PROMPT-LOG + `docs/engram/`.

## S17 — 23/09/2026 — Subrayado único en pestañas (OpenCode)
- El rojo activo se solapaba con el filete negro: fuera el filete base; la pestaña activa lleva un único subrayado negro 3px + semibold. Smoke OK.

## S18 — 23/09/2026 — Apagado del indicador rojo (OpenCode)
- El rojo era `.react-aria-SelectionIndicator` (verificado en el bundle 1.64, no el borde del botón): `transparent !important`. Queda solo el subrayado negro. Smoke OK.

## S19 — 23/09/2026 — Sistema de diseño corporativo (OpenCode)
- Inter (texto) + Montserrat 800 (títulos); todo a MAYÚSCULAS por CSS salvo inputs/código; texto `#000000` vía tema (crema `!important` solo dentro de tarjetas oscuras); cero emojis verificado por script; métricas sustituidas por cajas negras cuadradas `stat_box()` (st.metric no tiene hook en 1.64); tagline en cursiva. Smoke OK, pytest 13/13, E2E OK.

## S20 — 23/09/2026 — Paleta negro/blanco/rojo (OpenCode)
- `primaryColor` terracota → rojo brillante `#E30613`: sliders, botón primario, pestaña activa y barra de progreso pasan a rojo de una vez. Smoke OK.

## S21 — 23/09/2026 — Aviso legal único en sidebar (OpenCode)
- Fuera de alertas, resultados (`explain`), log y cabecera; sidebar sin logo/tagline redundantes; expander negro AVISO LEGAL con el texto nuevo + título FUNCIONAMIENTO WEB sobre Cómo puntúa. Specs y README actualizados. Pytest 13/13, smoke y E2E OK.

## S22 — 23/09/2026 — Aviso legal al final del sidebar (OpenCode)
- Expander movido bajo DATOS DEMO con divisor negro como el de Funcionamiento/Datos. Smoke OK.

## S24 — 23/09/2026 — Aviso legal dentro de Funcionamiento web (OpenCode)
- El expander pasa a ser el segundo de FUNCIONAMIENTO WEB (tras Cómo puntúa); se retira el bloque inferior. Smoke OK.

## S25 — 23/09/2026 — Mayúsculas totales + uploader en español (OpenCode)
- `text-transform` también en inputs/selects/portales (solo visual); botón Upload→SUBIR FOTO y límites→español por CSS (1.64 sin i18n, verificado en el chunk FileUploader); datos de tarjeta con viñetas. Pytest 13/13, smoke y E2E OK.

## S26 — 23/09/2026 — Hint oculto y uploader sin solapes (OpenCode)
- `InputInstructions` ("Press Enter...") oculto: el envío va por botón. El ocultado del uploader bajó a los hijos (llevan tamaño propio): solo SUBIR FOTO + límites en español. Smoke OK.

## S27 — 23/09/2026 — Selector de ubicación (OpenCode)
- Dirección→coords vía Nominatim (stdlib, con sesgo Jerez) + clic en mapa Leaflet + ajuste manual en expander; sustituye a los number_inputs (estaba en REQ-05.8 y faltaba). Corregido warning de sesión en `reg_lat` y migrado `use_container_width`→`width="stretch"`. Pytest 13/13, smoke y E2E OK.

## S28 — 23/09/2026 — Seed con ubicaciones exactas (OpenCode)
- `geocode_seed.py` (Nominatim, 1.2s pausa): 13/17 exactas (calle/barrio); 4 sin resultado conservan valor previo (found_010 aposta lejos); etiqueta manual del parque; el estadio cae en El Pelirón según OSM (mi recuerdo del oeste era erróneo). `sync_seed_gen.py` alinea el generador (regen no-op verificado). E2E 96.6%, pytest 13/13.

## S23 — 23/09/2026 — Español total + mayúsculas en portal y botones (OpenCode)
- Mapas ES en display (`Perro/Gato/Otro`, `Pequeño/Mediano/Grande`; la BD sigue en inglés por spec); datos collar/visto/zona en vertical; `text-transform` también en popover del desplegable y en `button` (no heredan). Pytest 13/13, smoke y E2E OK.

## S40 — 24/09/2026 — Evidencia proceso IA para entrega (Muse Spark)
- El alumno pregunta si Engram estaba activo y cómo cumplir el punto 4 del profe (`PROMPT-LOG.md` + exportación Engram).
- Se reconoce por escrito: S01-S37 no tuvieron Engram conectado; S38 reconstruyó 6 hitos a posteriori en proyecto `huellas` (#56-61) + export a `docs/engram/`; S39 activó captura automática (`engram setup opencode`, +hito #62). La sesión actual autodetecta `huellas-proyectofinaleoi` (0 obs, 2 prompts), separada del histórico `huellas`.
- Acción: hito #63 guardado en `huellas` (S40), PROMPT-LOG actualizado y re-exportado vault + JSON para acreditar pasos ante el profesor.

## S41 — 24/09/2026 — Perdidos + chinchetas + alertas demo + conteo (Muse Spark)
- Chinchetas: nuevo `render_mapa_avistados()` con tooltip + popup (id, animal, dirección, distancia); mapa previo "Avistados cerca" con los 10 found en azul + mapa de resultados (verde ≥85 / azul).
- Conteo 16 vs 15: no era bug — `lost_006` es resuelto demo ("volvió a casa"). UI lo explica: caption "16 totales (5 activos +1 resuelto +10 encontrados)", botón seed "16 avisos · 15 activos" con recarga real (wipe + 16 + backfill + demo, antes llamaba a make_seed).
- Alertas demo: `ensure_demo_alert()` precarga lost_001→found_001 si la tabla está vacía + botón "Generar alerta demo" + tarjetas con fotos (antes tabla vacía + solo tabla). Honesto: sin sentence-transformers el par da 79.8% (top-1 OK, bajo umbral); la demo usa 96.3% de referencia con modelos completos y log `#demo-referencia`.
- Navegación: fuera `st.tabs` (4); ahora `session_state.page` con 5 páginas (buscar/perdidos/encontrados/alertas/publicar): 3 botones negros arriba con conteos + 2 rojos primary centrados abajo (Publicar / Buscar). Nueva página Perdidos con filtro y tarjetas como Encontrados.
- Verificación: pytest 27/27, smoke 5 páginas OK, E2E found_001 top-1 79.8% ≥65%. `smoke_app.py` recorre las 5 páginas.

## S42 — 24/09/2026 — Botonera según feedback (Muse Spark)
- Las 3 cajas negras SON los botones (`5 · PERDIDOS ACTIVOS`, etc., secondary oscuros): navegan directo, sin "Ver perdidos…" debajo. Las rojas (`Publicar aviso` / `Buscar a mi mascota`, primary) suben justo debajo de las negras, centradas; se retira la botonera inferior duplicada y el submit de Publicar pasa a "Confirmar y publicar".
- Verificación: pytest 27/27, smoke 5 páginas OK.

## S43 — 24/09/2026 — Sidebar, leyenda, etiquetas y retirada demo (Muse Spark)
- Sidebar: fórmula en markdown blanco en negrita (antes `st.code` con scroll horizontal) + 4 cajas negras 2×2 (≥85% ALERTA · ≥65% EN LISTA · RADIO 15 KM · VENTANA 30 DÍAS) en blanco.
- Mapa: `pin_color()` verde = encontrados, azul = perdidos activos, rojo = tu mascota; DESTACADA ≥85% en el popup; leyenda al lado del mapa (columnas 5:1) y pre-búsqueda con otros perdidos en azul.
- Botoneras: `PERDIDOS ACTIVOS (5)`, `ENCONTRADOS (10)`, `ALERTAS (1)`.
- Alerta demo retirada (no era el mismo gato): fuera `ensure_demo_alert()` + botón demo; nuevo `retirar_alerta_demo()` borra la fila 0.963 en local y Cloud con traza en log; Alertas solo muestra reales ≥85% (vacía hasta que el alumno suba foto correcta).
- Verificación: pytest 27/27, smoke 5 páginas OK, demo local eliminada (0 alertas).

## S44 — 24/09/2026 — Filtros, clusters con foto y seed (Muse Spark)
- Filtros en Perdidos y Encontrados: `aplicar_filtros()` con animal + color (del seed: blanco, gris, marrón, naranja, negro, verde) + tamaño, en 3 columnas.
- Chinchetas: las faltantes estaban solapadas (found_001/009, found_004/010 y lost_003/found_008 comparten coords) → `MarkerCluster` por tipo con contador y despliegue al pulsar; popup con foto (`thumb_uri()` JPEG 240px base64, funciona en Cloud) + datos + DESTACADA.
- Seed: botón "CARGAR SEED JEREZ (15 AVISOS ACTIVOS)" y toast coherente.
- Verificación: pytest 27/27, smoke 5 páginas OK, MarkerCluster verificado.

## S45 — 24/09/2026 — Alerta real lost_001→found_011 (Muse Spark)
- Foto del alumno guardada como `data/seed/images/gato alert coincidencia con lost_001.jpg`; alta `found_011` (gato naranja, rayas + cola anillada, small, sin collar, Calle San Miguel a 90 m de lost_001, 20/09).
- `make_seed.py` + `SEED_VERSION=3` (Cloud recarga sola) + `embeddings.json` con 17 vectores CLIP (imprescindible: Cloud no tiene torch).
- Score real 89.9% (v=0.81, g=0.99, t=0.89, tmp=0.97) → `notificar()` genera la alerta; `demo_check.py` ahora exige top=found_011 ≥85% (found_001 sigue ≥65%).
- Textos a 17 avisos / 16 activos / 11 encontrados. Verificación: pytest 27/27, smoke 5 páginas OK, E2E OK.

## S46 — 24/09/2026 — Foto found_011 de mayor calidad (Muse Spark)
- Alumno sustituye el JPG (320×427); misma descripción e id. `embeddings.json` regenerado (17 CLIP) + nuevo `sync_seed_embeddings()` en `agents/vision.py` (actualiza vectores cambiados en local y Cloud sin wipe; llamado en `ensure_db` y recarga seed).
- Nuevo score real 85.6% (visual 0.71, antes 0.81 con la foto pequeña): sigue ≥85, alerta actualizada. Verificación: pytest 27/27, smoke 5 páginas OK, E2E OK.

## S47 — 24/09/2026 — Textos: sin caption seed, avistamientos (Muse Spark)
- Fuera el caption "Seed v… avisos totales…" bajo la botonera.
- Botón `ENCONTRADOS (11)` → `AVISTAMIENTOS (11)` (+ subheader, info y contador de la página).
- Publicar: "Publica un aviso de perdido o avistamiento".
- Verificación: pytest 27/27, smoke 5 páginas OK (solo textos).

## S48 — 24/09/2026 — Buscar libre + alerta al publicar (Muse Spark)
- Decisión del alumno tras discutirlo: fuera "Elige tu aviso"; Buscar es libre (1 foto obligatoria + 2 zona con geocoder, mapa clicable con dirección autocompletada vía `reverse_geocode_nominatim`, y manual + mini-mapa de avistados + 3 descripción + 4 lanzar con autoregistro opcional que reutiliza el mismo id para alertas).
- Alertas del cruce de datos: al publicar (ambos sentidos) y al guardar una búsqueda; la búsqueda libre transitoria no notifica ni persiste (verificado: DB intacta).
- Spec: CU-03 reescrito en `requirements.md`. Verificación: pytest 27/27, smoke 5 páginas OK, E2E OK, flujo libre simulado (top found_011 82.6%, 0 filas nuevas).

## S49 — 24/09/2026 — Bug Cloud: mismo espacio visual (Muse Spark)
- Sí había error: en Cloud (sin torch) la query se incrustaba en histograma y los candidatos en CLIP → coseno 0.09, todo bajo 65, lista vacía. Repro local: mixto 0 matches, hist-hist 5 matches (top 98.7%).
- Fix: `embedida_con_espacio()` + `embed_candidato()` en `agents/vision.py` (mismo espacio a ambos lados; fotos seed en git, también en Cloud); fuera `visual_fn_factory()`; 2 tests nuevos; nota en `requirements.md` §8.
- Verificación: pytest 29/29, smoke 5 páginas OK, E2E OK.

## S50 — 24/09/2026 — Resultados que no se repliegan (Muse Spark)
- Bug: los candidatos vivían solo en el run del clic (`if st.button`); cualquier rerun extra (montaje de mapas, sliders, checkbox) los hacía desaparecer.
- Fix: la búsqueda se guarda en `st.session_state.b_search` y el render (filtros, tarjetas, mapa) lee de ahí; + botón "Limpiar resultados"; de paso se corrigió `st.code(explain)` que estaba indentado dentro de la columna Tiempo.
- Verificación: pytest 29/29, smoke 5 páginas OK.

## S51 — 24/09/2026 — Pesos v1.2 + umbral 80 + UI buscar (Muse Spark)
- Pesos (decisión alumno, geo penalizaba): 0.40 visual + 0.30 texto + 0.20 temporal + 0.10 geo (`matcher.py`, spec §8 v1.2, `architecture.md`, `README.md`, sidebar, sub-scores en orden V-T-T-G).
- Consecuencia medida: found_011 84.3% <85 → umbral de alerta 85→80 (decisión alumno; spec §9, notifier, tests, E2E, README, UI). Demo viva como alerta real.
- Buscar: slider "Mostrar a partir de este porcentaje…" con formato `65 %`; un solo mapa (zona clicable + clusters + leyenda); `help` descriptivo en los 5 botones; fuera el caption de buscar.
- Verificación: pytest 29/29, smoke 5 páginas OK, E2E top found_011 84.3% ≥80%.

## S52 — 24/09/2026 — Perreras, tiempo+perro e imágenes (Muse Spark)
- Botonera sobre la cabecera: PERRERAS DE JEREZ (CMPA El Portal + No Me Abandones San Salvador 21B, verificados en jerez.es/nomeabandones.org + aviso Laceros) y TIEMPO EN JEREZ (Open-Meteo sin claves, caché 30 min; perro SVG animado: contento/calor(jadeo)/lluvia/triste/temblando según código+temperatura).
- Imágenes: `show_image()` a 380px y previews a 360px (antes todo a `stretch`, sobredimensionadas).
- Verificación: pytest 29/29, smoke 5 páginas OK. Tiempo no verificable en sandbox sin red ( Cloud sí tiene; con fallo muestra aviso).

## S53 — 24/09/2026 — Perro por components + botones abajo (Muse Spark)
- El perro salía como código: `st.markdown` no traga `<style>`+`<svg>` → render con `components.html` (iframe, altura 190).
- Botonera Perreras/Tiempo movida al pie de página; panel perreras en 2 tarjetas con cabecera negra.
- Verificación: pytest 29/29, smoke 5 páginas OK + paneles perreras/tiempo sin excepciones.

## S54 — 24/09/2026 — Perro sin texto, header, alerta visible, contacto (Muse Spark)
- Perro: fuera el texto (solo animación); mapa contento/despejado, jadeo≥30º, lluvia, triste=viento≥35, tirita≤8º (nieve también).
- Header: logo centrado en vertical con el tagline (`vertical_alignment="center"`).
- Publicar: si hay cruce ≥80%, caja destacada con celebración + botón "Ver la alerta" (redirige a ALERTAS).
- Contacto opcional al publicar (móvil/correo/RRSS → `contact_info`) y visible en tarjetas de Perdidos/Avistamientos.
- Verificación: pytest 29/29, smoke 5 páginas OK.

## S55 — 24/09/2026 — Imágenes, iconos, mapa, contactos, luna (Muse Spark)
- Imágenes: `imagen_cuadrada()` (recorte central 480px, sin caché para ver sustituciones al instante) en tarjetas; `vista_previa()` ajustada en subidas.
- Iconos ⌂/☀︎ negros grandes arriba-izquierda (CSS por aria-label) con paneles plegables; fuera botones del pie.
- Mapa: ancho 700 + leyenda a alto completo (fuera el hueco blanco).
- Contactos: 8 avisos con móvil variado, 9 vacíos (`make_seed.CONTACTOS`); SEED v4 (recarga Cloud; alerta se regenera con una búsqueda).
- Perro: luna 20:00–08:00 (`es_de_noche`), lluvia, termómetro calor/frío y ráfagas de viento.
- Verificación: pytest 29/29, smoke 5 páginas + paneles OK, E2E OK.

## S56 — 24/09/2026 — Iconos bajo >>, letterbox, >> negro (Muse Spark)
- Iconos pegados arriba (contenido a 1.2rem del `>>`) + CSS para el `>>` en negro (varias variantes de testid, best-effort).
- Fotos: letterbox crema 480px (animal entero, nada de recortes que decapiten).
- Verificación: pytest 29/29, smoke 5 páginas OK.

## S57 — 24/09/2026 — Publicar completo, sin fullscreen, iconos al >> (Muse Spark)
- Publicar: columna izquierda con Comportamiento/estado + Cómo lo perdiste/qué hiciste (se anexan a la descripción y mejoran el texto).
- Fullscreen de imágenes desactivado por CSS (daba error y no se usa).
- Iconos pegados al `>>` (contenido a 0.2rem, fila compacta).
- Verificación: pytest 29/29, smoke 5 páginas OK.

## S58 — 24/09/2026 — Sidebar, cuadros, leyenda (Muse Spark)
- Iconos ⌂/☀︎ dentro del sidebar (uno al lado del otro, con divisor negro) + paneles apilados; "FUNCIONAMIENTO WEB" → "PUNTUALIZACIONES SOBRE LA WEB".
- Publicar: Comportamiento y Estado en cuadros separados (ambos anexan a la descripción).
- Mapa: leyenda en franja bajo el mapa, sin columna lateral blanca.
- Verificación: pytest 29/29, smoke 5 páginas + paneles OK.

## S59 — 24/09/2026 — Volvió a casa en vez de Alertas (Muse Spark)
- Opinión: de acuerdo; la sección aportaba poco y el backend (`notifications`+log+E2E) sigue como trazabilidad.
- Nueva sección VOLVIÓ A CASA (contador de cerrados): multiselect perdido/avistamiento + fotos + nota → pendiente; galería de cierres y en revisión. Admin: valida (resuelve avisos) o rechaza (vandalismo, intactos), todo en `admin.log`. Tabla `reencuentros` + 3 tests.
- Alerta ≥80% intacta en publicar y buscar-guardada, pero "Ver la alerta" → "VER COINCIDENCIA" que salta al caso del otro lado y lo resalta primero.
- Spec: CU-05 + REQ-11.5. Verificación: pytest 32/32, smoke 5 páginas OK, ciclo reencuentro OK (DB restaurada), E2E OK.

## S60 — 24/09/2026 — Preliminar ambos lados + orden (Muse Spark)
- Buscar = BÚSQUEDA PRELIMINAR DE COINCIDENCIAS con selector de canal (quien busca es el caso inverso), transitoria sin guardar ni filas; al final botón PUBLICAR AVISO (allí se discierne el tipo). Caja de coincidencia + VER COINCIDENCIA en pantalla.
- Rojos invertidos: primero preliminar, luego publicar.
- Spec: CU-03 reescrito. Verificación: pytest 32/32, smoke 5 páginas OK, lado inverso simulado (top lost_001 73.9%, DB intacta).

## S61 — 24/09/2026 — Prefill publicar desde buscar (Muse Spark)
- El botón PUBLICAR AVISO lleva foto, zona y descriptivos a Publicar (`ir_a_publicar_con`); el tipo se infiere del canal (avistamientos→perdido y viceversa). Foto reutilizada por copia; "Empezar de cero" limpia; CU-03.
- Verificación: pytest 32/32, smoke 5 páginas OK, prefill simulado ambos lados con DB limpia.

## S62 — 24/09/2026 — Mapas anchos, blancos y SELECCIONAR (Muse Spark)
- Mapas con `use_container_width=True` (el iframe dejaba el hueco blanco a la derecha).
- Textos libres en blanco con `placeholder` de ayuda; selects con `SELECCIONAR` (`index=None`) + validación; formulario fresco al entrar en Buscar.
- Verificación: pytest 32/32, smoke 5 páginas OK, blancos comprobados por AppTest.

## S63 — 24/09/2026 — Inicio + navegación lateral + carrusel (Muse Spark)
- SDD primero: `requirements.md` §14 (REQ-UI-01..06) + `architecture.md` §8 (capa UI), espejados en `docs/`; matching, agentes, RAG y BD intactos; logo, header y fondo intactos.
- Nuevo `ui_home.py` puro (testeable sin Streamlit): `select_carousel_items()` filtra activos lost/found, máx. 12 recientes, ignora `contact_info` por construcción; `build_carousel_html()` marquee CSS con foto + Especie·color + zona + Perdido/Avistado, clic `?aviso=<id>`; vacío invita a publicar el primero.
- `app.py`: página `inicio` por defecto con hero (ESTOS PELUDOS / QUIEREN VOLVER A CASA en rojo con subrayado dibujado + corazón SVG con latido, fade-up por líneas) + 2 botones grandes (Publicar rojo sólido con pulso anillo / Búsqueda preliminar con borde rojo, visibles en móvil) + carrusel (miniaturas 300px data-URI con `st.cache_data(ttl=120)`, pausa en hover, `prefers-reduced-motion` sin animaciones) + 3 contadores (perdidos/avistamientos/reencuentros).
- Sidebar: Inicio/Perdidos/Avistamientos/Volvió a casa con icono Material + contador y activo con barra roja `#E30613`; sección Más (Protectoras/Tiempo/Aviso legal como páginas); CTAs al final en rojo; Datos demo y Administración plegados. Navegar conserva `session_state` (filtros intactos); solo CSS con paleta existente, sin dependencias nuevas.
- Verificación: pytest 36/36 (nuevo `tests/test_carousel.py`: sin contacto ni teléfono, máx. 12, etiquetas, vacío), smoke 9 páginas OK, demo_check E2E OK (found_011 top-1 ≥80%).

## S64 — 24/09/2026 — Inicio v1.3: sidebar de 5, hero 2×rojo, carrusel centrado, contadores clicables (Muse Spark)
- Sidebar nuevo en `app.py` (REQ-UI-02 v1.3): solo 5 elementos en orden — INICIO (casa), PUNTUALIZACIONES WEB (aviso, plegable → Cómo puntúa + Aviso legal), DATOS DEMO (stats, plegable → seed + expirar), MÁS (+, plegable → Protectoras y Tiempo en Jerez en negro), ADMINISTRACIÓN (llave, plegable → login + moderación). Fuera del lateral: Perdidos/Avistamientos/Volvió a casa, Aviso legal directo y los 2 CTAs. Botones negros `#23201B`/`#F5F1EA`, plegables con `_toggle()` colapsados por defecto, `nav_to()` limpia `?page=`/`?aviso=`.
- Hero solo en inicio (REQ-UI-03): `Publicar aviso` + `Búsqueda de coincidencias` (renombrado), ambos rojo sólido `#E30613` idénticos con pulso anillo; `type="primary"` en los dos.
- Carrusel centrado (REQ-UI-06): `carousel_thumb()` delega en `ui_home.make_carousel_thumb()` (letterbox crema 300×208, animal entero centrado, JPEG q65, data URI, `st.cache_data(ttl=120)`); CSS `.huellas-cd-img img` pasa a `object-fit:contain` centrado.
- Contadores clicables (REQ-UI-06): `render_inicio()` usa `build_counts_html()` (`?page=` → perdidos/encontrados/reencuentro) + nuevo `handle_counts_click()`; CSS `.huellas-count-link` con hover que levanta la tarjeta y marca borde rojo; `prefers-reduced-motion` cubre ambos anillos hero.
- Specs REQ-UI-02/03/04/06 + `architecture.md` §8 ya estaban en v1.3 (root + `docs/`), sin cambios nuevos.
- Verificación: pytest 38/38 (letterbox 300×208 + counts con links/sin contacto), smoke 9 páginas OK, demo_check E2E OK (found_011 top-1 84.3% ≥80%).

## S65 — 24/09/2026 — Sidebar rojo + FUNCIONALIDADES, contadores internos, contacto obligatorio (Muse Spark)
- Hero sin la línea JEREZ DE LA FRONTERA (redundante con el header); buscar sin el "(pesa el 40%)" en el uploader. El caption de perdidos ya era dinámico y muestra "5 activos de 6 perdidos totales (1 resuelto demo: el gatito gris que volvió a casa)": sin cambios.
- Sidebar v1.4 (REQ-UI-02/04): 6 elementos — INICIO + FUNCIONALIDADES (apps, desplegado por defecto, agrupa Publicar aviso + Búsqueda de coincidencias también en el lateral) + PUNTUALIZACIONES + DATOS DEMO + MÁS + ADMIN. Botones rojos grandes (`#E30613`, `1.02rem` negrita, `padding .75rem 1rem`); activo con barra blanca + fondo oscuro. Secciones abiertas por defecto y `nav_to()` las reabre al cambiar de pestaña (acceso rápido). Sin `help=` en botones (los tooltips se quedaban pegados).
- Contadores de inicio (REQ-UI-06): ahora 3 `st.button` blancos (navegación interna, misma pestaña; antes los links `?page=` abrían pestaña externa). `?page=` sigue soportado como deep-link.
- Obligatorios con `*`: buscar (canal, foto, animal, tamaño, color, descripción) y publicar (tipo, animal, tamaño, contacto con al menos un dato: móvil/correo/RRSS, bloquea con aviso si falta). Seed: 9 avisos sin móvil reciben correo aleatorio + `SEED_VERSION` 4→5 (la app recarga sola); nuevo `tests/test_seed.py`.
- Specs: CU-01/CU-02/CU-03, REQ-05 esquema intacto, REQ-09.5, REQ-UI-02/03/04/06 + `architecture.md` §8 en v1.4 (root + `docs/`).
- Verificación: pytest 40/40, smoke 9 páginas OK, demo_check E2E OK (found_011 top-1 ≥80%).

## S66 — 24/09/2026 — Correcciones sidebar v1.5: bocadillos, plegados, secundarios negros (Muse Spark)
- Bocadillos restaurados (`help=` en los 11 botones de hero/sidebar): la queja era que se quedaban pegados, no que existieran. Fix con CSS `div[data-baseweb="tooltip"]{pointer-events:none}` para que desaparezcan al retirar el puntero (el tooltip ya no captura el ratón).
- Solo FUNCIONALIDADES abierta por defecto; puntualizaciones/demo/más/admin plegadas (`_SIDE_OPEN_DEFAULT`, `_toggle` con defecto por clave). Sin autodespliegue general: `nav_to()`/`ir_a_caso()`/`ir_a_publicar_con()` solo reabren `side_func` + `initial_sidebar_state="expanded"`.
- Secundarios (Publicar/Búsqueda/Protectoras/Tiempo) en negro `#23201B` + `margin-left 1.25rem` (tabulados, jerarquía); principales rojos grandes. Caption de conteo bajo "Animales perdidos activos" eliminado del todo (+ limpieza de `n_lost_total`/`n_lost_res` sin uso).
- Specs v1.5: REQ-UI-02/04 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 40/40, smoke 9 páginas OK, demo_check E2E OK.

## S67 — 24/09/2026 — Bocadillos que sí se van, todo tabulado, barra a todo ancho (Muse Spark)
- Causa raíz del pegado: mi CSS usaba `div[data-baseweb="tooltip"]`, que NO existe en el DOM de Streamlit 1.64 (verificado en el bundle: el tooltip vive en `Tooltip.J-aaVqsl.js` con `data-testid="stTooltipContent"`, y se reabre al pasar el puntero sobre él). Fix real: ese selector + `pointer-events:none` + auto-ocultado a los 4s (`huellas-tip-max`), así ni el peor caso queda pillado.
- Puntualizaciones: expanders Cómo puntúa/Aviso legal con `expanded=False` (ya no abren solos) y contenidos tabulados con columnas `[0.12, 0.88]`; demo con `demo_seed`/`demo_expire` (negros tabulados + `use_container_width`); admin entero tabulado igual (reindentado bajo `with _adm:`).
- Barra a todo ancho: `section[data-testid="stSidebar"] div.block-container` con `padding` lateral `0.5rem`.
- Specs v1.6: REQ-UI-02/04 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 40/40, smoke 9 páginas OK, demo_check E2E OK.

## S68 — 24/09/2026 — Sidebar a toda altura: botones principales estirados (Muse Spark)
- Aclaración del usuario con captura: no era solo ancho, sino alto — la columna lateral debe llegar hasta abajo a la altura de la página principal. Fix con flex CSS: el `stVerticalBlock` del sidebar es columna `flex` con `min-height:calc(100vh - 110px)`; los contenedores de los 6 botones principales pasan a `display:contents` (vía `:has(.st-key-…)`) y cada botón `flex:1 0 auto` con `min-height:3.4rem` (crecen, nunca encogen bajo su contenido). Secundarios y paneles conservan tamaño.
- Specs v1.7: REQ-UI-04 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 40/40, smoke 9 páginas OK. Pendiente confirmación visual del usuario (sin navegador aquí).

## S69 — 24/09/2026 — Revert estirado flex: botones altos naturales y juntos (Muse Spark)
- Al usuario no le gustó la estética estirada: revertido el bloque flex (`display:contents` + `flex:1`, `100vh`). En su lugar, principales más altos de forma natural (`padding .95rem 1rem`, `1.08rem`) y juntos (`gap 6px`), manteniendo todo el ancho.
- Specs v1.8: REQ-UI-04 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 40/40, smoke 9 páginas OK.

## S70 — 24/09/2026 — Restaurado autodespliegue al cambiar de pestaña (Muse Spark)
- `nav_to()`/`ir_a_caso()`/`ir_a_publicar_con()` vuelven a reabrir las 5 secciones (`side_func/punt/demo/mas/admin = True`) como en S65. Al abrir la app sigue arrancando solo FUNCIONALIDADES desplegada (defectos de render intactos).
- Specs v1.9: REQ-UI-02 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 40/40, smoke 9 páginas OK.

## S71 — 24/09/2026 — Revert S70 + auto-apertura del PANEL al cambiar de pestaña (Muse Spark)
- Malentendido mío: el usuario quería que se abra el PANEL lateral (no sus secciones) al cambiar de pestaña. Revertido S70 (`nav_to()` y cía. solo reabren `side_func`).
- Streamlit no expone API para desplegar el sidebar: expansor de un solo disparo vía `components.html` (iframe invisible) que pulsa `stSidebarCollapsedControl`, solo en el run donde cambia `page` (con `_side_prev_page`/`_side_nav_n` para remontar; otros reruns no lo tocan). Falla en silencio si el sandbox lo bloquea. Nuevo `tests/test_sidebar_panel.py`.
- Specs v1.10: REQ-UI-02 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 42/42, smoke 9 páginas OK.

## S72 — 24/09/2026 — Fix expansor: selector real `stExpandSidebarButton` (Muse Spark)
- El usuario reportó que no funcionaba: causa verificada en el bundle de Streamlit 1.64 — `stSidebarCollapsedControl`/`collapsedControl` NO existen en el DOM; el botón de apertura vive en el header con `data-testid="stExpandSidebarButton"` (icono `keyboard_double_arrow_right`). Snippet actualizado con ese selector primero + 2 fallbacks. Test ajustado.
- Verificación: pytest 42/42, smoke 9 páginas OK. Pendiente confirmación visual del usuario.

## S73 — 24/09/2026 — Abandonada auto-apertura del panel; limpieza final (Muse Spark)
- El usuario pidió parar. Se verifica con Playwright (msedge) y se documenta la causa real: en 1.64 `components.html` genera un iframe `stCustomComponentV1` con contenido vacío (el script nunca corre) y `st.html(unsafe_allow_javascript=True)` es despojado por DOMPurify cuando el script contiene `querySelector` con testids complejos (variantes simples sí ejecutan). Sin API de Streamlit para desplegar el sidebar → sin solución fiable sin hackear el DOM del framework.
- Limpieza: fuera el bloque expansor (JS + `_side_prev_page`) y marcadores de debug; `nav_to()`/`ir_a_caso()`/`ir_a_publicar_con()` solo reabren `side_func` (estado S66); `initial_sidebar_state="expanded"` se mantiene. `tests/test_sidebar_panel.py` actualizado (sin experimentos). Entorno local: servidores de prueba parados, playwright desinstalado.
- Specs v1.11: REQ-UI-02 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 40/40, smoke 9 páginas OK.

## S74 — 24/09/2026 — Fotos lost_001..005 nuevas + INICIO siempre negro (Muse Spark)
- Fotos de `data/seed/images/losts changes/` (`lost 001 -` → lost_001, etc.): copiadas a `data/seed/images/lost_00X.jpg/png` y `image_url` actualizado en los 5 JSON (resto de campos intacto; originales conservados en ambas carpetas). Centrado verificado: las 5 vistas una a una (animal entero y centrado) + thumbs 300×208 exactos generados con `make_carousel_thumb` (p. ej. retrato 1600×3352 y apaisada 520×516 → letterbox crema sin recortes; `imagen_cuadrada` también es letterbox). `SEED_VERSION` 5→6 (la app recarga sola).
- INICIO siempre negro: regla CSS propia (`#23201B`, mismo tamaño que los rojos, hover `#353026`) + fuera del `_NAV_ACTIVE_MAP` (ya no cambia al estar activo ni en otras pestañas). Resto del panel intacto.
- Verificación: pytest 42/42, smoke 9 páginas OK, demo_check E2E OK (found_011 top-1 ≥80%).

## S75 — 24/09/2026 — Tanda UI v1.12: mapa, títulos, barrido, huella y fuera bocadillos (Muse Spark)
- Mapa Buscar: `leyenda_mapa(mostrar_perdidos, mostrar_avist)` contextual (AVISTAMIENTOS, nunca ENCONTRADOS); sin elegir canal ya muestra avistamientos (`qtype="lost"` por defecto); chinchetas del canal con `pin_color()` (verdes/avistamientos, azules/perdidos); `render_mapa_avistados()` infiere la leyenda de los tipos visibles.
- Buscar: título ANÁLISIS PRELIMINAR DE SIMILITUDES RESPECTO AL REGISTRO + reenumeración 1. ¿Dónde buscas? · 2. Foto · 3. Zona · 4. Descripción · 5. Lanza.
- Títulos Publicar/Buscar con barrido rojo continuo (`.huellas-barrido`, `huellas-sweep 3.2s`); MASCOTAS DESAPARECIDAS / RASTROS COMPARTIDOS / VOLVIÓ A CASA en caja con huella roja de perímetro (`.huellas-perimetro`, `huellas-peri 6s`); renombres aplicados a subheaders + `stat_box` + infos; admin y seed unificados a Avistamientos.
- Fuera bocadillos: cero `help=` en app.py + CSS tooltip eliminada + `title=` fuera del carrusel (`ui_home.py`); `prefers-reduced-motion` cubre sweep/peri.
- Specs v1.12: `requirements.md` §15 (REQ-UI-07..12) + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 42/42, smoke 9 páginas OK, demo_check E2E OK (found_011 top-1 84.3% ≥80%).

## S76 — 24/09/2026 — Fixes v1.12: mapa con ambos lados + animaciones congeladas (Muse Spark)
- Mapa Buscar: el contextual escondía un lado (primero perdidos, luego avistamientos). Ahora el mapa de zona muestra AMBOS (dos `MarkerCluster`, leyenda completa TU CASO + PERDIDOS + AVISTAMIENTOS); el cruce sigue yendo solo contra el canal. Caption único.
- Causa raíz de las animaciones congeladas (barrido y huella se veían pero quietas): el `!important` de la base gana a los keyframes en la cascada CSS — el reloj avanzaba (`currentTime` 7.1s→12.3s) pero el estilo computado quedaba fijo. Fix: `background/background-size` (barrido) y `top/left` (huella) sin `!important`, con comentario de guarda en el CSS.
- Verificado en Edge headless con Playwright (capturas + estilos computados): huella `left` 282px→83px, barrido `background-position` 3.8%→98.5%. Servidor de pruebas parado y Playwright desinstalado tras verificar.
- Verificación: pytest 42/42, smoke 9 páginas OK, demo_check E2E OK.

## S77 — 25/09/2026 — Publicar con vida + cascada global v1.13 (Muse Spark)
- Cascada global (REQ-UI-13): hijas del bloque principal con fade-up 60 ms (`huellas-cascade`),
  una sola vez al montar; verificado en Edge headless (delays 0/.06/…/.36 s).
- Foto (REQ-UI-14): borde discontinuo rojo (`foto_pub`) + huella flotante + `vista_previa_scan()`
  (escaneo 1,5 s + "Foto analizada" con retardo).
- Confirmar (REQ-UI-15): pulso si completo; shake 400 ms + lista de faltantes si no
  (`faltantes_publicar()` pura en `ui_home.py` + remontaje `confirm_pub_{n}` + `st.rerun()`).
- Cruce (REQ-UI-16): "Cruzando con N avisos…" (dots + progreso, mín. 1,5 s real); match →
  tarjeta slide-in con anillo 0→real y dígitos 0→real (`steps`) + "Ver aviso y contactar";
  sin match → check dibujado + "Te avisaremos si aparece algo".
- Causa raíz del conteo en 0: `var()` en `counter-reset` cae a `none` en Chromium y con
  `inherits:false` el SVG no hereda (verificado por bisección); además animar el contenedor
  con `overflow:hidden` desplaza la ventana (pista interior `.huellas-track`). Fix: keyframes
  con valores FIJOS por tarjeta. Verificado en Edge: anillo 37.9px→16px, dígito final "84".
- Specs v1.13: `requirements.md` §16 + `architecture.md` §8 (root + `docs/`).
  Servidor de pruebas parado y Playwright desinstalado tras verificar.
- Verificación: pytest 49/49 (nuevo `tests/test_publicar_ui.py`), smoke 9 páginas OK,
  demo_check E2E OK (found_011 top-1 84.3% ≥80%).

## S78 — 25/09/2026 — Obligatorios, foto despejada y autocompletado v1.14 (Muse Spark)
- REQ-UI-17: color principal y descripción con `*` y validación real (`faltantes_publicar`
  con 2 args más; pulso/shake la respetan; tests actualizados + `short_addr`).
- REQ-UI-18: fuera huella flotante y caption "Sube una foto…"; uploader con
  `min-height:190px` ocupando el hueco.
- REQ-UI-19: autocompletado en Ubicación exacta (Publicar): `sugerir_direcciones()`
  (Nominatim, caché 1 h, 3+ letras, sesgo Jerez) + radio de sugerencias que centra el
  mapa; sin red no aparece nada y nada rompe.
- Specs v1.14: `requirements.md` §17 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 51/51, smoke 9 páginas OK, demo_check E2E OK.

## S79 — 25/09/2026 — Desplegable de sugerencias + etiqueta lateral v1.15 (Muse Spark)
- REQ-UI-20: sugerencias como lista emergente pegada al input (botones blancos
  `addr_sug_{i}` con chincheta CSS y hover rojo; `!important` estático frente al
  secundario oscuro). Límite honesto: Streamlit no emite por tecla, refrescan al
  confirmar el texto; sin JS.
- REQ-UI-21: "Foto analizada" a la derecha de la imagen (`.huellas-scanrow` flex).
- Specs v1.15: `requirements.md` §18 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 51/51, smoke 9 páginas OK, demo_check E2E OK.

## S80 — 25/09/2026 — Ajustes foto + revert sugerencias v1.16 (Muse Spark)
- REQ-UI-22: "Foto analizada" más grande (1rem) y centrada (`.huellas-scanbadge` flex
  con `align-self:stretch`); imagen a 300px + `margin-bottom` en la fila (aire con
  el cuadro inferior).
- REQ-UI-23: revert total del autocompletado a petición del alumno (fuera bloque,
  CSS `addr_sug_*`, `sugerir_direcciones()`, `short_addr()` y su test; ubicación
  como estaba: botón + mapa + manual). Cero restos verificado por grep.
- Specs v1.16: `requirements.md` §19 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 50/50, smoke 9 páginas OK, demo_check E2E OK.

## S81 — 25/09/2026 — Boli en el hueco + imagen admin v1.17 (Muse Spark)
- REQ-UI-24: `build_pen_html()` (trazos con `pathLength=100` + boli con wobble, en bucle)
  al final de la columna derecha de Publicar, solo con foto/precarga.
- REQ-UI-25: admin con `show_image(..., width=220)` + guarda CSS `max-width:100%` en
  imágenes del sidebar (el letterbox ya centra al animal entero).
- Specs v1.17: `requirements.md` §20 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 51/51, smoke 9 páginas OK, demo_check E2E OK.

## S84 — 25/09/2026 — Buscar con vida + Perdidos/Avistamientos v1.18 (Muse Spark)
- REQ-UI-26/27: foto con esquinas + "Foto lista"; círculo 2 km + chip de punto
  (pin con rebote, rotación incluida en keyframes, + anillo pulsante).
- REQ-UI-28: radar con barrido/pings (mín. 1,5 s) + shake con `faltantes_buscar()`.
- REQ-UI-29/30: resultados en cascada 80 ms (envoltorio con retardo inline) + anillo
  y 4 barras fijas + top con borde rojo y pulso; sin resultados → "Guardar como aviso"
  con rebote.
- REQ-UI-31..34: contacto bajo demanda (escapado, 300 ms), chips de urgencia/neutros
  y "Nuevo" (`dias_perdido()`/`es_nuevo()` puros).
- Verificado en Edge headless con el CSS real: barra 0.71, spin activo, delay 0.08s,
  borde top rojo; captura conforme. Playwright desinstalado tras verificar.
- Specs v1.18: `requirements.md` §21 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 58/58 (nuevo `tests/test_buscar_ui.py`), smoke 9 páginas OK,
  demo_check E2E OK.

## S86 — 25/09/2026 — Pulido Buscar/Publicar/Perdidos v1.19 (Muse Spark)
- REQ-UI-35: "Foto lista" lateral + flash verde en ambas (builder compartido).
- REQ-UI-36: seed con fechas 25/08–25/09 (semilla fija, pareja E2E intacta, SEED v7) y
  formato DD/MM/AA (`fmt_corta()`); la regeneración había pisado 9 contactos S65,
  recuperados de git al dict `CONTACTOS`.
- REQ-UI-37: leyenda + chinchetas en el mapa de Publicar.
- REQ-UI-38: fix del crash al clicar (`q_addr_pending` antes del widget) + cachés 30 d.
- REQ-UI-39: contacto con `<details>` (abre/cierra fluido sin rerun; verificado open
  18px y cierre en Edge; la lectura intermedia era tiempo virtual headless).
- Specs v1.19: `requirements.md` §22 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 59/59, smoke 9 páginas OK, demo_check E2E OK
  (found_011 top-1 84.3% ≥80%).

## S87 — 25/09/2026 — Insignia grande + destello + doble clic v1.20 (Muse Spark)
- REQ-UI-40/41: `badge_lateral_html()` (flecha con impulso + insignia 1.25rem con
  destello dentro); flash fuera de las fotos.
- REQ-UI-42: doble clic documentado en ambos mapas.
- Specs v1.20: `requirements.md` §23 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 59/59, smoke 9 páginas OK, demo_check E2E OK.

## S88 — 25/09/2026 — Misma pestaña, atrás, fechas admin e insignia XL v1.21 (Muse Spark)
- REQ-UI-43: `target="_self"` en carrusel y contadores (si el navegador lo respeta,
  misma pestaña; si no, el deep-link igual aterriza en el aviso).
- REQ-UI-44: `?s=` por navegación + `sync_page_from_url()` (sustituye a
  `handle_counts_click()`; `?page=` migra solo; `?aviso=` no interfiere vía flag).
  Honesto: el atrás funciona si el navegador reacciona al historial; si no, todo
  queda igual que antes (sin regresión posible: la sesión manda en empates).
- REQ-UI-45: admin edita fechas ISO (valida `validate_aviso`, con traza en el log).
- REQ-UI-46: insignia 1.6rem + flecha 110px.
- Specs v1.21: `requirements.md` §24 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 59/59, smoke 9 páginas OK, demo_check E2E OK.

## S89 — 25/09/2026 — Foto centrada, atrás honesto y reencuentros v1.22 (Muse Spark)
- REQ-UI-47/48: foto centrada sin insignia; caption corto.
- REQ-UI-49: verificado por el alumno que el atrás no recorre (URL sí registra):
  `?s=` queda como deep-link; documentado el límite sin regresión.
- REQ-UI-50..55: reencuentros en ES, shake, revisión 1,5 s, fiesta (timeline+sello+
  lluvia), tarjetas cerradas con días y corazón, vacío con corazón.
  Regla de terminal del alumno guardada: jamás `streamlit run`/`Start-Process`;
  solo HTTP o Playwright contra el 8587 (aquí inalcanzable: sondas con file://).
- Specs v1.22: `requirements.md` §25 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 60/60, smoke 9 páginas OK, demo_check E2E OK.

## S90 — 25/09/2026 — Reencuentros visibles + cerrados en fila v1.23 (Muse Spark)
- REQ-UI-56: miniaturas de elegidos bajo multiselects (límite hover documentado).
- REQ-UI-57: tarjeta con marca/pie en cerrados y en revisión; "Resuelve X" dentro
  (márgenes coherentes); nota vacía con placeholder.
- REQ-UI-58: cerrados de 3 en 3 por fila.
- Aclarado al alumno: la tarjeta S89 solo salía en validados; ahora ambos estados
  la usan y se ve desde el primer aviso en revisión.
- Specs v1.23: `requirements.md` §26 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 60/60, smoke 9 páginas OK, demo_check E2E OK.

## S91 — 25/09/2026 — Casos con lluvia/ruleta + nota v1.24 (Muse Spark)
- REQ-UI-59/60/61: lluvia (8 corazones) vs ruleta por estado, tarjeta translúcida,
  nota bajo especie·color (parámetro `nota` + `estado` en el builder).
- Visión: verificado con datos que NO hay azar — seed intacto, CLIP local, top-1
  correctos en ambos espacios (lost_001→found_011 84.3/71.1%, lost_003→found_003).
  Lo de `marr�n` era artefacto del comparador, no del seed.
- Specs v1.24: `requirements.md` §27 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 60/60, smoke 9 páginas OK, demo_check E2E OK.

## S93 — 25/09/2026 — Admin fluida + reencuentros + 3 demo + carrusel v1.25 (Muse Spark)
- REQ-UI-62/63: `show_image(fluido=True)` + guarda CSS; gestor con filtro por estado,
  validar/rechazar/eliminar con confirmación (`delete_reencuentro()` + test + log).
- REQ-UI-64: siamés→`lost_007` (colisión con `lost_006` resuelto, avisado al alumno),
  `found_012/013`; SEED v8 + `embeddings.json` con 20 CLIP; conteos a 19 activos.
- REQ-UI-65: `extra={id: revision|cerrado}` en carrusel (resueltos incluidos) con
  segunda etiqueta ámbar/verde.
- Aclarado lo "aleatorio": sin azar en código (seed intacto, CLIP, top-1 OK).
- Specs v1.25: `requirements.md` §28 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 62/62, smoke 9 páginas OK, demo_check E2E OK.

## S94 — 25/09/2026 — Inicio vivo + expiración anual + lost_006 v1.26 (Muse Spark)
- REQ-UI-66/67: velo rojo en contadores (`::after`, evita el `!important` de la base)
  y pulso de escala en CTAs (fuera el anillo).
- REQ-UI-68: `expire_old(365)` + botón anual; `lost_006` a active + SEED v9
  (20 activos: 7 + 13); CU-05 y decisión 11 actualizadas.
- REQ-UI-69/70: etiqueta en bloque; gestor de reencuentros arriba del admin
  (estaba tras 20 tarjetas: invisible sin scroll).
- Specs v1.26: `requirements.md` §29 + CU-05 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 62/62, smoke 9 páginas OK, demo_check E2E OK.

## S95 — 25/09/2026 — Velo visible + reencuentro completo v1.27 (Muse Spark)
- REQ-UI-71: el velo era invisible por `opacity:0 !important` en la base (S76
  repetido); auditoría de todas las animaciones sin más casos; verificado en
  Edge (opacidad 0.15→0.59).
- REQ-UI-72: "Empezar de cero" + limpieza tras publicar + previews + par lado a
  lado + doble foto en tarjetas + 20 corazones (verificado doble 220px).
- Specs v1.27: `requirements.md` §30 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 62/62, smoke 9 páginas OK, demo_check E2E OK.

## S96 — 25/09/2026 — Remates casos y contadores v1.28 (Muse Spark)
- REQ-UI-73/74/75/76: revisión sin contenedor extra; fuera el par lateral del
  formulario; lluvia uniforme; contadores negros/negrita/96px.
- Specs v1.28: `requirements.md` §31 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 62/62, smoke 9 páginas OK, demo_check E2E OK.

## S97 — 25/09/2026 — Sin Datos demo v1.29 (Muse Spark)
- REQ-UI-77: fuera botón + seed + expirar con su CSS (sidebar de 5); la demo
  auto-carga al arrancar; limpiar = avisar (elegido por el alumno frente al
  quita-y-pon irreversible).
- Specs v1.29: `requirements.md` §32 + REQ-UI-02 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 62/62, smoke 9 páginas OK, demo_check E2E OK.

## S98 — 25/09/2026 — Mapas frescos, contadores y limpieza real v1.30 (Muse Spark)
- REQ-UI-78: `huella_mapa()` en las 3 claves (st_folium con clave fija reutilizaba
  el iframe con chinchetas viejas).
- REQ-UI-79/80: contadores chicos (negro/negrita intactos); 36 corazones uniformes.
- REQ-UI-81: causa del limpiar roto (uploader ignora el borrado; selects+texto sí
  se limpiaban — reproducido con AppTest) + rotación de clave en reencuentro y
  publicar + `tests/test_limpiar.py`.
- Specs v1.30: `requirements.md` §33 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 63/63, smoke 9 páginas OK, demo_check E2E OK.

## S99 — 25/09/2026 — Limpieza total por época v1.31 (Muse Spark)
- Causa del limpiar roto: en navegador real el frontal restaura valores borrados
  (AppTest no lo reproduce); solo rotar claves lo evita. Época en Publicar
  (15 claves + prefill) y Reencuentro (4 claves).
- Specs v1.31: `requirements.md` §34 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 63/63, smoke 9 páginas OK, demo_check E2E OK.

## S100 — 25/09/2026 — Sidebar uniforme + MÁS desplegable v1.32 (Muse Spark)
- REQ-UI-83: fuera columnas 0.12/0.88 en puntualizaciones (mismo ancho que el resto).
- REQ-UI-84: protectoras/tiempo como expanders compactos en el sidebar (las páginas
  grandes quedan como fallback por deep-link).
- De paso: `pub_size` también con época (era la única clave del formulario sin rotar).
- Aclarado: las capturas del alumno eran v1.30 (foto rota pero campos no = previo a
  la época v1.31); retest con Ctrl+F5 tras redesplegar.
- Specs v1.32: `requirements.md` §35 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 63/63, smoke 9 páginas OK.

## S101 — 25/09/2026 — Sidebar igualado + leyenda con conteos v1.33 (Muse Spark)
- REQ-UI-85/86: claves en los 4 expanders + tabulación; perrito sin `<style>` con
  CSS global (verificado salto activo); páginas grandes como fallback.
- REQ-UI-87: `build_leyenda_html()` con conteos (test) y llamadas con `len()`.
  Aclarado: los clusters agrupan chinchetas solapadas (clic para desplegar).
- Falsa alarma instructiva: buscaba `.perro-salto` con punto (es keyframes, sin
  punto); el CSS estaba bien.
- Specs v1.33: `requirements.md` §36 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 64/64, smoke 9 páginas OK, demo_check E2E OK.

## S102 — 25/09/2026 — Sidebar rematado + pie admin v1.34 (Muse Spark)
- REQ-UI-88/89: selector de Publicar restaurado (una edición lo había roto);
  puntúa compacto.
- REQ-UI-90: MÁS inline con contraste + perrito por iframe (el markdown escapaba
  el SVG a texto; revertido el experimento sin `<style>`).
- REQ-UI-91: métricas (7 días + urgentes), badge verde y redes/donar tras divisor.
- Specs v1.34: `requirements.md` §37 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 64/64, smoke 9 páginas OK, demo_check E2E OK.

## S103 — 25/09/2026 — Contraste MÁS + puntúa vertical + pie visible v1.35 (Muse Spark)
- REQ-UI-92: expansores MÁS en claro con selectores al widget (la versión por
  bloques fugaba a la cabecera); el alumno aclaró que eran Protectoras/Tiempo.
- REQ-UI-93/94: puntúa en 1 columna; pie de admin tras el login.
- Specs v1.35: `requirements.md` §38 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 64/64, smoke 9 páginas OK, demo_check E2E OK.

## S104 — 25/09/2026 — MÁS en negro + pie en sidebar v1.36 (Muse Spark)
- REQ-UI-95: revertido el experimento en claro (negro + blanco como secundarios).
- REQ-UI-96: métricas/soporte a nivel de sidebar tras ADMINISTRACIÓN (el pie tras
  login quedaba enterrado; el alumno lo quiere siempre visible).
- Specs v1.36: `requirements.md` §39 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 64/64, smoke 9 páginas OK, demo_check E2E OK.

## S105 — 25/09/2026 — Líneas alternas + pie centrado v1.37 (Muse Spark)
- REQ-UI-97/98: `build_alt_list()` blanco/rojo + enlaces legibles; pie centrado con
  segundo divisor y un solo enlace paypal.
- Specs v1.37: `requirements.md` §40 + `architecture.md` §8 (root + `docs/`).
- Verificación: pytest 65/65, smoke 9 páginas OK, demo_check E2E OK.

## S106 — 25/09/2026 — Badge contenido + soporte URL v1.38 (Muse Spark)
- REQ-UI-99: badge pequeño con aire + CONTACTO/https rojos clicables.
- Specs v1.38: `requirements.md` + `architecture.md` §8 (root + `docs/`).
- Verificación: smoke 9 páginas OK.

## S107 — 25/09/2026 — Métricas compactas + URLs que parten v1.39 (Muse Spark)
- REQ-UI-100: `stat_side()` compacto (las mini genéricas tapaban el título) y
  `.huellas-sup` con `break-all` (las https largas se solapaban).
- Specs v1.39: `requirements.md` + `architecture.md` §8 (root + `docs/`).
- Verificación: smoke 9 páginas OK.

## S85 — 25/09/2026 — Fix ImportError atascado en Cloud (Muse Spark)
- Causa raíz (2ª vez): el pull de Cloud actualiza ficheros sin reiniciar el proceso;
  el autoreload re-ejecuta `app.py` nuevo con `ui_home` cacheado viejo y el ImportError
  no se cura hasta el reboot. Fix: `importlib.reload(_uh)` antes del `from ui_home
  import` (con `try/except`, autocura en segundos).
- Simulado en local: módulo viejo cacheado + fichero nuevo → sin reload falla,
  con reload importa OK. Repo intacto tras la simulación (solo `M app.py`).
- Verificación: syntax OK, pytest 58/58, smoke 9 páginas OK, demo_check E2E OK.

## S82 — 25/09/2026 — Boli alto y translúcido (Muse Spark)
- Boli en formato alto (`min-height:240px`, SVG 300×150 con trazos repartidos) y fondo
  translúcido (`rgba(255,255,255,0.45)`, se ve el patrón de la web).
- Verificación: pytest 9/9 (UI) + smoke 9 páginas OK.

## S83 — 25/09/2026 — Boli sin marco (Muse Spark)
- Fuera el borde punteado de `.huellas-penwrap` (`border:none`): sin marco.
- Verificación: smoke 9 páginas OK.

## S109 — 25/09/2026 — Scan lado a lado + métricas frescas al publicar (Muse Spark)
- La insignia FOTO ANALIZADA envolvía debajo de la foto en la columna estrecha de Publicar: `.huellas-scanrow` ahora `flex-wrap:nowrap` con foto flexible (máx. 240px), flecha corta (56px) e insignia compacta (implementa REQ-UI-21).
- Las métricas (sidebar/inicio) se calculaban antes del alta y quedaban viejas tras publicar: ahora se guarda `pub_result`, se rota `pub_epoch` (formulario limpio, sin doble envío) y `st.rerun()`; el banner repite el resultado del cruce (éxito/tarjeta/Ver aviso o check/info) con descarte "Publicar otro aviso".
- Verificación: pytest (incl. `test_publicar_scan.py` 3/3) + smoke 9 páginas OK.

## S108 — 25/09/2026 — Matching v1.40: visual manda + puerta foto idéntica (Muse Spark)
- Queja del alumno con pantallazos: misma foto daba 73% (visual 100% pero texto 23% vetaba la alerta) y distintos perros daban visual alta (histograma de colores en Cloud, no identidad).
- Pesos (decisión alumno): 0.55 visual + 0.25 texto + 0.10 temporal + 0.10 geo (`matcher.py`, spec §8 v1.40, `architecture.md` x2, `README.md`, sidebar). Descartado 0.60 visual: medido, la demo E2E caía a 0.798 <0.80.
- Puerta visual: `visual>=0.95` también notifica/lista (`UMBRAL_GATE_VISUAL`, spec §9 v1.40); `notifier.py` respeta la bandera `m["notifica"]` (fuente única en Matcher).
- Texto frágil: `normalizar_txt()` (tildes/mayúsculas/espacios) + `COLOR_ALIAS` mínimos (café/canela/chocolate→marrón…) en `similitud_estructurada`.
- Specs v1.40: `requirements.md` §8/§9 + §7.5 (`docs/`).
- Verificación: pytest 71/71, demo_check E2E OK (found_011 top-1 80.8% ≥80%, found_001 72.4% ≥65%).

## S110 — 25/09/2026 — Desfile lateral tras Soporte (Muse Spark)
- Tras la divisoria negra bajo el PayPal del sidebar: tira de gatitos y perritos (SVG negro/rojo) trotando en fila, bucle infinito sin salto (`build_marcha_html()` + `.huellas-track`/`.huellas-trote`, respeta `prefers-reduced-motion`).
- Verificación: `test_sidebar_marcha.py` 2/2 + smoke 9 páginas OK.
- Fix: pista x3 (24 figuras, mitades idénticas) para que no se vacíe ningún lado + dirección `-50%→0` (avanzan hacia donde miran).
- Siluetas estilo B "Corre" elegidas por el alumno (hoja siluetas.html con 4 estilos): zancada extendida.
- Cambio a estilo C "Chibi" (cabezón sentado) + tira más rápida (12s→7s).
- Fix tirones: la tira de dígitos pisaba `.huellas-track` con `display:block`; reglas acotadas a `.huellas-march` + velocidad 4s + `will-change:transform`.
- Segunda tira invertida (`invertida=True`): espejada y en sentido contrario, mismos parámetros.

## S111 — 25/09/2026 — Botón rojo ⏪ a Inicio junto a títulos (Muse Spark)
- `titulo_barrido`/`titulo_perimetro` (los 5 títulos de sección) llevan al lado botón rojo con icono rewind blanco (`:material/fast_rewind:`, clave `home_*`) que redirige a Inicio vía `nav_to`.
- Verificación: `test_titulo_home.py` 2/2 (botón en las 5 páginas + navega) + smoke implícito.

## S112 — 25/09/2026 — Botón inicio a la izquierda y pegado + ajuste fino (Muse Spark)
- Botón a la izquierda del título (columnas 1:30, hueco pequeño, centrado vertical) + compacto.
- Alineación por prueba visual: barrido perfecto con 1px; viñetas en caja con clave propia `homebox_*` y `top:4px` (el padding se recentraba a la mitad; el diagnóstico temporal de 8px confirmó que el deploy llegaba).
- Verificación: `test_titulo_home.py` 3/3.

## S118 — 26/09/2026 — Títulos pegados al botón solo en escritorio (Muse Spark)
- En PC el hueco mediano quedaba excesivo: `column-gap:0.5rem` solo en `@media (min-width:641px)` para filas con botón home. Móvil intacto (prohibido tocarlo sin petición expresa).
- Verificación: `test_titulo_home.py` 4/4.

## S113 — 25/09/2026 — Auditoría final (Gemini/Claude/ChatGPT) + higiene (Muse Spark)
- **Admin**: fuera `DEFAULT_ADMIN_PASSWORD` ("huellas123") del código, README y specs (REQ-11.1 v1.40); sin `ADMIN_PASSWORD` (Secrets) ni `HUELLAS_ADMIN_PASSWORD` (env), la administración queda desactivada con aviso. `.streamlit/secrets.toml` local creado (gitignored) para no perder el flujo local.
- **requirements.txt**: versiones fijadas (numpy 2.5.3, pillow 12.3.0, scikit-learn 1.9.1, pytest 9.1.1; streamlit/folium ya estaban ==).
- **.gitignore**: + `data/admin.log`, `.env*`, `.pytest_cache/`, `.engram/`.
- **README**: título HUELLAS, enlace demo huellas.streamlit.app, 81 tests, demo_check actualizado (found_011 80.8%), sección "Limitaciones conocidas" (visión Cloud = histograma, datos efímeros en Cloud), fuera "Se añadirá el enlace" y contraseña.
- **Specs**: cabecera "Estado v1.40" + guía de lectura (REQ-UI cronológicos, reversiones en PROMPT-LOG); `requirements.md` root sincronizado con docs/ (faltaban los pesos v1.40 del §8); mermaid architecture: 0.55/0.25/0.10/0.10 y "notify >=80 o visual>=95" (root+docs).
- **Móvil**: media query ≤480px para la fila foto+insignia del escaneo.
- Nota: `App.py` no existe como archivo distinto (NTFS case-insensitive; git solo lleva `app.py`). INFORME.md (del alumno) mantiene datos históricos — no se toca por decisión.
- Verificación: pytest 81/81, smoke 9 páginas, demo_check E2E, eval_match OK.

## S115 — 26/09/2026 — Fix móvil carrusel táctil, solo (Muse Spark)
- El lote S114 se revirtió entero porque los otros dos fixes (imágenes, scroll lateral) empeoraron el móvil; el del carrusel sí estaba bien y se reaplica aislado.
- Pausa `:hover` del carrusel solo en `@media (hover:hover) and (pointer:fine)` + `touch-action:pan-y`: en táctil el toque dejaba el hover "enganchado" y lo trababa.
- Verificación: `test_movil.py` 1/1.

## S116 — 26/09/2026 — Fichas sin deriva lateral en Perdidos/Avistamientos (Muse Spark)
- Esas dos páginas se podían mover en horizontal en el móvil: la foto fija de 380px desbordaba la columna estrecha. Primer intento con CSS global (`FICHA_IMG_STYLE` + `min-width:0`) colapsó filtros y descripciones: revertido; header, filtros y descripciones intactos.
- Fix definitivo en Python: las fichas usan `show_image(..., fluido=True)` (ocupa el ancho de la columna, sin desbordar). Nada de CSS global.
- Verificación: `test_movil.py` 2/2 (ambas páginas renderizan sin excepción).

## S117 — 26/09/2026 — Botón inicio al lado del título en móvil (Muse Spark)
- En pantallas estrechas Streamlit apila las columnas y el botón caía ENCIMA del título. Solo en cabeceras con botón home se fuerza fila (`flex-direction:row` + `nowrap` vía `:has()`) y la columna del botón se ajusta a su contenido (`flex:0 0 auto`). Escritorio intacto.
- Verificación: `test_movil.py` 3/3.

## S119 — 26/09/2026 — Vista fija en Perdidos/Avistamientos móvil (Muse Spark)
- Esas dos páginas "bailaban" a los lados en móvil. `VISTA_FIJA_STYLE` recorta el desborde lateral del contenedor, emitido SOLO en esas dos páginas y SOLO bajo 640px (escritorio y resto de páginas intactos; sin `min-width:0` global esta vez).
- Verificación: `test_movil.py` 4/4 (incluye que inicio/buscar/publicar/reencuentro NO reciben el estilo).

## S133 — 26/09/2026 — Sidebar compacto al 85% (Muse Spark)
- Todo el contenido lateral reducido en proporción (`zoom:0.85` solo en el sidebar), ocupando igual el ancho.
- Verificación: `test_sidebar_marcha.py` 5/5.

## S120 — 26/09/2026 — Etiquetas del carrusel sin subrayado (Muse Spark)
- Perdido/avistado/en revisión/caso cerrado mostraban la línea azul del enlace: `.huellas-cd-link .huellas-cd-et` sin `text-decoration`, `border-bottom` ni `box-shadow`. El resto de textos subrayados, intactos.
- Verificación: `test_carousel.py` 8/8.

## S124 — 26/09/2026 — Subtítulo en tira hacia la derecha (Muse Spark)
- "Mira quién te está esperando…" avanza a la derecha, sale y vuelve a entrar en bucle sin salto (pista duplicada, 12s) + congelado con `prefers-reduced-motion`.
- Verificación: `test_carousel.py` 10/10.

## S134 — 26/09/2026 — Contenido pegado a la tira en inicio (Muse Spark)
- Hueco entre bloques a 0.25rem + colapsado el hueco fantasma del subtítulo desplazado (`margin-bottom:-1rem`).

## S126 — 26/09/2026 — Tira con entrada rápida y crucero intacto (Muse Spark)
- Tramos desiguales (0→20% entra, 20→100% cruza): la entrada es 4x más rápida y el viaje no se acelera.

## S128 — 26/09/2026 — Tira de una copia con entrada suavizada (Muse Spark)
- La opción solapada volvía a mostrar el texto duplicado (rechazado en S125: solape sin hueco y copia única son incompatibles). De vuelta a una copia con `ease-out` en la entrada: enlaza suave con el crucero y se acabó el tirón.

## S131 — 26/09/2026 — Tira sin microatascos sin tocar tiempos (Muse Spark)
- `contain:layout` en la tira: el navegador recalcula solo la tira por fotograma en vez de la página entera. Tiempos de entrada/salida intactos.

## S127 — 26/09/2026 — Tira solapada sin tirones (Muse Spark)
- Dos copias idénticas a velocidad constante: sale por un borde mientras entra por el otro (el tirón del cambio de tramo desaparece).

## S125 — 26/09/2026 — Tira de subtítulo de una sola pasada (Muse Spark)
- Sin texto duplicado: una copia cruza todo el ancho (sale cortada por la derecha, vuelve por la izquierda) a 8s.
