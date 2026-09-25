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


def _pct_score(score) -> int:
    """Porcentaje entero 0-100 desde un score 0-1 (tolerante)."""
    try:
        return int(round(max(0.0, min(1.0, float(score))) * 100))
    except (TypeError, ValueError):
        return 0


def _ring_block(pct: int) -> tuple:
    """Bloque anillo+dígitos con keyframes FIJOS. Retorna (estilo, cuerpo)."""
    if pct <= 0:
        tira = ('<span class="huellas-strip"><span class="huellas-track">'
                '<span>0</span></span></span><span class="huellas-pctsign"> %</span>')
        return "", tira
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
    cuerpo = (
        '<div class="huellas-ringwrap">'
        '<svg viewBox="0 0 120 120" class="huellas-ring" aria-hidden="true">'
        '<circle cx="60" cy="60" r="52" class="huellas-ring-bg"></circle>'
        '<circle cx="60" cy="60" r="52" pathLength="100" '
        f'class="huellas-ring-fg huellas-ringfill" '
        f'style="animation:huellas-ringfill-{pct} 1.6s ease-out .25s both"></circle>'
        '</svg>'
        f'<div class="huellas-ring-num">{tira}</div></div>'
    )
    return estilo, cuerpo


def build_match_card_html(cand_id: str, score: float) -> str:
    """Tarjeta de coincidencia con anillo y dígitos que van de 0 al % real.

    Solo CSS robusto: los keyframes se generan con valores FIJOS por tarjeta
    (anillo `stroke-dashoffset` 100→100-pct; tira de dígitos con `steps(pct)`).
    Sin animación, queda el `%` final en la línea del id (visible y correcto).
    """
    pct = _pct_score(score)
    cid = _html.escape(str(cand_id), quote=True)
    estilo, anillo = _ring_block(pct)
    return (
        f"{estilo}"
        '<div class="huellas-match-card">'
        '<div class="huellas-match-t">¡Posible coincidencia!</div>'
        f"{anillo}"
        f'<div class="huellas-match-id"><code>{cid}</code> · <b>{pct} %</b></div>'
        '</div>'
    )


def build_result_card_html(cand_id: str, score: float, dist_km, titulo: str,
                           idx: int = 0, top: bool = False) -> str:
    """Tarjeta de resultado de Buscar: anillo que cuenta + envoltorio en cascada.

    `idx` escalona la entrada 80 ms (`animation-delay` inline). `top` marca la
    mejor coincidencia (borde rojo + pulso). Sin contacto por construcción.
    """
    pct = _pct_score(score)
    cid = _html.escape(str(cand_id), quote=True)
    tit = _html.escape(str(titulo), quote=False)
    try:
        dist = f"{float(dist_km):.2f} km"
    except (TypeError, ValueError):
        dist = "—"
    estilo, anillo = _ring_block(pct)
    cls = "huellas-match-card huellas-res-top" if top else "huellas-match-card"
    retraso = max(0, int(idx)) * 0.08
    return (
        f"{estilo}"
        f'<div class="huellas-res" style="animation-delay:{retraso:.2f}s">'
        f'<div class="{cls}">'
        f'<div class="huellas-match-t">{tit}</div>'
        f"{anillo}"
        f'<div class="huellas-match-id"><code>{cid}</code> · {dist} · '
        f'<b>{pct} %</b></div>'
        '</div></div>'
    )


def build_bars_html(uid, visual: float = 0, zona: float = 0,
                    texto: float = 0, fecha: float = 0) -> str:
    """4 barras (Visual/Zona/Texto/Fecha) que se rellenan en 600 ms.

    Keyframes con valores FIJOS por barra (`huellas-bar-<uid>-<k>`).
    """
    uid = "".join(c if c.isalnum() else "_" for c in str(uid)) or "x"
    pares = [("Visual", visual), ("Zona", zona), ("Texto", texto), ("Fecha", fecha)]
    estilos = ["<style>"]
    filas = []
    for k, (etiq, v) in enumerate(pares):
        pc = _pct_score(v)
        estilos.append(f"@keyframes huellas-bar-{uid}-{k} "
                       f"{{ from {{ width:0; }} to {{ width:{pc}%; }} }}")
        filas.append(
            f'<div class="huellas-bar-row"><span>{etiq}</span>'
            f'<div class="huellas-bar"><div class="huellas-barfill" '
            f'style="animation:huellas-bar-{uid}-{k} .6s ease-out .15s both">'
            '</div></div>'
            f"<b>{pc} %</b></div>")
    estilos.append("</style>")
    return "".join(estilos) + '<div class="huellas-bars">' + "".join(filas) + "</div>"


def build_radar_html() -> str:
    """Radar de búsqueda: anillos + barrido giratorio + pings (solo CSS)."""
    return (
        '<div class="huellas-radarwrap">'
        '<div class="huellas-radar">'
        '<span class="huellas-ping p1"></span>'
        '<span class="huellas-ping p2"></span>'
        '</div><div class="huellas-radar-t">Buscando coincidencias…</div></div>'
    )


def build_foto_scan_html(data_uri: str, alt: str = "foto",
                         etiqueta=None, esquinas: bool = False) -> str:
    """Miniatura con escaneo + relleno verde parpadeante; esquinas y etiqueta opcionales."""
    uri_esc = _html.escape(str(data_uri or ""), quote=True)
    alt_esc = _html.escape(str(alt or "foto"), quote=False)
    extra = ('<i class="c1"></i><i class="c2"></i><i class="c3"></i><i class="c4"></i>'
             if esquinas else "")
    etiqueta_html = ""
    if etiqueta:
        et_esc = _html.escape(str(etiqueta), quote=False)
        etiqueta_html = f'<div><span class="huellas-analizada">{et_esc}</span></div>'
    return (
        f'<div class="huellas-scan"><img src="{uri_esc}" alt="{alt_esc}">{extra}'
        '<div class="huellas-scanline"></div><div class="huellas-flash"></div></div>'
        f'{etiqueta_html}'
    )


def faltantes_buscar(lado=None, foto_ok: bool = False, animal="",
                     size="", color="", desc="") -> list:
    """Campos que faltan en Buscar (shake + aviso). Pura y testeada."""
    faltan = []
    if not lado:
        faltan.append("canal")
    if not foto_ok:
        faltan.append("foto")
    if not animal:
        faltan.append("animal")
    if not size:
        faltan.append("tamaño")
    if not (color or "").strip():
        faltan.append("color principal")
    if not (desc or "").strip():
        faltan.append("descripción")
    return faltan


def fmt_corta(dt) -> str:
    """Fecha para mostrar en formato DD/MM/AA (25/09/26). Robusta."""
    from datetime import datetime

    if dt is None:
        return "—"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return dt[:10]
    try:
        return dt.strftime("%d/%m/%y")
    except Exception:
        return str(dt)


def _eff_dt(iso_last, iso_rep):
    """Fecha efectiva del aviso (last_seen si existe, si no reported)."""
    from datetime import datetime

    for cand in (iso_last, iso_rep):
        if cand:
            try:
                return datetime.fromisoformat(str(cand))
            except ValueError:
                continue
    return None


def dias_perdido(iso_last, iso_rep, hoy=None) -> int:
    """Días enteros desde la fecha efectiva (0 si futura o sin fecha)."""
    from datetime import date

    hoy = hoy or date.today()
    eff = _eff_dt(iso_last, iso_rep)
    if eff is None:
        return 0
    return max(0, (hoy - eff.date()).days)


def es_nuevo(iso_last, iso_rep, ahora=None) -> bool:
    """True si el aviso tiene menos de 48 h (y no es futuro)."""
    from datetime import datetime

    ahora = ahora or datetime.now().astimezone()
    eff = _eff_dt(iso_last, iso_rep)
    if eff is None:
        return False
    if eff.tzinfo is None:
        eff = eff.replace(tzinfo=ahora.tzinfo)
    return 0 <= (ahora - eff).total_seconds() < 48 * 3600


def chip_dias_perdido(n: int) -> str:
    """Chip 'N días perdido' con color de urgencia (verde/ámbar/rojo)."""
    n = max(0, int(n))
    clase = "verde" if n <= 2 else ("ambar" if n <= 6 else "rojo")
    if n == 0:
        txt = "Perdido hoy"
    elif n == 1:
        txt = "1 día perdido"
    else:
        txt = f"{n} días perdido"
    return f'<span class="huellas-chip {clase}">{txt}</span>'


def chip_visto(n: int) -> str:
    """Chip neutro 'Visto hace N días' para avistamientos."""
    n = max(0, int(n))
    txt = "Visto hoy" if n == 0 else (f"Visto hace {n} día" if n == 1
                                      else f"Visto hace {n} días")
    return f'<span class="huellas-chip neutro">{txt}</span>'


def nuevo_html() -> str:
    """Etiqueta 'Nuevo' con punto pulsante."""
    return '<span class="huellas-nuevo"><span class="huellas-dot"></span>Nuevo</span>'


def contacto_details_html(info: str) -> str:
    """Contacto tras <details> nativo: despliega y recoge fluido, sin rerun.

    El resumén alterna "Ver/Ocultar contacto" solo con CSS.
    """
    txt = _html.escape(str(info or "Sin contacto registrado."), quote=False)
    return ('<details class="huellas-details"><summary>'
            '<span class="mas">Ver contacto</span>'
            '<span class="menos">Ocultar contacto</span></summary>'
            f'<div class="huellas-slide"><div>- Contacto: {txt}</div></div></details>')


def build_pen_html() -> str:
    """Boli escribiendo trazos (relleno del hueco al subir foto). Solo CSS.

    Estático (sin parámetros): el SVG dibuja dos trazos y un subrayado en bucle
    con el boli temblando. Sin contacto por construcción.
    """
    return (
        '<div class="huellas-penwrap">'
        '<svg viewBox="0 0 300 150" class="huellas-pen" aria-hidden="true">'
        '<path d="M12 30 Q 70 8, 120 34 T 230 30" pathLength="100" '
        'class="huellas-trazo"></path>'
        '<path d="M12 75 Q 80 60, 150 80 T 260 75" pathLength="100" '
        'class="huellas-trazo t2"></path>'
        '<path d="M12 122 L 150 122" pathLength="100" '
        'class="huellas-trazo t3"></path>'
        '<g class="huellas-boli"><g transform="rotate(28 30 26)">'
        '<rect x="24" y="6" width="12" height="28" rx="4" fill="#23201B"/>'
        '<path d="M24 34 L36 34 L30 48 Z" fill="#E30613"/>'
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
