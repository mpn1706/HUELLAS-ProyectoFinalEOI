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
