# MascotasLost&Found — requirements.md

> Metodología: Spec-Driven Development (SDD).
> Este documento es la fuente de verdad del MVP. Todo commit debe referenciar una sección (p.ej. `REQ-03`, `CU-02`).
> Estado: v1.0 — decisiones cerradas 23/09/2026 (13/13). Stack: Streamlit + Python + SQLite, 100% local. Sin código aún.

## 1. Objetivo (REQ-01)

Construir un MVP funcional que centralice avisos de mascotas perdidas (`lost`) y encontradas (`found`) en un corpus propio y controlado, y sugiera **posibles coincidencias** a partir de imagen, descripción textual, ubicación y fecha.

El valor no es identificar con certeza, sino **priorizar candidatos** para que el dueño revise visualmente y contacte.

Principio transversal: **el sistema nunca afirma "es el mismo animal"**. Siempre muestra "posible coincidencia" con porcentaje y señales que la sustentan. El aviso legal vive en un único apartado del sidebar ("Este análisis no promete una coincidencia inequívoca respecto al animal buscado. Una imagen no permite confirmar la identidad, verifique en persona.").

## 2. Problema que resuelve (REQ-02)

Cuando una mascota se pierde, los avisos quedan dispersos en redes sociales y protectoras sin forma de cruzarlos automáticamente. El sistema centraliza avisos y propone cruces lost ↔ found.

## 3. Alcance del MVP — qué SÍ hace (REQ-03)

- REQ-03.1: Acepta cualquier animal doméstico (`dog | cat | other`), no solo perros/gatos.
- REQ-03.2: Permite registrar avisos `lost` y `found` con foto + texto libre + ubicación (lat/lng) + fechas.
- REQ-03.3: Normaliza todo aviso al esquema **Entidad Aviso** (ver §6).
- REQ-03.4: Ejecuta pipeline de 5 agentes: Ingestor → Vision Analyst → Matcher (+ Geo) → Notifier (ver §7).
- REQ-03.5: Calcula `score_total` con fórmula y pesos cerrados (ver §8).
- REQ-03.6: Muestra ranking de posibles coincidencias con desglose por señales y aplica umbrales §9.
- REQ-03.7: Visualiza candidatos en mapa interactivo por proximidad geográfica.
- REQ-03.8: Funciona con corpus demo propio de 15-20 avisos cargados manualmente (seed data).

## 4. Alcance — qué NO hace (límites explícitos, REQ-04)

- REQ-04.1: **NO scraping en vivo** de Facebook, Instagram, protectoras ni ninguna fuente externa. Queda fuera del MVP como ampliación futura documentable en memoria/slides, no a construir.
- REQ-04.2: **NO afirma identidad**: prohibido el literal "es el mismo animal" en UI, logs o notificaciones.
- REQ-04.3: NO autenticación multi-usuario ni roles. Excepción v1.1: UN único administrador con contraseña para moderación básica (ver REQ-11).
- REQ-04.4: NO app móvil nativa. Solo web MVP ejecutable en local + despliegue simple.
- REQ-04.5: NO Telegram/webhook real. Notifier MVP = panel/tabla en Streamlit + log (decisión 9, 23/09/2026).
- REQ-04.6: NO genera cartel PDF "SE BUSCA" en MVP (ampliación propuesta fuera de alcance salvo decisión explícita posterior).

## 5. Casos de uso principales

### CU-01 — Registrar aviso `lost`
Actor: dueño. Flujo: sube foto + descripción + ubicación + fechas + contacto opcional → Ingestor normaliza → Vision Analyst extrae atributos y embedding → se persiste → Matcher lo compara contra corpus `found` activos → se muestran coincidencias >=65% y se notifica si >=85%.

### CU-02 — Registrar aviso `found`
Actor: persona que encuentra / protectora. Flujo simétrico a CU-01, comparando contra corpus `lost` activos.

### CU-03 — Buscar coincidencias de un aviso existente
Actor: dueño / evaluador. Selecciona un aviso `lost`, define radio máximo y lanza Matcher contra `found`. Recibe lista ordenada por `score_total` con desglose.

### CU-04 — Revisar detalle de posible coincidencia
Actor: dueño. Ve lado a lado fotos, distancia km, diferencia días, atributos coincidentes/divergentes, y aviso legal de no-identidad. Decide contactar fuera del sistema.

### CU-05 — Resolver / expirar aviso
Actor: dueño. Marca aviso como `resolved` mediante botón manual "Marcar como resuelto". Función `expire_old()` marca `expired` a los avisos con más de 30 días (invocable bajo demanda, sin cron). Los no-`active` no entran en matching.

Fuera de MVP: CU-07 ingesta automática externa, CU-08 chat asistente, CU-09 impresión cartel.

### CU-06 — Moderar avisos (administrador)
Actor: administrador autenticado (contraseña). Flujo: entra en el apartado Administración del sidebar → filtra por tipo/texto → elimina duplicados o vandalismo (con confirmación) o marca resueltos → la acción queda en `data/admin.log`.

## 6. Esquema de datos — Entidad Aviso (REQ-05)

Todo aviso persiste con esta forma (decisión cerrada, no modificar sin nueva spec):

```json
{
  "id": "uuid",
  "type": "lost | found",
  "animal": "dog | cat | other",
  "breed_guess": "string (opcional, generado por el agente de visión)",
  "color_primary": "string",
  "color_secondary": "string (opcional)",
  "markings": ["string"],
  "size": "small | medium | large",
  "has_collar": "boolean",
  "collar_description": "string (opcional)",
  "description_text": "string (texto libre del usuario)",
  "location": { "lat": "number", "lng": "number", "address_text": "string opcional" },
  "date_reported": "ISO 8601 datetime",
  "date_last_seen": "ISO 8601 datetime (opcional)",
  "image_url": "string",
  "image_embedding": "vector (generado por el agente de visión, no por el usuario)",
  "contact_info": "string (opcional)",
  "status": "active | resolved | expired"
}
```

Reglas derivadas:
- REQ-05.1: `id` UUID v4 generado en ingesta.
- REQ-05.2: `breed_guess` e `image_embedding` solo los escribe Vision Analyst, nunca el usuario. `image_embedding`: CLIP `openai/clip-vit-base-patch32`, 512 dimensiones.
- REQ-05.3: Solo `status=active` participa en Matcher.
- REQ-05.4: El cruce es siempre `lost ↔ found`, nunca `lost ↔ lost` ni `found ↔ found`.
- REQ-05.5: `image_url`: ruta local relativa `data/seed/images/<fichero>`.
- REQ-05.6: Conflicto Ingestor vs Vision (decisión 10): manda Vision Analyst para `color_primary` y resto de atributos visuales; `description_text` conserva intacto el texto original del usuario.
- REQ-05.7: Si `animal="other"`: obligatorios `color_primary`, `size`, `description_text`; opcionales `markings`, `has_collar`/`collar_description`; `breed_guess` se omite (NULL).
- REQ-05.8: `location`: lat/lng capturados por mapa clicable Leaflet; ciudad seed fija: Jerez de la Frontera.
- REQ-05.9: Idioma UI y textos: solo español.

## 7. Agentes y responsabilidades (REQ-06, decisión cerrada)

1. **Ingestor**: recibe foto + texto + ubicación + fecha de un aviso nuevo y lo normaliza al esquema §6. No calcula scores. Preserva `description_text` intacto.
2. **Vision Analyst**: procesa la imagen y extrae especie, raza aproximada, color, manchas, collar, tamaño, y genera el embedding visual CLIP 512-dim. Tiene precedencia sobre atributos visuales (decisión 10).
3. **Matcher**: compara un aviso contra el resto del corpus y calcula score (ver §8).
4. **Geo**: calcula distancia haversine y aplica `max(0, 1 - distancia_km / 15)`, radio_máximo fijo 15 km.
5. **Notifier**: si `score >= 85%`, registra en tabla `notifications` + log y muestra destacada en panel Streamlit. Sin Telegram real.

> Conflicto Ingestor vs Vision resuelto 23/09/2026: manda Vision para `color_primary`; texto usuario intacto en `description_text`.

## 8. Motor de matching — fórmula y pesos cerrados (REQ-07, no cambiar)

```
score_total = (0.40 × similitud_visual)
            + (0.30 × proximidad_geográfica)
            + (0.20 × similitud_texto)
            + (0.10 × proximidad_temporal)
```

- `similitud_visual`: similitud coseno entre embeddings CLIP `openai/clip-vit-base-patch32` 512-dim (0-1).
- `proximidad_geográfica`: max(0, 1 - distancia_km / 15), radio_máximo fijo = 15 km.
- `similitud_texto`: 0.70 × estructurado + 0.30 × semántico. Estructurado: coincidencia campo a campo de `color_primary`, `markings`, `has_collar`, `size`. Semántico: coseno con `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` sobre `description_text`.
- `proximidad_temporal`: max(0, 1 - dias_diferencia / 30), ventana 30 días. Fecha usada: `date_last_seen` si existe, si no `date_reported`.

Restricciones: los 4 pesos suman 1.0. No se reponderan sin nueva spec.

## 9. Umbrales de notificación (REQ-08, decisión cerrada 23/09/2026, `>=`)

- Score >= 85%: notificación automática (panel + log) + se muestra como "posible coincidencia" destacada.
- Score 65-84.99%: aparece en el listado, sin notificación.
- Score < 65%: no se muestra como coincidencia, pero queda indexado.

## 10. Requisitos no funcionales (REQ-09)

- REQ-09.1: Ejecución local en 1 comando documentado en README para que el profesor evalúe sin nube.
- REQ-09.2: Despliegue simple opcional (Streamlit Cloud / similar) con enlace en README.
- REQ-09.3: SQLite / ficheros locales para seed; sin servicios externos obligatorios.
- REQ-09.4: Explicabilidad: todo match muestra sus 4 sub-scores.
- REQ-09.5: Privacidad mínima: `contact_info` opcional, visible solo en detalle.
- REQ-09.6: Trazabilidad SDD: commit → sección de spec.

## 11. Criterios de éxito del MVP (REQ-10)

- ÉXITO-01: Con seed de 15-20 avisos, un `lost` de prueba recupera al menos 1 `found` relevante >65% con desglose correcto.
- ÉXITO-02: Ninguna pantalla/log/notificación contiene "es el mismo animal".
- ÉXITO-03: Matcher respeta fórmula/pesos/umbrales auditables (test con vectores fijos).
- ÉXITO-04: Profesor ejecuta en local siguiendo README en <10 min sin claves obligatorias.
- ÉXITO-05: Repo GitHub con historial progresivo + PROMPT-LOG.md + sesiones Engram + informe reflexión.
- ÉXITO-06: Demo 5 min: registro → ranking → mapa → detalle explicable.

## 12. Administración (REQ-11, añadido v1.1)

- REQ-11.1: Un único administrador; acceso por contraseña (Secrets `ADMIN_PASSWORD` en Cloud, variable `HUELLAS_ADMIN_PASSWORD` o defecto documentado `huellas123` en local).
- REQ-11.2: Puede listar con filtros, eliminar (borra aviso + notificaciones ligadas + foto subida, nunca seed) y resolver.
- REQ-11.3: Toda acción se registra en `data/admin.log` con fecha.

## 13. Decisiones cerradas 23/09/2026 (13/13 — bloquean inicio de código)

1. Stack: Streamlit + Python + SQLite, 100% local. ✅
2. `image_embedding`: CLIP `openai/clip-vit-base-patch32`, 512-dim. ✅
3. `similitud_texto`: 70% estructurado (`color_primary`, `markings`, `has_collar`, `size`) + 30% semántico (`paraphrase-multilingual-MiniLM-L12-v2` sobre `description_text`). ✅
4. `proximidad_temporal`: `max(0, 1 - dias/30)`, ventana 30d, fecha = `date_last_seen` si existe si no `date_reported`. ✅
5. `radio_máximo`: 15 km fijos. ✅
6. Umbrales: `>=` en ambos (85 y 65). ✅
7. Ubicación: mapa Leaflet clicable + seed Jerez de la Frontera. ✅
8. `image_url`: ruta local `data/seed/images/`. ✅
9. Notifier: panel/tabla Streamlit + log, sin Telegram. ✅
10. Conflicto: manda Vision para `color_primary`; `description_text` intacto. ✅
11. `status`: botón "Marcar como resuelto" + `expire_old()` 30d bajo demanda, sin cron. ✅
12. `other`: obligatorios `color_primary`, `size`, `description_text`; opcionales `markings`, `has_collar`; `breed_guess` NULL. ✅
13. Idioma: solo español. ✅
