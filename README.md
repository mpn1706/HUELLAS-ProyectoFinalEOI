# HUELLAS — Agente de Búsqueda y Comparativa Visual de Animales Perdidos

Sistema de búsqueda y comparativa visual de animales perdidos/encontrados (Jerez de la Frontera).
Proyecto final del curso de IA Generativa y Vibe Coding (EOI) — MVP funcional con metodología **Spec-Driven Development**.

> **Demo en vivo: <https://huellas.streamlit.app>** (rama `main` de este repo).

> El sistema **nunca afirma "es el mismo animal"**. Solo muestra **posibles coincidencias** con porcentaje y desglose de señales. Aviso legal único en el sidebar: *"Este análisis no promete una coincidencia inequívoca respecto al animal buscado. Una imagen no permite confirmar la identidad, verifique en persona."*

## Problema que resuelve

Cuando una mascota se pierde, los avisos de "perdido" y "encontrado" quedan dispersos en redes sociales y protectoras, sin forma de cruzarlos automáticamente. Esta app centraliza avisos y sugiere candidatos basándose en **imagen, descripción, ubicación y fecha**.

## Funcionalidades (MVP)

- Registrar avisos `lost` / `found` con foto + texto libre + ubicación (mapa Leaflet clicable) + fechas (cualquier animal doméstico: `dog | cat | other`).
- **5 agentes**: Ingestor (normaliza) → Vision Analyst (atributos + embedding CLIP 512) → Matcher (score) + Geo (haversine, radio 15 km) → Notifier (panel + log si `>=80%`).
- **RAG textual**: retrieval sobre descripciones (`70%` campos estructurados + `30%` MiniLM multilingüe), filtrado `active` y tipo opuesto.
- Ranking explicable con las 4 sub-señales + mapa Folium + detalle lado a lado.
- **Automatización**: al registrar o buscar, si un candidato supera el 80% se genera notificación (tabla `notifications` + `data/notifications.log`); botón "Expirar avisos de más de 1 año" (`expire_old()`, sin cron).
- **Administración** (sidebar, CU-06): un único admin con contraseña elimina duplicados/vandalismo (con confirmación) o marca resueltos; todo queda en `data/admin.log`. La contraseña se configura en Secrets `ADMIN_PASSWORD` (Cloud) o en la variable `HUELLAS_ADMIN_PASSWORD` (local, p. ej. vía `.streamlit/secrets.toml`, que no viaja a git). **Sin contraseña configurada, la administración queda desactivada** (no existe contraseña por defecto en el código).
- Las alertas no se duplican: un par (aviso, candidato) genera una sola fila (se actualiza si cambia el score).

## Fotos del seed

1. Entre ≤800px y <500KB, nombradas por aviso (found_001.jpg, lost_001.jpg, …) en `data/seed/images/`, y apunta `image_url` en su JSON.

2. `pip install torch --index-url https://download.pytorch.org/whl/cpu` + `pip install transformers pillow` (solo local).

3. `python scripts/compute_embeddings.py` → genera `data/seed/embeddings.json` (vectores CLIP reales, viajan en git).

4. Commit de imágenes + JSONs + `embeddings.json`.

• Corpus demo propio de **20 avisos de Jerez con fotos reales** (7 lost + 13 found, todos activos), sin scraping (fuera de alcance por decisión de diseño).

### Fórmula (cerrada, `requirements.md` §8)

```
score = 0.55·visual + 0.25·texto + 0.10·temporal + 0.10·geo
geo   = max(0, 1 - km/15) · texto = 0.70·estructurado + 0.30·semántico
temp  = max(0, 1 - días/30), fecha = last_seen si existe si no reported
```
Umbrales: `>=80%` notifica + destaca · `visual>=95%` también notifica (misma foto) · `>=65%` lista · `<65%` solo indexa.
Color/marcas se comparan sin tildes ni mayúsculas (Marrón=marron, Café=marrón).

## Stack

Python 3.11+ · Streamlit (+ streamlit-folium) · SQLite (`data/huellas.db`, cero setup) · numpy + scikit-learn · CLIP `openai/clip-vit-base-patch32` (512-dim) y MiniLM `paraphrase-multilingual-MiniLM-L12-v2` con **fallback local** (TF-IDF/Jaccard + histograma) para ejecutar sin GPU ni claves. Solo español.

## Cómo ejecutarlo (profesor, <10 min)

```bash
pip install -r requirements.txt
python scripts/make_seed.py      # genera data/seed (20 avisos + imágenes)
python scripts/load_seed.py      # carga SQLite data/huellas.db
streamlit run app.py             # abre la app en el navegador
```

Verificación extra:

```bash
python -m pytest tests -q          # 81 tests (fórmula, umbrales, geo, ingestor, UI…)
python scripts/eval_match.py       # ÉXITO-01/03 con vectores fijos
python scripts/demo_check.py       # E2E: lost_001 → found_011 top-1 ≥80% (alerta real)
python scripts/smoke_app.py        # 9 páginas sin excepciones (headless)
```

## Despliegue

- Local: `streamlit run app.py` — ver instrucciones arriba.
- Nube: **<https://huellas.streamlit.app>** — Streamlit Community Cloud sobre este repo, rama `main`, fichero `app.py`. La app **auto-carga el seed de Jerez** si la DB está vacía (el filesystem cloud es efímero y `data/huellas.db` no viaja en git): cero comandos tras el deploy.

### Limitaciones conocidas (importante para la demo en vivo)

- **Visión en Cloud**: sin `torch`, la similitud visual usa un **histograma de color** (8×8×8) calculado en ambos lados (query y candidatos en el MISMO espacio, S49). `embeddings.json` (CLIP) solo se usa en local con `torch` instalado. Consecuencia: en Cloud la señal visual discrimina menos (misma paleta = score alto aunque sean animales distintos); en local con CLIP la comparación es mucho más fina.
- **Datos efímeros en Cloud**: los avisos publicados en la demo desplegada se pierden al reiniciar/dormir la app (SQLite vive en el filesystem temporal). El corpus permanente es el seed. Para persistencia real haría falta una BD externa (p. ej. Supabase/Turso).
- **Privacidad**: el contacto se muestra tras el desplegable "Ver contacto" (no en abierto); la ubicación se muestra a nivel de calle/zona.
- **Administración en Cloud**: requiere configurar el secret `ADMIN_PASSWORD` en el panel de Secrets de la app; si no, el apartado queda desactivado.

## Estructura del proyecto

```
HUELLAS-ProyectoFinalEOI/
├── app.py # app Streamlit (UI + páginas + CSS)
├── ui_home.py # constructores HTML puros de Inicio (testeables)
├── agents/ # 5 agentes + persistencia
│   ├── ingestor.py # normaliza avisos al esquema
│   ├── vision.py # CLIP 512-dim (fallback histograma sin torch)
│   ├── matcher.py # score 0.55/0.25/0.10/0.10 + umbrales >=80/>=65
│   ├── geo.py # haversine, proximidad max(0,1-km/15)
│   ├── notifier.py # panel + log + tabla notifications
│   ├── db.py # SQLite (avisos, notifications, reencuentros)
│   └── admin.py # listar, borrar, resolver (con contraseña)
├── rag/ # texto: MiniLM (fallback TF-IDF/Jaccard) + retrieval
│   ├── embeddings.py # similitud semántica description_text
│   └── retrieval.py # filtra active/opuestos, ordena por score
├── data/seed/ # corpus demo Jerez (viaja en git; Cloud recarga de aquí)
│   ├── lost/ # 7 avisos lost_001…lost_007 (.json)
│   ├── found/ # 13 avisos found_001…found_013 (.json)
│   ├── images/ # fotos reales + backup demo reencuentros/
│   └── embeddings.json # vectores CLIP precalculados (20 avisos)
├── scripts/ # utilidades (compute/load/make seed, checks, smoke)
├── tests/ # 18 ficheros, 91 tests (pytest + AppTest headless)
├── assets/ # logo.png + fondo.png
├── .streamlit/ # config.toml (tema); secrets.toml solo local (no viaja)
├── requirements.md # spec fuente de verdad (v1.40)
├── architecture.md # agentes, flujos y diagramas
├── PROMPT-LOG.md # bitácora de sesiones con la IA (S01…)
├── INFORME.md # informe de reflexión del alumno
└── requirements.txt # dependencias fijadas (sin torch: va en local)
```

Specs (`requirements.md` v1.40, `architecture.md`) son la fuente de verdad: cada commit referencia su sección (`[REQ-…]`). Proceso con IA en `PROMPT-LOG.md`.
