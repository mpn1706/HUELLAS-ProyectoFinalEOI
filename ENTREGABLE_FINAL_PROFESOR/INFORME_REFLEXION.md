# Informe de reflexión — Proyecto final HUELLAS

**Alumno:** Mario Camacho  
**Curso:** IA Generativa y Vibe Coding — EOI  
**Fecha:** 5 de octubre de 2026
**Metodología:** Spec-Driven Development (SDD)

## 1. Trabajo realizado con apoyo de IA

La IA se utilizó como asistente de diseño, programación, documentación y verificación. A partir de un problema y unas decisiones de producto definidos por mí, ayudó a formalizar `requirements.md` y `architecture.md`, construir la aplicación Streamlit y desarrollar los módulos de `agents/`, `rag/`, `scripts/` y `tests/`.

El MVP permite registrar y buscar avisos de animales perdidos y encontrados en Jerez. La implementación incluye un pipeline de cinco agentes de software —Ingestor, Vision, Matcher, Geo y Notifier—, persistencia SQLite, búsqueda textual con recuperación RAG, mapas Folium y una interfaz con funciones de administración y seguimiento de reencuentros. También se preparó un seed de 20 avisos, herramientas de carga y evaluación, pruebas de interfaz con AppTest, documentación técnica, README y bitácora de prompts.

La IA propuso e implementó iteraciones pequeñas, y colaboró en investigar fallos reproducibles. La entrega actual usa matching explicable con cuatro señales, un corpus local controlado y fallbacks para ejecutar el MVP sin GPU ni claves. La suite contiene 121 casos; en el entorno completo con PyTorch pasan 121/121 y en la instalación base pasan 119 con 2 pruebas CLIP omitidas por depender del paquete opcional. Además se ejecutan evaluación del matching, comprobación E2E y smoke test de las nueve páginas.

## 2. Decisiones humanas, arquitectura y supervisión

La dirección del producto y los criterios de aceptación fueron responsabilidad mía. Antes de ampliar la aplicación definí el alcance del MVP, el esquema de los avisos, la secuencia de agentes y los requisitos en SDD. La especificación se trató como contrato: los cambios importantes debían responder a una necesidad identificada y mantener trazabilidad con los requisitos.

Elegí Python, Streamlit y SQLite para obtener una demo sencilla de ejecutar y desplegar. Decidí mantener un corpus propio y no depender de scraping de redes sociales; usar Jerez como ámbito geográfico; admitir perros, gatos y otros animales; y no presentar una coincidencia como una identificación cierta. La interfaz muestra posibles candidatos, señales y aviso legal. También fijé que la administración no tuviera contraseña predeterminada y permaneciera desactivada si no se configura un secreto.

Una decisión técnica clave fue priorizar la señal visual sin hacer que el sistema dependiera obligatoriamente de modelos pesados. El score final combina visual (55%), texto (25%), tiempo (10%) y geografía (10%). Se notifican resultados desde el 80%, se listan desde el 65% y existe una puerta visual del 95% para casos de imagen casi idéntica. En local pueden usarse embeddings CLIP; en Cloud, donde el límite de 1 GB de RAM impide cargar PyTorch, se ejecuta MobileNetV3-Small en ONNX (un 5% de la memoria del canónico) y el histograma de color queda como último recurso. Esta elección reduce la barrera de instalación, aunque se documenta que el motor ligero discrimina algo menos que CLIP.

Supervisé las entregas ejecutando pruebas y revisando el comportamiento de la demo, no aceptando el código solo por su apariencia. También decidí revertir iteraciones de interfaz cuando las pruebas manuales mostraron un empeoramiento y mantuve explícitamente la restricción de no modificar la experiencia móvil sin autorización.

## 3. Errores de IA y método de corrección

Durante el desarrollo se detectaron errores concretos: uso de `sys.insert` en vez de `sys.path.insert`; cálculo temporal con `.days` que penalizaba dos avisos del mismo día; comparación exacta de flotantes en un test; paso de vectores al matcher donde se esperaba una puntuación escalar; y rutas relativas incorrectas en `AppTest.from_file`. Cada caso se reprodujo mediante ejecución, se corrigió y se volvió a verificar con una prueba o script pertinente.

También hubo desviaciones de diseño que exigieron revisión: el fallback visual en Cloud podía comparar imágenes en espacios incompatibles, y algunas iteraciones de CSS móvil causaron regresiones. La respuesta fue aislar la causa, limitar el alcance del cambio, añadir o ajustar pruebas y revertir lo que no cumplía el criterio humano. La experiencia confirmó que una respuesta generada por IA es una propuesta: la aceptación final requiere especificación, reproducción, evidencia y juicio del responsable del proyecto.

## 4. Resultado y límites

La versión final cuenta con especificaciones SDD, 20 avisos de demo, documentación de instalación y despliegue público. La suite tiene 121 casos: 121/121 pasan con PyTorch y la instalación base ejecuta 119 con 2 pruebas CLIP omitidas por la dependencia opcional. La aplicación prioriza candidatos, pero no confirma identidades. El almacenamiento de la demo Cloud es efímero y la visión Cloud (MobileNetV3 ONNX) discrimina algo menos que CLIP; estos límites se comunican en el README para que no se confunda el prototipo con un servicio persistente o una verificación concluyente.

La principal aportación del trabajo no fue delegar el proyecto a la IA, sino aprender a dirigirla: delimitar el problema, establecer restricciones, contrastar los resultados con pruebas y conservar únicamente los cambios que satisfacían los requisitos.

## 5. Límites técnicos y Roadmap V2.0

### 5.1 Gestión de recursos en nube vs. local (arquitectura híbrida)

El motor de visión canónico local utiliza CLIP `openai/clip-vit-base-patch32` (512 dimensiones, PyTorch/Transformers). En Streamlit Community Cloud, cuyo plan gratuito dispone de alrededor de 1 GB de RAM, cargar ese modelo completo puede causar un error de memoria (OOM). Por ello, Cloud usa MobileNetV3-Small exportado a ONNX (576 dimensiones, alrededor de 10 MB de RAM); el histograma de color queda como último recurso si faltaran el runtime o los ficheros del modelo. Las búsquedas comparan query y candidatos dentro del mismo espacio vectorial. CLIP se mantiene como ruta local preferente.

### 5.2 Navegación y UX web (arquitectura SPA y estado)

El MVP concentra la interfaz en una aplicación Streamlit de página única para mantener una respuesta ágil y controlar de forma directa el estado compartido de los agentes y los formularios. La navegación actual ya refleja la sección en parámetros de URL (`?s=`) y admite enlaces directos básicos. En V2.0 se propone migrar al routing multipágina nativo de Streamlit y reforzar la integración con el historial del navegador, las acciones atrás/adelante y los deep links hacia fichas concretas.

### 5.3 Integración y automatización: bot de Telegram bidireccional

El siguiente paso de producto sería un bot bidireccional con dos flujos: publicación *on-the-go* (enviar desde la calle una foto y la ubicación para registrar un aviso al instante) y alertas push en tiempo real cuando HUELLAS detecte una posible coincidencia que alcance el umbral de notificación (score ≥80%). El bot queda fuera del MVP actual, coherente con H-09 (panel y registro, sin Telegram), y requeriría una API, autenticación, alojamiento siempre disponible y persistencia externa.
