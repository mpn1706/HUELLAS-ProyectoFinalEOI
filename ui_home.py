"""HUELLAS — Lógica pura de la pantalla Inicio (REQ-UI-06).

Sin Streamlit ni BD: testeable en pytest. La app (`app.py`) combina
`select_carousel_items()` + miniaturas data-URI + `build_carousel_html()`.

Garantía de privacidad: estas funciones JAMÁS leen ni emiten `contact_info`,
teléfonos, correos ni RRSS. Solo: id, tipo, especie, color, zona y foto.
"""

import html as _html

ANIMAL_ES = {"dog": "Perro", "cat": "Gato", "other": "Otro"}
MAX_ITEMS = 12
THUMB_W, THUMB_H = 300, 208  # ratio 150×104 de la tarjeta: el cover no recorta
THUMB_BG = (245, 241, 234)  # crema #F5F1EA: misma que imagen_cuadrada en app.py


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


def make_carousel_thumb(path: str) -> str:
    """Miniatura letterbox crema 300×208 en data URI (animal entero, centrado).

    Pura (solo PIL): la app la envuelve con `st.cache_data(ttl=120)`.
    Si la foto falta o falla, cadena vacía (la tarjeta muestra inicial).
    """
    try:
        from PIL import Image
        import base64
        import io

        img = Image.open(path).convert("RGB")
        img.thumbnail((THUMB_W, THUMB_H))
        lienzo = Image.new("RGB", (THUMB_W, THUMB_H), THUMB_BG)
        lienzo.paste(img, ((THUMB_W - img.width) // 2, (THUMB_H - img.height) // 2))
        buf = io.BytesIO()
        lienzo.save(buf, format="JPEG", quality=65)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return ""


def faltantes_publicar(tipo="", animal="", size="", color="", desc="",
                       movil="", mail="", rrss="") -> list:
    """Campos obligatorios que faltan al publicar (shake + aviso).

    Pura y testeada: la app la usa para decidir pulso/shake sin tocar el matching.
    Color principal y descripción también son obligatorios (v1.14).
    """
    faltan = []
    if not tipo:
        faltan.append("tipo de aviso")
    if not animal:
        faltan.append("animal")
    if not size:
        faltan.append("tamaño")
    if not (color or "").strip():
        faltan.append("color principal")
    if not (desc or "").strip():
        faltan.append("descripción")
    if not ((movil or "").strip() or (mail or "").strip() or (rrss or "").strip()):
        faltan.append("contacto (móvil, correo o red social)")
    return faltan


def build_crossing_html(n: int) -> str:
    """Bloque 'Cruzando con N avisos…' con puntos que rebotan (solo CSS)."""
    return (
        '<div class="huellas-cruce">'
        f'Cruzando con {int(n)} aviso(s)…'
        '<span class="huellas-dots"><span></span><span></span><span></span></span>'
        '</div>'
    )


def build_match_card_html(cand_id: str, score: float) -> str:
    """Tarjeta de coincidencia con anillo y dígitos que van de 0 al % real.

    Solo CSS robusto: los keyframes se generan con valores FIJOS por tarjeta
    (anillo `stroke-dashoffset` 100→100-pct; tira de dígitos con `steps(pct)`).
    Sin animación, queda el `%` final en la línea del id (visible y correcto).
    """
    try:
        pct = int(round(max(0.0, min(1.0, float(score))) * 100))
    except (TypeError, ValueError):
        pct = 0
    cid = _html.escape(str(cand_id), quote=True)
    if pct <= 0:
        tira = ('<span class="huellas-strip"><span class="huellas-track">'
                '<span>0</span></span></span><span class="huellas-pctsign"> %</span>')
        estilo = ''
    else:
        digitos = "".join(f"<span>{i}</span>" for i in range(pct + 1))
        viaje = f"{pct * 1.4:.1f}"
        estilo = (
            "<style>"
            f"@keyframes huellas-ringfill-{pct} "
            f"{{ from {{ stroke-dashoffset:100; }} to {{ stroke-dashoffset:{100 - pct}; }} }}"
            f"@keyframes huellas-strip-{pct} "
            f"{{ from {{ transform:translateY(0); }} to {{ transform:translateY(-{viaje}em); }} }}"
            "</style>"
        )
        tira = (f'<span class="huellas-strip"><span class="huellas-track" '
                f'style="animation:huellas-strip-{pct} 1.6s steps({pct}) .25s both">'
                f'{digitos}</span></span><span class="huellas-pctsign"> %</span>')
    return (
        f"{estilo}"
        '<div class="huellas-match-card">'
        '<div class="huellas-match-t">¡Posible coincidencia!</div>'
        '<div class="huellas-ringwrap">'
        '<svg viewBox="0 0 120 120" class="huellas-ring" aria-hidden="true">'
        '<circle cx="60" cy="60" r="52" class="huellas-ring-bg"></circle>'
        '<circle cx="60" cy="60" r="52" pathLength="100" '
        f'class="huellas-ring-fg huellas-ringfill"'
        + (f' style="animation:huellas-ringfill-{pct} 1.6s ease-out .25s both"'
           if pct > 0 else '')
        + '></circle>'
        '</svg>'
        f'<div class="huellas-ring-num">{tira}</div></div>'
        f'<div class="huellas-match-id"><code>{cid}</code> · <b>{pct} %</b></div>'
        '</div>'
    )


def build_pen_html() -> str:
    """Boli escribiendo trazos (relleno del hueco al subir foto). Solo CSS.

    Estático (sin parámetros): el SVG dibuja dos trazos y un subrayado en bucle
    con el boli temblando. Sin contacto por construcción.
    """
    return (
        '<div class="huellas-penwrap">'
        '<svg viewBox="0 0 300 96" class="huellas-pen" aria-hidden="true">'
        '<path d="M12 26 Q 70 6, 120 30 T 230 26" pathLength="100" '
        'class="huellas-trazo"></path>'
        '<path d="M12 54 Q 80 40, 150 56 T 260 52" pathLength="100" '
        'class="huellas-trazo t2"></path>'
        '<path d="M12 80 L 120 80" pathLength="100" '
        'class="huellas-trazo t3"></path>'
        '<g class="huellas-boli"><g transform="rotate(28 30 22)">'
        '<rect x="24" y="2" width="12" height="28" rx="4" fill="#23201B"/>'
        '<path d="M24 30 L36 30 L30 44 Z" fill="#E30613"/>'
        "</g></g>"
        "</svg></div>"
    )


def build_check_html() -> str:
    """Check verde que se dibuja solo (solo CSS) para 'sin coincidencias'."""
    return (
        '<div class="huellas-okcheck">'
        '<svg viewBox="0 0 52 52" aria-hidden="true">'
        '<circle cx="26" cy="26" r="24"></circle>'
        '<path d="M15 27l7 7 15-16"></path>'
        '</svg></div>'
    )


def build_counts_html(n_lost: int, n_found: int, n_reenc: int) -> str:
    """3 contadores blancos clicables (?page= → su pestaña). Sin contacto."""
    return (
        '<div class="huellas-counts">'
        f'<a class="huellas-count-link" href="?page=perdidos">'
        f'<div class="huellas-count"><div class="huellas-count-v">{int(n_lost)}</div>'
        '<div class="huellas-count-l">perdidos activos</div></div></a>'
        f'<a class="huellas-count-link" href="?page=encontrados">'
        f'<div class="huellas-count"><div class="huellas-count-v">{int(n_found)}</div>'
        '<div class="huellas-count-l">avistamientos</div></div></a>'
        f'<a class="huellas-count-link" href="?page=reencuentro">'
        f'<div class="huellas-count"><div class="huellas-count-v">{int(n_reenc)}</div>'
        '<div class="huellas-count-l">reencuentros</div></div></a>'
        '</div>'
    )


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
            f'<a class="huellas-cd-link" href="?aviso={cid}">'
            f'<div class="huellas-cd"><div class="huellas-cd-img">{foto}</div>'
            f'<div class="huellas-cd-b"><div class="huellas-cd-t">{titulo}</div>'
            f'<div class="huellas-cd-z">{zona}</div>'
            f'<span class="huellas-cd-et {cls_et}">{et}</span>'
            '</div></div></a>'
        )
    pista = "".join(piezas)
    # Pista con contenido duplicado para bucle continuo translateX(-50%).
    return (f'<div class="huellas-vp"><div class="huellas-trk">{pista}{pista}</div></div>')
