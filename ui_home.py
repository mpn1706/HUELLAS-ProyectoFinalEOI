"""HUELLAS — Lógica pura de la pantalla Inicio (REQ-UI-06).

Sin Streamlit ni BD: testeable en pytest. La app (`app.py`) combina
`select_carousel_items()` + miniaturas data-URI + `build_carousel_html()`.

Garantía de privacidad: estas funciones JAMÁS leen ni emiten `contact_info`,
teléfonos, correos ni RRSS. Solo: id, tipo, especie, color, zona y foto.
"""

import html as _html

ANIMAL_ES = {"dog": "Perro", "cat": "Gato", "other": "Otro"}
MAX_ITEMS = 12


def _titulo(a: dict) -> str:
    especie = ANIMAL_ES.get(a.get("animal"), a.get("animal") or "Otro")
    color = (a.get("color_primary") or "").strip()
    if color:
        return f"{especie} · {color}"
    return f"{especie}"


def _zona(a: dict) -> str:
    loc = a.get("location") or {}
    return ((loc.get("address_text") or "").strip()) or "Jerez de la Frontera"


def select_carousel_items(avisos: list, limit: int = MAX_ITEMS) -> list:
    """Filtra activos lost/found, ordena recientes y devuelve tarjetas seguras.

    Entrada: dicts de aviso (pueden traer `contact_info`, se IGNORA).
    Salida: [{id, type, titulo, zona, image_path, etiqueta}] — sin contacto.
    """
    if limit <= 0:
        return []
    activos = [a for a in (avisos or [])
               if isinstance(a, dict)
               and a.get("status") == "active"
               and a.get("type") in ("lost", "found")
               and a.get("id")]
    activos.sort(key=lambda a: str(a.get("date_reported") or ""), reverse=True)
    out = []
    for a in activos[:limit]:
        tipo = a.get("type")
        out.append({
            "id": str(a.get("id")),
            "type": tipo,
            "titulo": _titulo(a),
            "zona": _zona(a),
            "image_path": a.get("image_url") or "",
            "etiqueta": "Perdido" if tipo == "lost" else "Avistado",
        })
    return out


def build_carousel_html(cards: list) -> str:
    """HTML del carrusel infinito (marquee CSS). Nunca incluye contacto.

    `cards`: [{id, titulo, zona, etiqueta, img_uri}] — `img_uri` data-URI o "".
    El clic va a `?aviso=<id>` (la app lo convierte en salto al aviso).
    Vacío → estado con invitación a publicar el primero.
    """
    if not cards:
        return (
            '<div class="huellas-vp huellas-vacio">'
            '<p class="huellas-vacio-t">Aún no hay avisos con foto.</p>'
            '<p class="huellas-vacio-s">Publica el primero y aparecerá aquí en movimiento.</p>'
            '</div>'
        )
    piezas = []
    for c in cards:
        cid = _html.escape(str(c.get("id", "")), quote=True)
        titulo = _html.escape(str(c.get("titulo", "")), quote=False)
        zona = _html.escape(str(c.get("zona", "")), quote=False)
        et = _html.escape(str(c.get("etiqueta", "")), quote=False)
        uri = str(c.get("img_uri") or "")
        if uri.startswith("data:image"):
            uri_esc = _html.escape(uri, quote=True)
            foto = (f'<img src="{uri_esc}" alt="{titulo}" loading="lazy">')
        else:
            inicial = _html.escape((titulo[:1] or "H").upper(), quote=False)
            foto = f'<div class="huellas-cd-ph" aria-hidden="true">{inicial}</div>'
        cls_et = "perd" if et.lower().startswith("perd") else "avis"
        piezas.append(
            f'<a class="huellas-cd-link" href="?aviso={cid}" title="{titulo}">'
            f'<div class="huellas-cd"><div class="huellas-cd-img">{foto}</div>'
            f'<div class="huellas-cd-b"><div class="huellas-cd-t">{titulo}</div>'
            f'<div class="huellas-cd-z">{zona}</div>'
            f'<span class="huellas-cd-et {cls_et}">{et}</span>'
            '</div></div></a>'
        )
    pista = "".join(piezas)
    # Pista con contenido duplicado para bucle continuo translateX(-50%).
    return (f'<div class="huellas-vp"><div class="huellas-trk">{pista}{pista}</div></div>')
