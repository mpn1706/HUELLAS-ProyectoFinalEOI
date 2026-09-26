"""HUELLAS — Lógica pura de la pantalla Inicio (REQ-UI-06).

Sin Streamlit ni BD: testeable en pytest. La app (`app.py`) combina
`select_carousel_items()` + miniaturas data-URI + `build_carousel_html()`.

Garantía de privacidad: estas funciones JAMÁS leen ni emiten `contact_info`,
teléfonos, correos ni RRSS. Solo: id, tipo, especie, color, zona y foto.
"""

import html as _html
from pathlib import Path as _Path

ANIMAL_ES = {"dog": "Perro", "cat": "Gato", "other": "Otro"}
MAX_ITEMS = 12
THUMB_W, THUMB_H = 300, 208  # ratio 150×104 de la tarjeta: el cover no recorta
THUMB_BG = (245, 241, 234)  # crema #F5F1EA: misma que imagen_cuadrada en app.py
PERG_DIR = _Path(__file__).resolve().parent / "data" / "seed" / "images" / "animacion_pergamino"


def _titulo(a: dict) -> str:
    especie = ANIMAL_ES.get(a.get("animal"), a.get("animal") or "Otro")
    color = (a.get("color_primary") or "").strip()
    if color:
        return f"{especie} · {color}"
    return f"{especie}"


def _zona(a: dict) -> str:
    loc = a.get("location") or {}
    return ((loc.get("address_text") or "").strip()) or "Jerez de la Frontera"


def select_carousel_items(avisos: list, limit: int = MAX_ITEMS,
                          extra: dict | None = None) -> list:
    """Filtra activos lost/found, ordena recientes y devuelve tarjetas seguras.

    Entrada: dicts de aviso (pueden traer `contact_info`, se IGNORA).
    `extra`: {aviso_id: "revision"|"cerrado"} — esos avisos entran aunque estén
    resueltos (siguen visibles en el carrusel) con segunda etiqueta.
    Salida: [{id, type, titulo, zona, image_path, etiqueta, extra}] — sin contacto.
    """
    if limit <= 0:
        return []
    extra = extra or {}
    activos = [a for a in (avisos or [])
               if isinstance(a, dict)
               and (a.get("status") == "active" or a.get("id") in extra)
               and a.get("type") in ("lost", "found")
               and a.get("id")]
    activos.sort(key=lambda a: str(a.get("date_reported") or ""), reverse=True)
    out = []
    for a in activos[:limit]:
        tipo = a.get("type")
        marca = extra.get(a.get("id"))
        out.append({
            "id": str(a.get("id")),
            "type": tipo,
            "titulo": _titulo(a),
            "zona": _zona(a),
            "image_path": a.get("image_url") or "",
            "etiqueta": "Perdido" if tipo == "lost" else "Avistado",
            "extra": ("En revisión" if marca == "revision"
                      else "Caso cerrado" if marca == "cerrado" else None),
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
    """Miniatura con línea de escaneo; esquinas de encuadre + etiqueta opcionales."""
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
        '<div class="huellas-scanline"></div></div>'
        f'{etiqueta_html}'
    )


def badge_lateral_html(texto: str) -> str:
    """Insignia lateral grande con flecha a la foto y destello verde dentro."""
    et = _html.escape(str(texto), quote=False)
    return ('<div class="huellas-scanbadge"><span class="huellas-flecha"></span>'
            f'<span class="huellas-analizada">{et}'
            '<i class="huellas-flash"></i></span></div>')


_PERRO_MARCHA = (
    '<svg viewBox="0 0 48 34" width="40" height="30" aria-hidden="true">'
    '<path d="M12 27 Q5 25 6 17" stroke="{c}" stroke-width="3" fill="none" '
    'stroke-linecap="round"/>'
    '<ellipse cx="20" cy="25" rx="9" ry="7" fill="{c}"/>'
    '<rect x="23" y="25" width="3.4" height="7" rx="1.7" fill="{c}"/>'
    '<circle cx="30" cy="12" r="8" fill="{c}"/>'
    '<ellipse cx="24" cy="6" rx="3" ry="5" fill="{c}" '
    'transform="rotate(-20 24 6)"/>'
    '<ellipse cx="36" cy="14" rx="3" ry="2.5" fill="{c}"/></svg>')

_GATO_MARCHA = (
    '<svg viewBox="0 0 48 34" width="40" height="30" aria-hidden="true">'
    '<path d="M12 27 Q4 25 7 14" stroke="{c}" stroke-width="3" fill="none" '
    'stroke-linecap="round"/>'
    '<ellipse cx="19" cy="25" rx="8" ry="7" fill="{c}"/>'
    '<rect x="21" y="25" width="3.2" height="7" rx="1.6" fill="{c}"/>'
    '<circle cx="30" cy="12" r="7" fill="{c}"/>'
    '<path d="M24 8 L23 1 L28.5 5.5 Z" fill="{c}"/>'
    '<path d="M32.5 6.5 L35 0 L37 6 Z" fill="{c}"/></svg>')


def build_marcha_html(invertida: bool = False) -> str:
    """Tira de gatitos y perritos trotando en fila (solo CSS, bucle infinito).

    Miran a la derecha y avanzan hacia delante (`-50%→0`). Con
    `invertida=True` van hacia la izquierda (figuras espejadas, `0→-50%`).
    Pista de 6 manadas (la mitad idéntica a la otra) para que nunca se
    vacíe ningún lado aunque el sidebar sea ancho. Cada figura trota con
    retardo escalonado. Paleta de la web: negro y rojo alternos.
    """
    manada = [(_PERRO_MARCHA.format(c="#23201B"), 0.0),
              (_GATO_MARCHA.format(c="#E30613"), 0.12),
              (_PERRO_MARCHA.format(c="#E30613"), 0.24),
              (_GATO_MARCHA.format(c="#23201B"), 0.36)]
    pack = "".join(
        f'<span class="huellas-pet" style="animation-delay:{d}s">{svg}</span>'
        for svg, d in manada)
    mitad = pack * 3
    cls = "huellas-march inv" if invertida else "huellas-march"
    return (f'<div class="{cls}" aria-hidden="true">'
            f'<div class="huellas-track">{mitad}{mitad}</div></div>')


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


def titulo_corto(a: dict) -> str:
    """'Especie · color' para tarjetas (p. ej. 'Perro · marrón')."""
    return _titulo(a)


def dias_entre(iso_desde, iso_hasta) -> int:
    """Días enteros entre dos ISO (0 si falla o es negativo)."""
    from datetime import datetime

    try:
        a = datetime.fromisoformat(str(iso_desde))
        b = datetime.fromisoformat(str(iso_hasta))
        return max(0, (b.date() - a.date()).days)
    except (ValueError, TypeError, AttributeError):
        return 0


def texto_dias_casa(n: int) -> str:
    """'Volvió a casa tras N días' (casos 0 y 1 cuidados)."""
    n = max(0, int(n))
    if n == 0:
        return "Volvió a casa el mismo día"
    if n == 1:
        return "Volvió a casa tras 1 día"
    return f"Volvió a casa tras {n} días"


def build_revision_html() -> str:
    """Bloque 'En revisión' con puntos animados (reutiliza dots)."""
    return (
        '<div class="huellas-cruce">En revisión'
        '<span class="huellas-dots"><span></span><span></span><span></span></span>'
        '</div>'
    )


def build_fiesta_html() -> str:
    """Celebración de reencuentro: timeline + sello (los corazones los pone la app).

    Nodos con rebote escalonado, líneas que se dibujan y sello que cae.
    Sin contacto por construcción.
    """
    return (
        '<div class="huellas-fiesta">'
        '<div class="huellas-tl">'
        '<div class="huellas-nodo n1"><span>Perdido</span></div>'
        '<div class="huellas-tl-linea l1"></div>'
        '<div class="huellas-nodo n2"><span>Encontrado</span></div>'
        '<div class="huellas-tl-linea l2"></div>'
        '<div class="huellas-nodo n3"><span>En casa</span></div>'
        '</div>'
        '<div class="huellas-sello">Volvió a casa</div>'
        '</div>'
    )


def build_cerrado_card_html(foto_uri: str, titulo: str, dias_txt: str,
                            idx: int = 0, marca=None,
                            marca_clase: str = "verde", pie=None, nota=None,
                            estado: str = "cerrada", foto2_uri: str = "") -> str:
    """Tarjeta de caso: marca, fotos lado a lado, 'Especie · color', nota y pie.

    Cerrada: llueven corazones + corazón latiendo. En revisión: solo ruleta.
    `foto2_uri` (foto del aviso) va junto a la foto del reencuentro.
    """
    titulo_e = _html.escape(str(titulo), quote=False)
    dias_e = _html.escape(str(dias_txt), quote=False)
    def _foto(u: str) -> str:
        u = str(u or "")
        if u.startswith("data:image"):
            return f'<img src="{_html.escape(u, quote=True)}" alt="{titulo_e}" loading="lazy">'
        inicial = _html.escape((titulo_e[:1] or "H").upper(), quote=False)
        return f'<div class="huellas-cd-ph" aria-hidden="true">{inicial}</div>'

    foto = _foto(foto_uri)
    foto2 = _foto(foto2_uri) if str(foto2_uri or "") else ""
    marca_html = ""
    if marca:
        mc = "".join(c if c.isalnum() else "" for c in str(marca_clase)) or "verde"
        marca_html = (f'<div><span class="huellas-marca {mc}">'
                      f'{_html.escape(str(marca), quote=False)}</span></div>')
    nota_html = ""
    if (nota or "").strip():
        nota_html = (f'<div class="huellas-cerrado-nota">'
                     f'{_html.escape(str(nota).strip(), quote=False)}</div>')
    pie_html = ""
    if pie:
        pie_html = (f'<div class="huellas-cerrado-pie">'
                    f'{_html.escape(str(pie), quote=False)}</div>')
    if estado == "revision":
        final = '<div class="huellas-spinner"></div>'
        lluvia = ""
    else:
        corazones = "".join(
            f'<svg viewBox="0 0 24 24" width="{12 + (i * 7) % 12}" '
            f'height="{12 + (i * 7) % 12}" aria-hidden="true" '
            f'style="left:{2 + (i * 37) % 94:.1f}%;'
            f'animation-delay:{(i * 53) % 340 / 100:.2f}s">'
            '<path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 '
            '2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 '
            '16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 '
            '21.35z" fill="#E30613"/></svg>'
            for i in range(36))
        lluvia = f'<div class="huellas-lluvia">{corazones}</div>'
        final = ('<svg class="huellas-heart" viewBox="0 0 24 24" width="26" height="26" '
                 'aria-hidden="true"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 '
                 '2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 '
                 '16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" '
                 'fill="#E30613"/></svg>')
    retraso = max(0, int(idx)) * 0.08
    fotos_html = f'<div class="huellas-cerrado-imgs">{foto}{foto2}</div>'
    return (
        f'<div class="huellas-res" style="animation-delay:{retraso:.2f}s">'
        '<div class="huellas-cerrado">'
        f'{lluvia}'
        f'{marca_html}'
        f'{fotos_html}'
        f'<div class="huellas-cerrado-t">{titulo_e}</div>'
        f'{nota_html}'
        f'<div class="huellas-cerrado-d">{dias_e}</div>'
        f'{pie_html}'
        f'{final}'
        '</div></div>'
    )


def build_alt_list(items: list) -> str:
    """Lista con líneas alternas blanca/roja para fondo oscuro. Pura y testeada.

    `items`: [(texto, negrita)]. Sin contacto por construcción.
    """
    out = ['<div class="huellas-alt">']
    for i, (txt, bold) in enumerate(items or []):
        col = "#FFFFFF" if i % 2 == 0 else "#E30613"
        w = "800" if bold else "400"
        out.append(f'<div style="color:{col};font-weight:{w}">'
                   f'{_html.escape(str(txt), quote=False)}</div>')
    return "".join(out) + "</div>"


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


def build_leyenda_html(mostrar_perdidos: bool = True, mostrar_avist: bool = True,
                       n_perd=None, n_av=None) -> str:
    """Franja de leyenda del mapa, con conteos opcionales. Pura y testeada."""
    piezas = ['<span><span style="display:inline-block;width:12px;height:12px;'
              'border-radius:50%;background:#E30613;margin-right:.35rem;"></span>TU CASO</span>']
    if mostrar_perdidos:
        txt = f"PERDIDOS ({int(n_perd)})" if n_perd is not None else "PERDIDOS"
        piezas.append('<span><span style="display:inline-block;width:12px;height:12px;'
                      'border-radius:50%;background:#3388FF;margin-right:.35rem;"></span>'
                      f'{txt}</span>')
    if mostrar_avist:
        txt = f"AVISTAMIENTOS ({int(n_av)})" if n_av is not None else "AVISTAMIENTOS"
        piezas.append('<span><span style="display:inline-block;width:12px;height:12px;'
                      'border-radius:50%;background:#35AC46;margin-right:.35rem;"></span>'
                      f'{txt}</span>')
    piezas.append('<span style="font-weight:400;">PULSA CADA CHINCHETA PARA VER FOTO '
                  'Y DIRECCIÓN.</span>')
    return (
        '<div style="background:#23201B;border-radius:10px;padding:.45rem .9rem;'
        'color:#FFFFFF;font-weight:700;font-size:.75rem;display:flex;gap:1.4rem;'
        'flex-wrap:wrap;align-items:center;margin-top:.4rem;">'
        + "".join(piezas) + '</div>'
    )


def build_counts_html(n_lost: int, n_found: int, n_reenc: int) -> str:
    """3 contadores blancos clicables (?page= → su pestaña). Sin contacto."""
    return (
        '<div class="huellas-counts">'
        f'<a class="huellas-count-link" href="?page=perdidos" target="_self">'
        f'<div class="huellas-count"><div class="huellas-count-v">{int(n_lost)}</div>'
        '<div class="huellas-count-l">perdidos activos</div></div></a>'
        f'<a class="huellas-count-link" href="?page=encontrados" target="_self">'
        f'<div class="huellas-count"><div class="huellas-count-v">{int(n_found)}</div>'
        '<div class="huellas-count-l">avistamientos</div></div></a>'
        f'<a class="huellas-count-link" href="?page=reencuentro" target="_self">'
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
        extra = _html.escape(str(c.get("extra") or ""), quote=False)
        extra_html = ""
        if extra == "En revisión":
            extra_html = ' <span class="huellas-cd-et rev">En revisión</span>'
        elif extra == "Caso cerrado":
            extra_html = ' <span class="huellas-cd-et cerr">Caso cerrado</span>'
        piezas.append(
            # target=_self: misma pestaña si el navegador lo respeta (si no,
            # el enlace igual aterriza directo en el aviso en pestaña nueva).
            f'<a class="huellas-cd-link" href="?aviso={cid}" target="_self">'
            f'<div class="huellas-cd"><div class="huellas-cd-img">{foto}</div>'
            f'<div class="huellas-cd-b"><div class="huellas-cd-t">{titulo}</div>'
            f'<div class="huellas-cd-z">{zona}</div>'
            f'<span class="huellas-cd-et {cls_et}">{et}</span>{extra_html}'
            '</div></div></a>'
        )
    pista = "".join(piezas)
    # Pista con contenido duplicado para bucle continuo translateX(-50%).
    return (f'<div class="huellas-vp"><div class="huellas-trk">{pista}{pista}</div></div>')


def _pergamino_uri(fp: _Path, alto: int = 480) -> str:
    """Data-URI JPEG vertical (conserva proporción, aligera la página)."""
    import base64 as _b64
    import io as _io

    from PIL import Image as _Image

    img = _Image.open(fp).convert("RGB")
    img.thumbnail((694, alto))
    buf = _io.BytesIO()
    img.save(buf, format="JPEG", quality=70)
    return "data:image/jpeg;base64," + _b64.b64encode(buf.getvalue()).decode()


def build_pergaminos_html() -> str:
    """Tres carteles MOST WANTED que se desenrollan por turnos (solo CSS).

    Pura (sin Streamlit ni BD): si faltan las fotos, cadena vacía y la app
    no muestra nada (no rompe).
    """
    piezas = []
    for i, fp in enumerate(sorted(PERG_DIR.glob("pergamino_*.jpg"))[:3]):
        try:
            uri = _pergamino_uri(fp)
        except Exception:
            continue
        piezas.append(
            f'<img src="{uri}" alt="Se busca" style="animation-delay:{i * 4}s">')
    if not piezas:
        return ""
    return ('<div class="huellas-perg" aria-hidden="true">'
            + "".join(piezas) + "</div>")
