# MascotasLost&Found — HUELLAS

Sistema de búsqueda y comparativa visual de animales perdidos/encontrados (Jerez de la Frontera).
Proyecto final del curso de IA Generativa y Vibe Coding (EOI) — MVP funcional con metodología **Spec-Driven Development**.

> El sistema **nunca afirma "es el mismo animal"**. Solo muestra **posibles coincidencias** con porcentaje y desglose de señales. Aviso legal único en el sidebar: *"Este análisis no promete una coincidencia inequívoca respecto al animal buscado. Una imagen no permite confirmar la identidad, verifique en persona."*

## Problema que resuelve

Cuando una mascota se pierde, los avisos de "perdido" y "encontrado" quedan dispersos en redes sociales y protectoras, sin forma de cruzarlos automáticamente. Esta app centraliza avisos y sugiere candidatos basándose en **imagen, descripción, ubicación y fecha**.

## Funcionalidades (MVP)

- Registrar avisos `lost` / `found` con foto + texto libre + ubicación (mapa Leaflet clicable) + fechas (cualquier animal doméstico: `dog | cat | other`).
- **5 agentes**: Ingestor (normaliza) → Vision Analyst (atributos + embedding CLIP 512) → Matcher (score) + Geo (haversine, radio 15 km) → Notifier (panel + log si `>=80%`).
- **RAG textual**: retrieval sobre descripciones (`70%` campos estructurados + `30%` MiniLM multilingüe), filtrado `active` y tipo opuesto.
- Ranking explicable con las 4 sub-señales + mapa Folium + detalle lado a lado.
- **Automatización**: al registrar o buscar, si un candidato supera el 80% se genera notificación (tabla `notifications` + `data/notifications.log`); botón "Expirar avisos >30 días" (`expire_old()`, sin cron).
- **Administración** (sidebar, CU-06): un único admin con contraseña elimina duplicados/vandalismo (con confirmación) o marca resueltos; todo queda en `data/admin.log`. Contraseña: Secrets `ADMIN_PASSWORD` en Cloud, o variable `HUELLAS_ADMIN_PASSWORD`, o defecto local `huellas123`.
- Las alertas no se duplican: un par (aviso, candidato) genera una sola fila (se actualiza si cambia el score).

## Fotos reales del seed

1. Consigue JPG propias o de licencia libre (no valen fotos ajenas de redes), ≤800px y <500KB, nombradas por aviso (`found_001.jpg`…) en `data/seed/images/`, y apunta `image_url` en su JSON.
2. `pip install torch --index-url https://download.pytorch.org/whl/cpu` + `pip install transformers pillow` (solo local).
3. `python scripts/compute_embeddings.py` → genera `data/seed/embeddings.json` (vectores CLIP reales, viajan en git; Cloud los usa sin torch).
4. Commit de imágenes + JSONs + `embeddings.json`.
- Corpus demo propio de **20 avisos de Jerez con fotos reales** (7 lost + 13 found, 19 activos + 1 resuelto demo), sin scraping (fuera de alcance por decisión de diseño).

### Fórmula (cerrada, `requirements.md` §8)

```
score = 0.40·visual + 0.30·texto + 0.20·temporal + 0.10·geo
geo   = max(0, 1 - km/15) · texto = 0.70·estructurado + 0.30·semántico
temp  = max(0, 1 - días/30), fecha = last_seen si existe si no reported
```
Umbrales: `>=80%` notifica + destaca · `>=65%` lista · `<65%` solo indexa.

## Stack

Python 3.11+ · Streamlit (+ streamlit-folium) · SQLite (`data/huellas.db`, cero setup) · numpy + scikit-learn · CLIP `openai/clip-vit-base-patch32` (512-dim) y MiniLM `paraphrase-multilingual-MiniLM-L12-v2` con **fallback local** (TF-IDF/Jaccard + hash) para ejecutar sin GPU ni claves. Solo español.

## Cómo ejecutarlo (profesor, <10 min)

```bash
pip install -r requirements.txt
python scripts/make_seed.py      # genera data/seed (20 avisos + imágenes)
python scripts/load_seed.py      # carga SQLite data/huellas.db
streamlit run app.py             # abre la app en el navegador
```

Verificación extra:

```bash
python -m pytest tests -q          # 13 tests (fórmula, umbrales, geo, ingestor)
python scripts/eval_match.py       # ÉXITO-01/03 con vectores fijos
python scripts/demo_check.py       # E2E: lost_001 → found_001 top-1 (96.3%)
```

## Despliegue

- Local (evaluación oficial): `streamlit run app.py` — ver instrucciones arriba.
- Nube: Streamlit Community Cloud sobre este repo, rama `main`, fichero `app.py`. La app **auto-carga el seed de Jerez** si la DB está vacía (el filesystem cloud es efímero y `data/huellas.db` no viaja en git): cero comandos tras el deploy. Se añadirá el enlace aquí al desplegar.

## Estructura

```
app.py  agents/{ingestor,vision,matcher,geo,notifier,db}.py
rag/{embeddings,retrieval}.py  data/seed/{lost,found,images}/
scripts/{make_seed,load_seed,eval_match,demo_check}.py  tests/
requirements.md  architecture.md  PROMPT-LOG.md
```

Specs (`requirements.md` v1.0, `architecture.md`) son la fuente de verdad: cada commit referencia su sección (`[REQ-…]`). Proceso con IA en `PROMPT-LOG.md`.
