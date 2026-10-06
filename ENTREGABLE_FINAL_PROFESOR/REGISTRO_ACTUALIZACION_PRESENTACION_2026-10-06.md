# Actualización del guion oral — 06/10/2026

El profesor confirmó la estructura oral definitiva del 13/10: diez minutos, repartidos en cinco de demostración viva más una decisión técnica y cinco de defensa sobre la dirección del agente de IA.

- Se reescribió `PRESENTACION_GUION.md` como ocho diapositivas de apoyo sincronizadas con la demo y el speech.
- La Parte 1 usa el flujo real de Buscar, el fichero de prueba `data/seed/images/lost_001.jpg`, campos reproducibles, cronómetro externo de extremo a extremo, tarjeta/listado de coincidencias y mapas Folium.
- La decisión técnica explica CLIP/PyTorch local y MobileNetV3 ONNX en Cloud (1 GB RAM). Se distingue el benchmark Fase 0 (84.5%) del ensayo actual reproducible (~83%); en vivo se lee el valor real y se rellena el tiempo medido, sin atribuir latencia de UI al modelo.
- La Parte 2 explica roles del agente, prompts estructurados/SDD, errores y regresiones TDD, suite 121 casos y control humano.
- Duración planificada: 00:00–05:00 demo + decisión; 05:00–10:00 defensa IA. No se añadieron ni cambiaron funcionalidades del MVP.
