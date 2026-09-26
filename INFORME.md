# Informe de reflexión — MascotasLost&Found

**Alumno:** Mario Camacho · **Proyecto:** HUELLAS, sistema de búsqueda y comparativa visual de animales perdidos (Jerez de la Frontera) · **Metodología:** Spec-Driven Development con OpenCode.

## 1. Qué ejecutó la IA

La IA trabajó siempre bajo especificación cerrada (`requirements.md` v1.0 + `architecture.md`) y generó: formalización de ambos specs a partir de mi borrador; el núcleo `agents/` (geo/haversine con radio 15 km, ingestor con validación del esquema Aviso, matcher con la fórmula `0.40/0.30/0.20/0.10` y umbrales `>=`, vision con CLIP y fallback, SQLite espejo del esquema, notifier panel+log); el RAG textual (MiniLM con fallback TF-IDF/Jaccard + retrieval con filtro `active`/tipo opuesto); el seed reproducible de 17 avisos de Jerez con imágenes placeholder; la app Streamlit (buscar, registrar, notificaciones, mapa Folium); y la batería de verificación (13 tests, `eval_match.py`, `demo_check.py` E2E, `smoke_app.py` headless). También redactó `README.md` y este informe a partir de mis indicaciones.

## 2. Qué decidí y supervisé yo

Todas las decisiones de producto son mías y la IA las formalizó sin rediseñarlas (13/13, 23/09): stack Streamlit+SQLite 100% local ejecutable sin claves; modelos (CLIP 512-dim, MiniLM 70/30); fórmulas exactas (`max(0,1-km/15)`, `max(0,1-días/30)` con `last_seen→reported`); umbrales inclusivos `>=`; seed de Jerez en lugar de Sevilla; `image_url` local; notifier sin Telegram; precedencia de Vision en color con texto de usuario intacto; expiración bajo demanda sin cron; reglas de `animal: other`; solo español. Impuse además los dos marcos que blindan el proyecto: **nada de scraping vivo en el camino crítico** (corpus controlado) y **prohibido afirmar identidad** ("posible coincidencia" + aviso legal en UI, logs y notificaciones). Supervisé cada entrega ejecutándola: pytest, E2E (`lost_001→found_001` top-1, 96.3%), smoke test, y exigí commits trazables `[REQ-…]` (7 en `main`, reescritos a mi autoría antes del primer push a GitHub).

## 3. Errores de la IA y cómo los corregí

Cinco, todos detectados por ejecución, no por inspección visual: (1) `sys.insert(0,…)` en dos scripts — AttributeError al correrlos; corrección: `sys.path.insert`. (2) `timedelta.days` con floor negativo: dos avisos del mismo día daban temporal 0.966 en vez de 1.0; lo reveló un test; corrección: comparar `.date()`. (3) `assert score_total(1,1,1,1) == 1.0` — falló por `0.999…`; corrección: tolerancia `1e-9`. (4) El más grave: `retrieval` pasaba **vectores** al matcher donde esperaba un float (`TypeError` en el E2E); rediseño: el coseno visual se calcula en retrieval y el fallback de visión usa los bytes de la imagen. (5) `AppTest.from_file("app.py")` resolvía contra `scripts/` (FileNotFoundError); corrección: ruta absoluta. Limitación asumida y documentada: con placeholders del mismo color sólido el visual da 1.0 entre marrones distintos; con CLIP real diferenciaría, y el desglose por señales + geo/temporal lo compensa en la demo.

**Conclusión:** la IA aceleró la construcción, pero el valor del proyecto está en la dirección: especificaciones cerradas antes de programar, verificación por ejecución de cada pieza y corrección de cinco errores que habrían roto la demo del 13 de octubre.

---

## 4. Addendum — Estado final del proyecto (26/09/2026)

La evolución posterior al cierre inicial (v1.1–v1.40, sesiones S02–S138) dejó el sistema en su estado de entrega:

- **Spec viva**: `requirements.md` v1.40 (25/09/2026) + `architecture.md` como fuente de verdad; cada commit referencia su sección (`[REQ-…]`).
- **Datos**: seed reproducible de **20 avisos de Jerez con fotos reales** (7 lost + 13 found, todos activos) en `data/seed/`, con `embeddings.json` (vectores CLIP 512-dim precalculados) viajando en git.
- **Matching v1.40**: fórmula `0.55·visual + 0.25·texto + 0.10·temporal + 0.10·geo` (antes 0.40/0.30/0.20/0.10), umbrales `>=80%` notifica + destaca, `>=65%` lista, puerta visual `>=95%` (misma foto), colores/marcas normalizados sin tildes.
- **Agentes**: 5 (Ingestor, Vision con fallback histograma sin torch, Matcher, Geo, Notifier) + SQLite + RAG textual (MiniLM con fallback TF-IDF/Jaccard) + Administración con contraseña (desactivada por defecto) y gestor de reencuentros.
- **Verificación**: suite de **92 tests** (17 ficheros, pytest + AppTest headless) en verde; `eval_match.py` (fórmula con vectores fijos), `demo_check.py` E2E (lost_001 → found_011 top-1 80.8%), `smoke_app.py` (9 páginas sin excepciones).
- **UI**: inicio con hero animado, carrusel infinito, tiras, contadores y modo demo, páginas Publicar/Buscar/Perdidos/Avistamientos/Reencuentros, mapas Folium, todo en español y responsive móvil/escritorio con `prefers-reduced-motion`.
- **Despliegue**: demo en vivo <https://huellas.streamlit.app> sobre la rama `main` (auto-carga del seed si la DB está vacía; en Cloud la señal visual usa histograma y en local CLIP real).
- **Auditoría final 26/09/2026**: sincronización local/Cloud exacta (tag `punto-restauracion` en HEAD), `requirements.txt` sin dependencias sobrantes (Streamlit fijado a 1.64.0 a propósito), documentación y métricas actualizadas. Conservadas a conciencia las imágenes de trabajo/backup del seed.
