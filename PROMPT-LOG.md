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
