# HUELLAS — actualización final de Engram (05/10/2026)

Registro curado de decisiones y verificaciones de las sesiones posteriores al snapshot histórico de Engram. No reemplaza ni modifica la exportación histórica del 24/09; la complementa.

## Visión híbrida Cloud/Local

- Fase 0 comparó MobileNetV3-Small en ONNX con el histograma Cloud y CLIP local sobre los pares del seed y una query de gato naranja.
- Decisión: Cloud usa MobileNetV3-Small ONNX (576 dimensiones, `onnxruntime==1.30.0`, modelo de ~4 MB y ~10 MB RAM); Local conserva CLIP (512 dimensiones) si PyTorch está disponible.
- Orden de fallbacks: CLIP → ONNX → histograma → hash. Se preserva la regla de no comparar vectores de espacios distintos.
- Resultado medido antes de integrar: query gatito 72.4% top-1 `lost_001`; par insignia `lost_001→found_011` 84.5% DESTACADA; 0 DESTACADAs cruzadas en la matriz evaluada.

## Seed, persistencia y búsqueda

- `make_seed.py` es la fuente única de verdad. Seed v15: 20 avisos (6 lost + 14 found), 19 activos y uno resuelto por el caso cerrado; 3 reencuentros versionados.
- El Cloud tiene filesystem efímero; la recarga restaura avisos/reencuentros desde JSON versionados. Una prueba de carga desde DB vacía verificó avisos, estados, fotos y enlaces.
- Buscar usa fecha de referencia fija 25/09/2026 para que el factor temporal del seed estático no decaiga; los avisos publicados mantienen fecha real.
- Se añadió raíz ligera en español para diminutivos/género/plural (`gatito/gato/gata`, `manchitas/mancha`) en colores, marcas y fallbacks TF-IDF/Jaccard; los pesos del score no cambiaron.

## Verificación y entrega

- Suite: 121/121 tests; `eval_match.py`, `demo_check.py` (found_011 top-1 80.5%) y `smoke_app.py` (9 páginas) en verde.
- Auditoría de dependencias fijó Folium como dependencia directa; revisión Pyflakes sin imports muertos relevantes. No se alteró CSS ni código móvil.
- Roadmap documental: routing multipágina nativo, bot de Telegram para publicación con foto/ubicación y alertas push ante score ≥80%. La rúbrica oficial del profesor no está disponible y sigue pendiente de cotejo.

## Commits clave

`07e1efb` ONNX Cloud · `93192ca` fecha demo y raíces · `61ecf1e` auditoría técnica · actualización de entregables 05/10/2026.
