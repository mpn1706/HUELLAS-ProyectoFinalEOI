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
