# Registro de preparación del paquete — 05/10/2026

## Actualización realizada

Se sincronizaron los documentos existentes del paquete con sus fuentes actuales, sin reconstruirlos desde cero: README, informe de reflexión, guion oral, PROMPT-LOG y checklist. Se incluyeron las especificaciones `requirements.md` v1.41 y `architecture.md`, se actualizó `ENLACES_Y_REPOSITORIO.txt` y se incorporó el delta reciente de Engram, manteniendo marcado como histórico el snapshot original del 24/09.

## Estado técnico verificado

- 20 avisos (6 lost + 14 found), con 19 activos y uno resuelto; 3 reencuentros sembrados.
- Visión local CLIP 512-d y visión Cloud MobileNetV3-Small ONNX 576-d; histograma/hash como últimos recursos.
- Búsquedas de demo con referencia temporal fija al 25/09/2026; publicación con fecha real y fecha de pérdida/avistamiento seleccionable.
- 121 tests en verde, `eval_match.py` correcto, `demo_check.py` (found_011 top-1 80.5%) y `smoke_app.py` (9 páginas).
- Roadmap V2: routing multipágina nativo y bot Telegram bidireccional con publicación desde la calle y alertas push al alcanzar score ≥80%.

## Pendiente externo

La guía/rúbrica oficial del profesor no se ha recibido. El checklist identifica este único bloqueo para certificar cumplimiento frente a criterios externos concretos.

El ZIP contiene esta carpeta documental y registros Engram filtrados/curados. El código y los modelos ONNX se obtienen del repositorio enlazado; no se incluyen secretos ni la base SQLite local.
