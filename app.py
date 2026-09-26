"""HUELLAS — MascotasLost&Found (Jerez de la Frontera).

MVP Streamlit — REQ-09, CU-01..CU-05.
Nunca afirma identidad: solo "posible coincidencia" + aviso legal.
Logo: assets/logo.png si existe (si no, inicial H).
"""
from pathlib import Path

import streamlit as st

from agents import admin as admmod
from agents import db as dbmod
from agents.ingestor import effective_date, normalize_aviso
from agents.matcher import UMBRAL_NOTIF, explain
from agents.notifier import notificar
from agents.vision import get_image_embedding
from rag.embeddings import semantic_similarity
from rag.retrieval import retrieve
import ui_home as _uh
import importlib as _importlib
try:
    # Cloud: el pull trae ficheros nuevos sin reiniciar el proceso; el autoreload
    # re-ejecuta este app.py nuevo con ui_home cacheado (viejo) y el ImportError
    # se quedaba atascado hasta el reboot. Recargar a disco lo autocura.
    _importlib.reload(_uh)
except Exception:
    pass
from ui_home import (
    build_alt_list,
    build_bars_html,
    build_carousel_html,
    badge_lateral_html,
    build_cerrado_card_html,
    build_check_html,
    build_crossing_html,
    build_fiesta_html,
    build_foto_scan_html,
    build_leyenda_html,
    build_match_card_html,
    build_marcha_html,
    build_pen_html,
    build_radar_html,
    build_result_card_html,
    build_revision_html,
    chip_dias_perdido,
    chip_visto,
    contacto_details_html,
    dias_entre,
    dias_perdido,
    texto_dias_casa,
    titulo_corto,
    es_nuevo,
    faltantes_buscar,
    faltantes_publicar,
    fmt_corta,
    make_carousel_thumb,
    nuevo_html,
    select_carousel_items,
)

DB = "data/huellas.db"
LOGO = next((p for p in ("assets/logo.png", "assets/logo.jpg", "assets/logo.jpeg", "assets/logo.webp")
             if Path(p).exists()), None)
FONDO = next((p for p in ("assets/fondo.png", "assets/fondo.jpg", "assets/fondo.jpeg")
              if Path(p).exists()), None)
ANIMAL_ES = {"dog": "Perro", "cat": "Gato", "other": "Otro"}
SIZE_ES = {"small": "Pequeño", "medium": "Mediano", "large": "Grande"}
TAGLINE = "Agente de Búsqueda y Comparativa Visual de Animales Perdidos"
SUBTITLE = "Encuentra a tu mascota entre los avisos de avistamientos en Jerez de la Frontera"

st.set_page_config(page_title="HUELLAS", page_icon=LOGO if LOGO else None, layout="wide",
                   initial_sidebar_state="expanded")


def inject_background():
    """Fondo con el patrón assets/fondo.png en toda la app.

    Velo blanco por encima para que el texto siga legible; si no hay
    archivo, no hace nada (la app funciona igual).
    """
    if not FONDO:
        return
    import base64

    mime = "image/jpeg" if Path(FONDO).suffix.lower() in (".jpg", ".jpeg") else "image/png"
    b64 = base64.b64encode(Path(FONDO).read_bytes()).decode()
    st.markdown(
        f"""<style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Montserrat:wght@700;800&display=swap');
        [data-testid="stAppViewContainer"],
        [data-testid="stSidebar"],
        [data-testid="stHeader"] {{
            font-family: 'Inter', system-ui, sans-serif;
            text-transform: uppercase;
        }}
        [data-testid="stAppViewContainer"] h1,
        [data-testid="stAppViewContainer"] h2,
        [data-testid="stAppViewContainer"] h3,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2 {{
            font-family: 'Montserrat', 'Inter', sans-serif;
            font-weight: 800;
            letter-spacing: 0.03em;
        }}
        .huellas-tagline {{
            font-style: italic;
            font-weight: 600;
        }}
        code, pre {{
            text-transform: none !important;
        }}
        /* Todo en mayúsculas también dentro de campos (solo visual; el valor guardado no cambia) */
        input, textarea,
        div[data-baseweb="select"], div[data-baseweb="select"] *,
        div[data-baseweb="popover"], div[data-baseweb="popover"] *,
        div[data-baseweb="menu"], div[data-baseweb="menu"] * {{
            font-family: 'Inter', system-ui, sans-serif;
            text-transform: uppercase !important;
        }}
        /* El envío va por botón: se oculta el hint flotante "Press Enter..." */
        [data-testid="InputInstructions"] {{
            display: none !important;
        }}
        /* Streamlit 1.64 no tiene i18n: se traducen los textos fijos del uploader */
        [data-testid="stFileUploader"] button,
        [data-testid="stFileUploader"] button * {{
            font-size: 0 !important;
            line-height: 0 !important;
        }}
        [data-testid="stFileUploader"] button::after {{
            content: "SUBIR FOTO";
            font-size: 0.875rem;
            line-height: 1.4;
            font-weight: 600;
        }}
        [data-testid="stFileUploaderDropzoneInstructions"],
        [data-testid="stFileUploaderDropzoneInstructions"] * {{
            font-size: 0 !important;
            line-height: 0 !important;
        }}
        [data-testid="stFileUploaderDropzoneInstructions"]::after {{
            content: "MÁX. 200MB POR ARCHIVO • JPG, PNG";
            font-size: 0.75rem;
            line-height: 1.4;
        }}
        /* El menú del desplegable vive en un portal fuera del contenedor: mayúsculas + Inter también aquí */
        div[data-baseweb="popover"], div[data-baseweb="menu"] {{
            font-family: 'Inter', system-ui, sans-serif;
            text-transform: uppercase;
        }}
        /* Los botones no heredan text-transform: se fuerza */
        [data-testid="stAppViewContainer"] button,
        [data-testid="stSidebar"] button {{
            text-transform: uppercase;
        }}
        /* Cajas de destacados: cuadradas, borde grueso, alto contraste */
        .huellas-stat {{
            background: #000000;
            border: 3px solid #000000;
            border-radius: 0;
            padding: 1rem 0.5rem;
            text-align: center;
        }}
        .huellas-stat-value {{
            font-family: 'Montserrat', 'Inter', sans-serif;
            font-size: 2.1rem;
            font-weight: 800;
            color: #FFFFFF;
            line-height: 1.1;
        }}
        .huellas-stat-label {{
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            color: #F5F1EA;
            margin-top: 0.3rem;
        }}
        .huellas-stat-mini .huellas-stat-value {{
            font-size: 1.4rem;
        }}
        .huellas-stat-side {{
            background: #000000;
            border: 3px solid #000000;
            border-radius: 0;
            padding: .45rem .3rem;
            margin-top: .45rem;
            text-align: center;
        }}
        .huellas-stat-side-v {{
            font-family: 'Montserrat', 'Inter', sans-serif;
            font-size: 1.1rem;
            font-weight: 800;
            color: #FFFFFF;
            line-height: 1.1;
        }}
        .huellas-stat-side-l {{
            font-size: .65rem;
            font-weight: 700;
            letter-spacing: .06em;
            color: #F5F1EA;
            margin-top: .2rem;
        }}
        .huellas-sup {{
            text-align: center;
            font-size: .8rem;
            overflow-wrap: break-word;
            word-break: break-all;
            line-height: 1.5;
            margin-top: .45rem;
        }}
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(255,255,255,0.90), rgba(255,255,255,0.90)),
                        url("data:{mime};base64,{b64}");
            background-size: 480px;
        }}
        [data-testid="stSidebar"] {{
            background: linear-gradient(rgba(255,255,255,0.94), rgba(255,255,255,0.94)),
                        url("data:{mime};base64,{b64}");
            background-size: 380px;
        }}
        [data-testid="stHeader"] {{
            background: linear-gradient(rgba(255,255,255,0.90), rgba(255,255,255,0.90)),
                        url("data:{mime};base64,{b64}");
            background-size: 480px;
        }}
        /* Zonas de interacción: tarjetas oscuras para contraste sobre el patrón claro */
        [data-testid="stSelectbox"],
        [data-testid="stTextInput"],
        [data-testid="stTextArea"],
        [data-testid="stNumberInput"],
        [data-testid="stFileUploader"],
        [data-testid="stSlider"] {{
            background-color: #23201B;
            border: 1.5px solid #57503F;
            border-radius: 10px;
            padding: 0.6rem 0.8rem;
            box-shadow: 0 2px 8px rgba(60, 45, 30, 0.25);
        }}
        [data-testid="stSelectbox"] [data-testid="stWidgetLabel"] p,
        [data-testid="stTextInput"] [data-testid="stWidgetLabel"] p,
        [data-testid="stTextArea"] [data-testid="stWidgetLabel"] p,
        [data-testid="stNumberInput"] [data-testid="stWidgetLabel"] p,
        [data-testid="stFileUploader"] [data-testid="stWidgetLabel"] p,
        [data-testid="stSlider"] [data-testid="stWidgetLabel"] p,
        [data-testid="stSlider"] [data-testid="stTickBarMin"],
        [data-testid="stSlider"] [data-testid="stTickBarMax"] {{
            color: #F5F1EA !important;
        }}
        [data-testid="stExpander"] {{
            background-color: #23201B;
            border: 1.5px solid #57503F;
            border-radius: 10px;
        }}
        [data-testid="stExpander"] summary span,
        [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {{
            color: #F5F1EA !important;
        }}
        [data-testid="stButton"] button[kind="secondary"] {{
            background-color: #23201B;
            border: 1.5px solid #6B6257;
            color: #F5F1EA;
        }}
        [data-testid="stButton"] button[kind="secondary"]:hover {{
            background-color: #353026;
            border-color: #8A7F6A;
            color: #FFFFFF;
        }}
        [data-testid="stDivider"],
        [data-testid="stAppViewContainer"] hr,
        [data-testid="stSidebar"] hr {{
            border: none;
            border-top: 2px solid #23201B !important;
            margin: 1rem 0;
            background: transparent;
            opacity: 1;
        }}
        /* Tarjetas con borde nativo (query, resultados): solo afecta a bloques CON borde */
        [data-testid="stAppViewContainer"] [data-testid="stVerticalBlock"],
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
            border-color: #23201B !important;
        }}
        /* Pestañas: sin doble línea; la activa lleva un único subrayado negro grueso */
        [data-testid="stTabs"] [role="tablist"] {{
            border-bottom: none !important;
        }}
        [data-testid="stTab"] {{
            border-bottom: 3px solid transparent;
        }}
        [data-testid="stTab"][aria-selected="true"] {{
            border-bottom: 3px solid #23201B !important;
            font-weight: 600;
        }}
        /* Apaga el indicador rojo nativo (react-aria SelectionIndicator) */
        [data-testid="stTab"] .react-aria-SelectionIndicator {{
            background-color: transparent !important;
        }}
        /* Iconos casa/sol: grandes y negros */
        [data-testid="stAppViewContainer"] button[aria-label="⌂"],
        [data-testid="stAppViewContainer"] button[aria-label="☀︎"] {{
            font-size: 2rem !important;
            background-color: #000000 !important;
            border: 3px solid #000000 !important;
            color: #FFFFFF !important;
            min-height: 3.2rem;
        }}
        /* Contenido pegado arriba, justo bajo el >> */
        [data-testid="stAppViewContainer"] .block-container {{
            padding-top: 0.2rem !important;
        }}
        /* Fuera el botón de fullscreen de las imágenes */
        [data-testid="stImage"] button {{
            display: none !important;
        }}
        /* El >> de la barra lateral, también negro */
        button[data-testid="stSidebarCollapsedControl"],
        div[data-testid="stSidebarCollapsedControl"] button,
        button[data-testid="stSidebarCollapseButton"],
        div[data-testid="collapsedControl"] button {{
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border-radius: 8px !important;
        }}
        </style>""",
        unsafe_allow_html=True,
    )


inject_background()

_LOGO_IMG = None


def get_logo_img():
    """Logo con el fondo blanco convertido a transparente para fundirse con sidebar/cabecera."""
    global _LOGO_IMG
    if _LOGO_IMG is None and LOGO:
        import numpy as np
        from PIL import Image

        img = Image.open(LOGO).convert("RGBA")
        a = np.array(img)
        blanco = (a[..., 0] > 240) & (a[..., 1] > 240) & (a[..., 2] > 240)
        a[blanco, 3] = 0
        _LOGO_IMG = Image.fromarray(a)
    return _LOGO_IMG


def imagen_cuadrada(path: str, lado: int = 480, fondo=(245, 241, 234)):
    """Foto completa en lienzo cuadrado: misma dimensión sin recortar al animal.

    Letterbox crema (paleta de la web): el animal siempre se ve entero,
    nada de recortes centrales que lo decapiten. Sin caché a propósito:
    si se sustituye la foto, se ve al instante.
    """
    from PIL import Image

    img = Image.open(path).convert("RGB")
    img.thumbnail((lado, lado))
    lienzo = Image.new("RGB", (lado, lado), fondo)
    lienzo.paste(img, ((lado - img.width) // 2, (lado - img.height) // 2))
    return lienzo


def vista_previa(foto, caption: str = "Vista previa", ancho: int = 360):
    """Preview de subida ajustada al ancho sin deformar ni sobredimensionar."""
    from PIL import Image

    img = Image.open(foto).convert("RGB")
    img.thumbnail((ancho, ancho))
    st.image(img, caption=caption, width=min(ancho, img.width))


def show_image(path: str, caption: str = "", width: int = 380, fluido: bool = False):
    """Muestra imagen si existe; si no, placeholder textual (rutas locales ausentes en Cloud).

    `fluido=True` ocupa todo el ancho disponible (sidebar: se adapta plegado o no).
    """
    if path and Path(path).exists():
        try:
            img = imagen_cuadrada(path)
            if fluido:
                st.image(img, caption=caption, use_container_width=True)
            else:
                st.image(img, caption=caption, width=width)
        except Exception:
            if fluido:
                st.image(path, caption=caption, use_container_width=True)
            else:
                st.image(path, caption=caption, width=width)
    else:
        st.info("[ IMAGEN NO DISPONIBLE EN ESTE DESPLIEGUE ]" + (f" {caption}" if caption else ""))


def stat_box(value, label: str, mini: bool = False):
    """Caja de destacado: cuadrada, negra, alto contraste (sustituye a st.metric)."""
    cls = "huellas-stat huellas-stat-mini" if mini else "huellas-stat"
    st.markdown(f'<div class="{cls}"><div class="huellas-stat-value">{value}</div>'
                f'<div class="huellas-stat-label">{label}</div></div>', unsafe_allow_html=True)


def stat_side(value, label: str):
    """Mini-caja compacta para el sidebar (no tapa títulos vecinos)."""
    st.markdown(f'<div class="huellas-stat-side"><div class="huellas-stat-side-v">{value}</div>'
                f'<div class="huellas-stat-side-l">{label}</div></div>', unsafe_allow_html=True)


PULSE_CONFIRM_STYLE = """<style>
div[class*="st-key-confirm_pub"] button::after {
  content:""; position:absolute; inset:-2px; border:2px solid #E30613;
  border-radius:8px; animation:huellas-ring 2s ease-out infinite;
  pointer-events:none;
}
</style>"""

SHAKE_CONFIRM_STYLE = """<style>
div[class*="st-key-confirm_pub"] button { animation:huellas-shake .4s ease 1; }
</style>"""

SHAKE_BUSCAR_STYLE = """<style>
div[class*="st-key-b_buscar"] button { animation:huellas-shake .4s ease 1; }
</style>"""

SHAKE_RE_STYLE = """<style>
div[class*="st-key-re_notif"] button { animation:huellas-shake .4s ease 1; }
</style>"""

VISTA_FIJA_STYLE = """<style>
/* Perdidos/Avistamientos en móvil: algún elemento ensancha la página y la
   vista "baila" a los lados al desplazar. Se recorta el desborde lateral del
   contenedor. Solo se emite en estas dos páginas y solo en móvil (≤640px):
   el resto de páginas y el escritorio quedan intactos. */
@media (max-width:640px) {
  div[data-testid="stAppViewContainer"] .block-container {
    overflow-x:hidden;
    overflow-x:clip;
  }
}
</style>"""

FOTO_PUB_STYLE = """<style>
/* Zona de foto de Publicar: borde discontinuo rojo sobre tarjeta blanca,
   con altura mínima para dar aire (compensa la huella y el caption retirados). */
div[class*="st-key-pub_foto"] [data-testid="stFileUploader"] {
  border:2px dashed #E30613;
  border-radius:12px;
  background:#FFFFFF;
  min-height:190px;
}
</style>"""


def vista_previa_scan(foto):
    """Preview con línea de escaneo roja (~1,5 s) y etiqueta 'Foto analizada'.

    Solo HTML+CSS: la línea barre una vez al montar y la etiqueta aparece con
    retardo 1.5s. Sin caché a propósito (cada subida remonta y re-anima).
    """
    import base64
    import html as _html

    raw = foto.getvalue()
    mime = "image/png" if raw[:8] == b"\x89PNG\r\n\x1a\n" else "image/jpeg"
    b64 = base64.b64encode(raw).decode()
    st.markdown(
        f'<div class="huellas-scanrow">'
        + build_foto_scan_html(f"data:{mime};base64,{b64}",
                               getattr(foto, "name", "tu foto"))
        + badge_lateral_html("Foto analizada") + '</div>',
        unsafe_allow_html=True)


def celebrate_search():
    """Lluvia de lupas y huellas (paleta negro/rojo) al publicar. Solo CSS, efímera."""
    paw = ('<svg viewBox="0 0 100 100" width="{s}" height="{s}">'
           '<g fill="#111111"><ellipse cx="50" cy="66" rx="22" ry="17"/>'
           '<circle cx="24" cy="36" r="10"/><circle cx="41" cy="25" r="10"/>'
           '<circle cx="59" cy="25" r="10"/><circle cx="76" cy="36" r="10"/></g></svg>')
    lupa = ('<svg viewBox="0 0 100 100" width="{s}" height="{s}">'
            '<circle cx="40" cy="40" r="22" fill="none" stroke="#E30613" stroke-width="9"/>'
            '<line x1="57" y1="57" x2="82" y2="82" stroke="#111111" stroke-width="11" '
            'stroke-linecap="round"/></svg>')
    items = [(paw, 70, 6, 0.0), (lupa, 60, 18, 0.2), (paw, 85, 32, 0.4), (lupa, 55, 47, 0.1),
             (paw, 62, 61, 0.5), (lupa, 78, 74, 0.3), (paw, 58, 86, 0.15), (lupa, 66, 93, 0.55)]
    floats = "".join(
        f'<div class="huellas-float" style="left:{x}%;animation-delay:{d}s">{svg.format(s=s)}</div>'
        for svg, s, x, d in items)
    st.markdown(
        """<style>
        .huellas-cele { position: fixed; inset: 0; pointer-events: none; z-index: 9999; overflow: hidden; }
        .huellas-float { position: absolute; bottom: -130px; opacity: 0; animation: huellas-rise 3s ease-out forwards; }
        @keyframes huellas-rise {
            0% { transform: translateY(0) rotate(-8deg); opacity: 0; }
            12% { opacity: 1; }
            100% { transform: translateY(-115vh) rotate(20deg); opacity: 0; }
        }
        </style>"""
        f'<div class="huellas-cele">{floats}</div>', unsafe_allow_html=True)


def get_con():
    return dbmod.connect(DB)


def ensure_db():
    """Conecta y auto-carga el seed si la DB está vacía (Cloud: filesystem efímero)."""
    import json

    con = get_con()
    n = con.execute("SELECT COUNT(*) FROM avisos").fetchone()[0]
    if dbmod.get_seed_version(con) != dbmod.SEED_VERSION or n == 0:
        with st.spinner("Actualizando corpus demo de Jerez…"):
            dbmod.wipe_all(con)
            total = 0
            for folder in ("lost", "found"):
                for fp in sorted(Path("data/seed", folder).glob("*.json")):
                    dbmod.upsert_aviso(con, normalize_aviso(json.loads(fp.read_text(encoding="utf-8"))))
                    total += 1
            dbmod.set_seed_version(con)
        st.toast(f"Seed v{dbmod.SEED_VERSION} cargada: {total} avisos.")
    from agents.vision import backfill_embeddings, sync_seed_embeddings
    backfill_embeddings(con)
    sync_seed_embeddings(con)
    return con


def retirar_alerta_demo(con) -> int:
    """Elimina la fila demo incorrecta (lost_001 → found_001, 0.963).

    El alumno confirmó que no es el mismo gato: la demo se retira y
    Alertas solo mostrará notificaciones reales ≥80%. Se deja traza en
    el log. Trazable a REQ-08.
    """
    try:
        cur = con.execute(
            "DELETE FROM notifications WHERE aviso_id='lost_001' AND candidato_id='found_001'"
            " AND ABS(score - 0.963) < 1e-9")
        con.commit()
        if cur.rowcount:
            try:
                with open("data/notifications.log", "a", encoding="utf-8") as _lf:
                    _lf.write("#demo-referencia retirada: no era el mismo animal\n")
            except OSError:
                pass
        return cur.rowcount
    except Exception:
        return 0


def pin_color(a: dict) -> str:
    """Verde = avistamientos · azul = perdidos activos (el query va en rojo).

    Las destacadas ≥80% se anuncian en el popup, sin cambiar el color.
    """
    return "green" if a.get("type") == "found" else "blue"


PAW_ROJA_SVG = ('<svg viewBox="0 0 100 100" width="26" height="26" aria-hidden="true">'
                '<g fill="#E30613"><ellipse cx="50" cy="66" rx="22" ry="17"/>'
                '<circle cx="24" cy="36" r="10"/><circle cx="41" cy="25" r="10"/>'
                '<circle cx="59" cy="25" r="10"/><circle cx="76" cy="36" r="10"/></g></svg>')


def _boton_inicio(texto: str, caja: bool = False):
    """Botón rojo ⏪ junto al título: vuelve a Inicio (nav_to).

    `caja=True` (viñetas en caja) usa clave propia para 1px extra abajo.
    """
    import hashlib as _hl

    slug = _hl.md5(texto.encode("utf-8")).hexdigest()[:6]
    clave = f"homebox_{slug}" if caja else f"home_{slug}"
    st.button("", icon=":material/fast_rewind:", key=clave,
              help="Volver al inicio", on_click=nav_to, args=("inicio",))


def titulo_barrido(texto: str):
    """Título con barrido rojo continuo sobre letras negras (izq↔der). Solo CSS."""
    import html as _html

    c1, c2 = st.columns([1, 30], gap="medium", vertical_alignment="center")
    with c1:
        _boton_inicio(texto)
    with c2:
        st.markdown(f'<h3 class="huellas-barrido">{_html.escape(texto)}</h3>',
                    unsafe_allow_html=True)


def titulo_perimetro(texto: str):
    """Título en caja con huella roja recorriendo su perímetro (velocidad media)."""
    import html as _html

    c1, c2 = st.columns([1, 30], gap="medium", vertical_alignment="center")
    with c1:
        _boton_inicio(texto, caja=True)
    with c2:
        st.markdown(
            f'<div class="huellas-peri-wrap"><span class="huellas-perimetro">'
            f'{_html.escape(texto)}'
            f'<span class="huellas-perimetro-paw">{PAW_ROJA_SVG}</span></span></div>',
            unsafe_allow_html=True)


def linea_chips_perdido(a: dict):
    """Chip de días perdido (urgencia) + Nuevo si <48 h."""
    piezas = [chip_dias_perdido(dias_perdido(a.get("date_last_seen"),
                                             a.get("date_reported")))]
    if es_nuevo(a.get("date_last_seen"), a.get("date_reported")):
        piezas.append(nuevo_html())
    st.markdown(" ".join(piezas), unsafe_allow_html=True)


def linea_chips_avist(a: dict):
    """Chip neutro 'Visto hace N días' + Nuevo si <48 h."""
    piezas = [chip_visto(dias_perdido(a.get("date_last_seen"),
                                      a.get("date_reported")))]
    if es_nuevo(a.get("date_last_seen"), a.get("date_reported")):
        piezas.append(nuevo_html())
    st.markdown(" ".join(piezas), unsafe_allow_html=True)


def bloque_contacto(a: dict):
    """Contacto oculto tras <details> nativo: fluido al abrir y al cerrar."""
    st.markdown(contacto_details_html(a.get("contact_info")), unsafe_allow_html=True)


def _prev_sel(ids: list, opts: list):
    """Miniaturas de los avisos elegidos (el desplegable no previsualiza al hover)."""
    if not ids:
        return
    cols = st.columns(min(5, len(ids)))
    for cc, sid in zip(cols, ids[:5]):
        with cc:
            sa = next((x for x in opts if x["id"] == sid), None)
            if sa:
                show_image(sa["image_url"], caption=sid, width=120)
    if len(ids) > 5:
        st.caption(f"+{len(ids) - 5} más…")
    st.caption("Vista previa de tu selección (el desplegable no previsualiza "
               "al pasar el cursor).")


def _datos_caso(con, r: dict):
    """Primer aviso del caso + uri de su primera foto + uri del aviso (tarjetas)."""
    av0 = None
    for aid in r["aviso_ids"]:
        try:
            av0 = dbmod.get_aviso(con, aid)
        except Exception:
            av0 = None
        if av0:
            break
    uri = ""
    for fp in r["fotos"][:1]:
        uri = thumb_uri(fp)
        if uri:
            break
    uri_av = thumb_uri(av0["image_url"]) if av0 else ""
    return av0, uri, uri_av


def aplicar_filtros(lista: list, pref: str) -> list:
    """Filtros por animal + color + tamaño (tres columnas). Devuelve la lista filtrada."""
    c1, c2, c3 = st.columns(3)
    with c1:
        f_an = st.selectbox("Filtrar por animal", ["Todos", "Perro", "Gato", "Otro"],
                            key=f"{pref}_animal")
    with c2:
        colores = ["Todos"] + sorted({(a.get("color_primary") or "").strip() for a in lista
                                      if (a.get("color_primary") or "").strip()})
        f_col = st.selectbox("Filtrar por color", colores, key=f"{pref}_color",
                             format_func=lambda c: "Todos" if c == "Todos" else c.capitalize())
    with c3:
        f_sz = st.selectbox("Filtrar por tamaño", ["Todos", "Pequeño", "Mediano", "Grande"],
                            key=f"{pref}_tam")
    inv = {"Todos": None, "Perro": "dog", "Gato": "cat", "Otro": "other"}
    invsz = {"Todos": None, "Pequeño": "small", "Mediano": "medium", "Grande": "large"}
    return [a for a in lista
            if (not inv[f_an] or a["animal"] == inv[f_an])
            and (f_col == "Todos" or (a.get("color_primary") or "") == f_col)
            and (not invsz[f_sz] or a["size"] == invsz[f_sz])]


@st.cache_data(show_spinner=False)
def thumb_uri(path: str) -> str:
    """Miniatura JPEG en base64 para el popup de la chincheta (funciona en Cloud).

    Si la foto no existe, cadena vacía y el popup sale solo con texto.
    """
    try:
        from PIL import Image
        import base64
        import io

        img = Image.open(path).convert("RGB")
        img.thumbnail((240, 240))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=65)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return ""


def popup_html(c: dict, marca: str = "", dist=None) -> str:
    """HTML del popup: foto + datos (la foto faltante no rompe)."""
    uri = thumb_uri(c.get("image_url") or "")
    img = f'<img src="{uri}" width="220"><br>' if uri else ""
    dd = f"<br>{dist} km" if dist is not None else ""
    return (f"<b>{c['id']}{marca}</b><br>{img}"
            f"{animal_tag(c)}<br>{c['location'].get('address_text', '')}{dd}")
    """Verde = encontrados · azul = perdidos activos (el query va en rojo).

    Las destacadas ≥80% se anuncian en el popup, sin cambiar el color.
    """
    return "green" if a.get("type") == "found" else "blue"


def leyenda_mapa(mostrar_perdidos: bool = True, mostrar_avist: bool = True,
                 n_perd=None, n_av=None):
    """Franja de leyenda bajo el mapa (canales visibles + conteos en vivo)."""
    st.markdown(build_leyenda_html(mostrar_perdidos, mostrar_avist, n_perd, n_av),
                unsafe_allow_html=True)


def huella_mapa(con) -> str:
    """Fingerprint de avisos (id+coords+estado): si cambia, el mapa remonta fresco.

    st_folium con clave fija reutiliza el iframe y las chinchetas se quedaban
    viejas al publicar/resolver. Con la huella en la clave, cualquier alta, baja,
    edición o resolución regenera el mapa.
    """
    import hashlib

    try:
        rows = con.execute("SELECT id, lat, lng, status FROM avisos ORDER BY id").fetchall()
        base = "|".join(f"{r['id']}:{r['lat']}:{r['lng']}:{r['status']}" for r in rows)
    except Exception:
        base = "x"
    return hashlib.md5(base.encode()).hexdigest()[:8]


def render_mapa_avistados(q: dict, items: list, key: str, otros_lost: list | None = None,
                          zoom: int = 13):
    """Mapa Leaflet con chinchetas + leyenda en franja debajo.

    Roja = tu mascota · azules = perdidos · verdes = avistamientos.
    Los avisos con la misma ubicación se agrupan (círculo con el nº);
    pulsa para desplegarlos. Cada chincheta lleva foto + datos en el popup
    y marca DESTACADA si ≥80%. Si folium no está, aviso sin romper.
    """
    try:
        import folium
        from folium.plugins import MarkerCluster
        from streamlit_folium import st_folium

        fmap = folium.Map(location=[q["location"]["lat"], q["location"]["lng"]], zoom_start=zoom)
        folium.Marker(
            [q["location"]["lat"], q["location"]["lng"]],
            tooltip=f"TU CASO {q['id']}",
            popup=folium.Popup(popup_html(q, marca=" · TU CASO"), max_width=260),
            icon=folium.Icon(color="red"),
        ).add_to(fmap)
        cl_lost = MarkerCluster(name="Perdidos").add_to(fmap)
        for o in otros_lost or []:
            if o["id"] == q["id"]:
                continue
            folium.Marker(
                [o["location"]["lat"], o["location"]["lng"]],
                tooltip=f"PERDIDO {o['id']}",
                popup=folium.Popup(popup_html(o), max_width=260),
                icon=folium.Icon(color="blue"),
            ).add_to(cl_lost)
        cl_found = MarkerCluster(name="Avistamientos").add_to(fmap)
        for it in items:
            c = it.get("candidato", it)
            score = it.get("score")
            marca = " · DESTACADA" if (score is not None and score >= UMBRAL_NOTIF) else ""
            if score is not None:
                marca += f" · {score*100:.0f}%"
            etiqueta = f"{c['id']}" + (f" {score*100:.0f}%" if score is not None else "")
            folium.Marker(
                [c["location"]["lat"], c["location"]["lng"]],
                tooltip=etiqueta,
                popup=folium.Popup(
                    popup_html(c, marca=marca, dist=it.get("dist_km")), max_width=260),
                icon=folium.Icon(color=pin_color(c)),
            ).add_to(cl_found)
        st_folium(fmap, key=f"{key}_{huella_mapa(con)}", height=450,
                  use_container_width=True)
        tipos = {it.get("candidato", it).get("type") for it in items}
        n_p = sum(1 for it in items if it.get("candidato", it).get("type") == "lost")
        n_p += len(otros_lost or [])
        n_a = sum(1 for it in items if it.get("candidato", it).get("type") == "found")
        leyenda_mapa(mostrar_perdidos=("lost" in tipos or bool(otros_lost)),
                     mostrar_avist=("found" in tipos), n_perd=n_p, n_av=n_a)
    except Exception as e:
        st.caption(f"Mapa no disponible ({e}).")


@st.cache_data(ttl=86400 * 30, show_spinner=False)
def geocode_nominatim(q: str):
    """Calle/número → (lat, lng, nombre) vía Nominatim OSM con sesgo a Jerez.

    Sin dependencias ni claves. Devuelve None si no hay red o no se encuentra.
    Cache 30 días (las direcciones no cambian; evita re-llamar al recargar).
    """
    import json as _json
    import urllib.parse
    import urllib.request

    url = ("https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "json", "limit": 1,
         "viewbox": "-6.25,36.75,-6.00,36.60", "bounded": 0}))
    req = urllib.request.Request(url, headers={"User-Agent": "HUELLAS-EOI-MVP/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            data = _json.loads(r.read().decode("utf-8"))
    except Exception:
        return None
    if not data:
        return None
    return float(data[0]["lat"]), float(data[0]["lon"]), data[0].get("display_name", q)


@st.cache_data(ttl=86400 * 30, show_spinner=False)
def reverse_geocode_nominatim(lat: float, lng: float):
    """Coords → dirección legible vía Nominatim OSM (para autocompletar al clicar).

    Sin dependencias ni claves. Devuelve None si no hay red o no se encuentra.
    Cache 30 días: cada punto solo viaja a la red una vez (el mapa va fluido).
    """
    import urllib.parse
    import urllib.request
    import json as _json

    url = ("https://nominatim.openstreetmap.org/reverse?" + urllib.parse.urlencode(
        {"lat": lat, "lon": lng, "format": "json"}))
    req = urllib.request.Request(url, headers={"User-Agent": "HUELLAS-EOI-MVP/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            data = _json.loads(r.read().decode("utf-8"))
    except Exception:
        return None
    return data.get("display_name")


def animal_tag(a: dict) -> str:
    return (f"{ANIMAL_ES.get(a.get('animal'), a.get('animal'))} · "
            f"{a.get('color_primary')} · {SIZE_ES.get(a.get('size'), a.get('size'))}")


PERRERAS = [
    {"nombre": "CMPA · Centro Municipal de Protección Animal",
     "direccion": "Polígono El Portal, Calle Marruecos s/n (junto a MercaJerez)",
     "contacto": "956 149 533 · info.mascotas@aytojerez.es",
     "nota": "Perrera municipal: recoge vagabundos y gestiona adopciones."},
    {"nombre": "No Me Abandones (protectora)",
     "direccion": "Calle San Salvador 21B, Jerez de la Frontera",
     "contacto": "656 42 13 42 (solo WhatsApp) · info@nomeabandones.org",
     "nota": "Protectora con 20 años de trayectoria: rescates, acogidas y adopciones."},
]

WMO_ES = {0: "Despejado", 1: "Casi despejado", 2: "Intervalos nubosos", 3: "Cubierto",
          45: "Niebla", 48: "Niebla", 51: "Llovizna", 53: "Llovizna", 55: "Llovizna",
          61: "Lluvia", 63: "Lluvia", 65: "Lluvia fuerte", 71: "Nieve", 73: "Nieve",
          77: "Granizo", 80: "Chubascos", 81: "Chubascos", 82: "Chubascos fuertes",
          95: "Tormenta", 96: "Tormenta", 99: "Tormenta"}


@st.cache_data(ttl=1800, show_spinner=False)
def get_tiempo():
    """Meteo actual de Jerez vía Open-Meteo (sin claves). Cache 30 min."""
    import urllib.parse
    import urllib.request
    import json as _json

    url = ("https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode({
        "latitude": 36.6826, "longitude": -6.1376,
        "current": "temperature_2m,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "Europe/Madrid", "forecast_days": 1}))
    req = urllib.request.Request(url, headers={"User-Agent": "HUELLAS-EOI-MVP/1.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return _json.loads(r.read().decode("utf-8"))


def estado_perro(d: dict):
    """Modo de animación del perro según la meteo (sin texto asociado).

    Contento = despejado y suave · calor = 30º o más (jadeo) ·
    lluvia = lloviendo · triste = viento fuerte (35 km/h o más) ·
    frío = 8º o menos (tirita). La nieve también tirita.
    """
    cur = d.get("current") or {}
    t = cur.get("temperature_2m")
    code = cur.get("weather_code", 0)
    viento = cur.get("wind_speed_10m") or 0
    if code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99):
        return ("LLUVIA", "lluvia")
    if code in (71, 73, 75, 77, 85, 86):
        return ("NIEVE", "frio")
    if viento >= 35:
        return ("VIENTO", "triste")
    if t is not None and t >= 30:
        return ("CALOR", "calor")
    if t is not None and t <= 8:
        return ("FRÍO", "frio")
    return ("SOLEADO", "contento")


def es_de_noche(d: dict) -> bool:
    """True de 20:00 a 08:00 con la hora local que trae Open-Meteo."""
    try:
        hora = int(str((d.get("current") or {}).get("time", ""))[11:13])
        return hora >= 20 or hora < 8
    except (TypeError, ValueError):
        return False


def perro_html(modo: str, noche: bool = False) -> str:
    """Perro SVG con animación según el tiempo (y luna de 20:00 a 08:00).

    Solo CSS, sin dependencias. Extras visuales: lluvia, termómetro
    (rojo calor / azul frío) y ráfagas de viento.
    """
    if noche:
        astro = ('<defs><mask id="luna"><rect width="180" height="130" fill="white"/>'
                 '<circle cx="143" cy="22" r="13" fill="black"/></mask></defs>'
                 '<circle cx="150" cy="28" r="15" fill="#E8D98A" mask="url(#luna)"/>'
                 '<circle cx="28" cy="18" r="2" fill="#8A7F6A" class="twinkle"/>'
                 '<circle cx="56" cy="10" r="1.5" fill="#8A7F6A" class="twinkle"/>')
    else:
        astro = ('<circle cx="150" cy="28" r="16" fill="#F5B301"/>'
                 '<g stroke="#F5B301" stroke-width="4" stroke-linecap="round">'
                 '<line x1="150" y1="4" x2="150" y2="10"/><line x1="150" y1="46" x2="150" y2="52"/>'
                 '<line x1="126" y1="28" x2="132" y2="28"/><line x1="168" y1="28" x2="174" y2="28"/></g>')
    extra = astro
    if modo == "lluvia":
        extra += ('<g fill="#3388FF">'
                  '<rect x="30" y="4" width="5" height="16" rx="2" class="lluvia l1"/>'
                  '<rect x="80" y="4" width="5" height="16" rx="2" class="lluvia l2"/>'
                  '<rect x="130" y="4" width="5" height="16" rx="2" class="lluvia l3"/></g>'
                  '<ellipse cx="85" cy="26" rx="46" ry="16" fill="#9AA3AD"/>')
    viento = ('<g stroke="#9AA3AD" stroke-width="4" stroke-linecap="round" fill="none">'
              '<path d="M6 56 q20 -8 40 0 t40 0" class="viento v1"/>'
              '<path d="M6 80 q20 -8 40 0 t40 0" class="viento v2"/>'
              '<path d="M6 104 q20 -8 40 0 t40 0" class="viento v3"/></g>'
              if modo == "triste" else "")
    termo = ""
    if modo == "calor":
        termo = ('<rect x="158" y="60" width="12" height="50" rx="6" fill="#DDDDDD" stroke="#57503F"/>'
                 '<circle cx="164" cy="114" r="10" fill="#E30613"/>'
                 '<rect x="161" y="64" width="6" height="46" fill="#E30613"/>')
    elif modo == "frio":
        termo = ('<rect x="158" y="60" width="12" height="50" rx="6" fill="#DDDDDD" stroke="#57503F"/>'
                 '<circle cx="164" cy="114" r="10" fill="#3388FF"/>'
                 '<rect x="161" y="96" width="6" height="14" fill="#3388FF"/>')
    lengua = ('<ellipse cx="104" cy="98" rx="7" ry="12" fill="#E30613" class="lengua"/>'
              if modo == "calor" else "")
    lagrima = ('<ellipse cx="76" cy="72" rx="4" ry="7" fill="#3388FF" class="lagrima"/>'
               if modo == "triste" else "")
    orejas = 'rotate(-14 62 40)' if modo == "triste" else 'none'
    return f"""<style>
    .perro-wrap {{ text-align: center; }}
    .perro-svg {{ animation: perro-salto 1.6s ease-in-out infinite; }}
    .perro-svg.frio {{ animation: perro-tiritona 0.25s linear infinite; }}
    .perro-cola {{ transform-origin: 30px 78px; animation: perro-cola 0.5s ease-in-out infinite alternate; }}
    .perro-svg.triste .perro-cola {{ animation: none; }}
    @keyframes perro-cola {{ from {{ transform: rotate(-18deg); }} to {{ transform: rotate(24deg); }} }}
    @keyframes perro-salto {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-7px); }} }}
    @keyframes perro-tiritona {{ 0%,100% {{ transform: translateX(-2px); }} 50% {{ transform: translateX(2px); }} }}
    .lengua {{ animation: perro-lengua 0.8s ease-in-out infinite alternate; transform-origin: 104px 88px; }}
    @keyframes perro-lengua {{ from {{ transform: scaleY(1); }} to {{ transform: scaleY(1.35); }} }}
    .lluvia {{ animation: perro-lluvia 0.9s linear infinite; }}
    .l2 {{ animation-delay: 0.3s; }} .l3 {{ animation-delay: 0.6s; }}
    @keyframes perro-lluvia {{ from {{ transform: translateY(-6px); opacity: 0; }} 30% {{ opacity: 1; }} to {{ transform: translateY(14px); opacity: 0; }} }}
    .viento {{ stroke-dasharray: 14 12; animation: perro-viento 0.9s linear infinite; }}
    .v2 {{ animation-delay: 0.3s; }} .v3 {{ animation-delay: 0.6s; }}
    @keyframes perro-viento {{ to {{ stroke-dashoffset: -52; }} }}
    .twinkle {{ animation: perro-tw 1.8s ease-in-out infinite alternate; }}
    @keyframes perro-tw {{ from {{ opacity: 0.25; }} to {{ opacity: 1; }} }}
    </style><div class="perro-wrap"><svg class="perro-svg {modo}" viewBox="0 0 180 130" width="200" height="145">
    {extra}{viento}
    <ellipse cx="85" cy="118" rx="62" ry="7" fill="#000" opacity="0.12"/>
    <ellipse cx="85" cy="92" rx="42" ry="24" fill="#C68A4B"/>
    <circle cx="92" cy="58" r="26" fill="#D89A55"/>
    <ellipse cx="62" cy="40" rx="10" ry="20" fill="#8A5A2B" transform="{orejas}"/>
    <ellipse cx="118" cy="42" rx="10" ry="20" fill="#8A5A2B"/>
    <circle cx="83" cy="54" r="4" fill="#111"/><circle cx="103" cy="54" r="4" fill="#111"/>
    <ellipse cx="93" cy="68" rx="6" ry="5" fill="#111"/>{lengua}{lagrima}
    <path d="M44 84 Q22 78 28 60" stroke="#8A5A2B" stroke-width="9" fill="none" stroke-linecap="round" class="perro-cola"/>
    <rect x="58" y="102" width="12" height="16" rx="5" fill="#8A5A2B"/><rect x="102" y="102" width="12" height="16" rx="5" fill="#8A5A2B"/>
    {termo}
    </svg></div>"""


def toggle_top(nombre: str):
    st.session_state.top_panel = None if st.session_state.get("top_panel") == nombre else nombre


# ── Cabecera (si hay logo con wordmark, no se duplica el título) ──
if LOGO:
    hc1, hc2 = st.columns([2, 5], vertical_alignment="center")
    with hc1:
        st.image(get_logo_img(), width="stretch")
    with hc2:
        st.markdown(f"## {TAGLINE}")
        st.markdown(f'<p class="huellas-tagline">{SUBTITLE}</p>', unsafe_allow_html=True)
else:
    hc1, hc2 = st.columns([1, 6])
    with hc1:
        st.markdown("# H")
    with hc2:
        st.title("HUELLAS")
        st.markdown(f"## {TAGLINE}")
        st.markdown(f'<p class="huellas-tagline">{SUBTITLE}</p>', unsafe_allow_html=True)

con = ensure_db()
retirar_alerta_demo(con)

n_lost = con.execute("SELECT COUNT(*) FROM avisos WHERE status='active' AND type='lost'").fetchone()[0]
n_found = con.execute("SELECT COUNT(*) FROM avisos WHERE status='active' AND type='found'").fetchone()[0]
n_reenc = con.execute("SELECT COUNT(*) FROM reencuentros WHERE estado='validada'").fetchone()[0]
n_total = con.execute("SELECT COUNT(*) FROM avisos").fetchone()[0]

if "page" not in st.session_state:
    st.session_state.page = "inicio"


_PAGES = ("inicio", "buscar", "perdidos", "encontrados", "reencuentro",
          "publicar", "protectoras", "tiempo", "legal")


def nav_to(dest: str):
    # Cambio de sección sin perder filtros: solo cambia la página y limpia el resaltado.
    # Mantiene FUNCIONALIDADES abierta para tener inicio/funciones siempre a mano.
    # Refleja la sección en ?s= para que el botón atrás del navegador pueda volver.
    st.session_state.page = dest
    st.session_state.pop("destacar_id", None)
    st.session_state["side_func"] = True
    for _k in ("page", "aviso"):
        try:
            if _k in st.query_params:
                del st.query_params[_k]
        except Exception:
            pass
    try:
        st.query_params["s"] = dest
    except Exception:
        pass


# Secciones abiertas por defecto (el resto, plegadas).
_SIDE_OPEN_DEFAULT = {"side_func": True}


def _toggle(key: str):
    """Alterna una sección plegable del sidebar (solo FUNCIONALIDADES abre por defecto)."""
    st.session_state[key] = not st.session_state.get(key, _SIDE_OPEN_DEFAULT.get(key, False))


def ir_a_caso(aviso_id: str, tipo: str):
    """Salta al caso del otro lado y lo resalta (botón VER COINCIDENCIA)."""
    st.session_state.destacar_id = aviso_id
    st.session_state.page = "perdidos" if tipo == "lost" else "encontrados"
    st.session_state["side_func"] = True
    try:
        st.query_params["s"] = st.session_state.page
    except Exception:
        pass


def ir_a_publicar_con(q: dict, lado: str):
    """Lleva a PUBLICAR con foto, zona y descriptivos precargados.

    El tipo se infiere del canal: buscar entre avistamientos = perdido,
    buscar entre perdidos = avistamiento.
    """
    loc = q.get("location") or {}
    st.session_state.pub_prefill = {
        "tipo": "lost" if lado == "found" else "found",
        "animal": q.get("animal", "dog"), "color": q.get("color_primary", ""),
        "size": q.get("size", "medium"), "collar": bool(q.get("has_collar")),
        "desc": q.get("description_text") or "",
        "lat": loc.get("lat", 36.6826), "lng": loc.get("lng", -6.1376),
        "addr": loc.get("address_text", ""), "qpath": q.get("image_url", "")}
    st.session_state.pub_init = False
    st.session_state.page = "publicar"
    st.session_state["side_func"] = True
    try:
        st.query_params["s"] = "publicar"
    except Exception:
        pass


def tarjeta_destacada(aid: str) -> bool:
    return st.session_state.get("destacar_id") == aid


# ── Inicio / navegación lateral [REQ-UI-01..06] ──────────────────────
# Solo UI: no toca matching, agentes, RAG ni BD.
_NAV_ACTIVE_MAP = {
    "protectoras": "nav_protectoras",
    "tiempo": "nav_tiempo",
}


def inject_ui_css(active_page: str) -> None:
    """Estilos nav/hero/carrusel/contadores (solo CSS, paleta existente)."""
    base = """<style>
/* Títulos con barrido rojo continuo (Publicar + Buscar): letras negras con
   reflejo rojo que va de izquierda a derecha y viceversa. Solo CSS. */
.huellas-barrido {
  font-family:'Montserrat','Inter',sans-serif !important;
  font-weight:800 !important;
  letter-spacing:0.01em !important;
  font-size:1.35rem !important;
  line-height:1.3 !important;
  margin:0.6rem 0 0.8rem !important;
  /* SIN !important en background/background-size: con !important la base
     ganaría a los keyframes en la cascada y el barrido quedaría congelado. */
  background:linear-gradient(90deg, #23201B 35%, #E30613 50%, #23201B 65%);
  background-size:200% auto;
  -webkit-background-clip:text !important;
  background-clip:text !important;
  -webkit-text-fill-color:transparent !important;
  color:transparent !important;
  animation:huellas-sweep 3.2s ease-in-out infinite !important;
}
@keyframes huellas-sweep {
  0% { background-position:0% center; }
  50% { background-position:100% center; }
  100% { background-position:0% center; }
}
/* Títulos en caja con huella roja recorriendo el perímetro (velocidad media). */
.huellas-peri-wrap { margin:0.6rem 0 0.9rem; }
.huellas-perimetro {
  position:relative !important;
  display:inline-block !important;
  font-family:'Montserrat','Inter',sans-serif !important;
  font-weight:800 !important;
  letter-spacing:0.01em !important;
  font-size:1.35rem !important;
  line-height:1.3 !important;
  color:#23201B !important;
  background:#FFFFFF !important;
  border:2px solid #23201B !important;
  border-radius:10px !important;
  padding:0.45rem 1.1rem !important;
}
.huellas-perimetro-paw {
  position:absolute !important;
  /* SIN !important en top/left (los animan los keyframes): con !important
     la base ganaría en la cascada y la huella quedaría clavada en la esquina. */
  top:-14px;
  left:-14px;
  width:26px !important;
  height:26px !important;
  line-height:0 !important;
  pointer-events:none !important;
  animation:huellas-peri 6s linear infinite !important;
}
@keyframes huellas-peri {
  0% { top:-14px; left:-14px; }
  25% { top:-14px; left:calc(100% - 12px); }
  50% { top:calc(100% - 12px); left:calc(100% - 12px); }
  75% { top:calc(100% - 12px); left:-14px; }
  100% { top:-14px; left:-14px; }
}
/* INICIO: siempre negro, en cualquier pestaña (mismo tamaño que los rojos). */
[data-testid="stSidebar"] .st-key-nav_inicio button {
  border-radius:6px !important;
  border-left:3px solid transparent !important;
  transition:transform .2s, background .2s !important;
  text-align:left;
  background:#23201B !important;
  color:#F5F1EA !important;
  padding:0.95rem 1rem !important;
  font-size:1.08rem !important;
  font-weight:700 !important;
}
[data-testid="stSidebar"] .st-key-nav_inicio button:hover {
  transform:translateX(3px) !important;
  background:#353026 !important;
}
[data-testid="stSidebar"] .st-key-tgl_func button,
[data-testid="stSidebar"] .st-key-tgl_punt button,
[data-testid="stSidebar"] .st-key-tgl_mas button,
[data-testid="stSidebar"] .st-key-tgl_admin button {
  border-radius:6px !important;
  border-left:3px solid transparent !important;
  transition:transform .2s, background .2s !important;
  text-align:left;
  background:#E30613 !important;
  color:#FFFFFF !important;
  padding:0.95rem 1rem !important;
  font-size:1.08rem !important;
  font-weight:700 !important;
}
[data-testid="stSidebar"] .st-key-tgl_func button:hover,
[data-testid="stSidebar"] .st-key-tgl_punt button:hover,
[data-testid="stSidebar"] .st-key-tgl_mas button:hover,
[data-testid="stSidebar"] .st-key-tgl_admin button:hover {
  transform:translateX(3px) !important;
  background:rgba(227,6,19,0.85) !important;
}
/* Botones secundarios: negros y tabulados a la derecha (jerarquía visual). */
[data-testid="stSidebar"] .st-key-nav_publicar_side,
[data-testid="stSidebar"] .st-key-nav_buscar_side,
[data-testid="stSidebar"] .st-key-nav_protectoras,
[data-testid="stSidebar"] .st-key-nav_tiempo,
[data-testid="stSidebar"] .st-key-exp_punt1,
[data-testid="stSidebar"] .st-key-exp_punt2,
[data-testid="stSidebar"] .st-key-exp_mas1,
[data-testid="stSidebar"] .st-key-exp_mas2 {
  margin-left:1.25rem !important;
}
/* Enlaces legibles dentro de los desplegables oscuros. */
[data-testid="stSidebar"] .st-key-exp_mas1 a,
[data-testid="stSidebar"] .st-key-exp_mas2 a {
  color:#E30613 !important;
}

[data-testid="stSidebar"] .st-key-nav_publicar_side button,
[data-testid="stSidebar"] .st-key-nav_buscar_side button,
[data-testid="stSidebar"] .st-key-nav_protectoras button,
[data-testid="stSidebar"] .st-key-nav_tiempo button {
  border-radius:6px !important;
  border-left:3px solid transparent !important;
  transition:transform .2s, background .2s !important;
  text-align:left;
  background:#23201B !important;
  color:#F5F1EA !important;
  padding:0.6rem 0.9rem !important;
  font-size:0.95rem !important;
  font-weight:600 !important;
}
[data-testid="stSidebar"] .st-key-nav_publicar_side button:hover,
[data-testid="stSidebar"] .st-key-nav_buscar_side button:hover,
[data-testid="stSidebar"] .st-key-nav_protectoras button:hover,
[data-testid="stSidebar"] .st-key-nav_tiempo button:hover {
  transform:translateX(3px) !important;
  background:#353026 !important;
}
/* La barra ocupa todo el ancho: menos relleno lateral para los botones. */
section[data-testid="stSidebar"] div.block-container {
  padding-left:0.5rem !important;
  padding-right:0.5rem !important;
}
/* Botones principales más altos y juntos (sin estirado flex). */
[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
  gap:6px !important;
}
[data-testid="stAppViewContainer"] .st-key-hero_publicar button,
[data-testid="stAppViewContainer"] .st-key-hero_buscar button {
  position:relative !important;
  border-radius:6px !important;
  background:#E30613 !important;
  color:#FFFFFF !important;
  border:none !important;
  transition:background .2s !important;
  animation:huellas-beatbox 2.4s ease-in-out infinite !important;
}
@keyframes huellas-beatbox {
  0%,100% { transform:scale(1); }
  50% { transform:scale(.94); }
}
[data-testid="stAppViewContainer"] .st-key-hero_publicar button:hover,
[data-testid="stAppViewContainer"] .st-key-hero_buscar button:hover {
  background:rgba(227,6,19,0.85) !important;
}
[data-testid="stAppViewContainer"] .st-key-hero_publicar button,
[data-testid="stAppViewContainer"] .st-key-hero_buscar button {
  padding:0.9rem 1rem !important;
  font-size:1rem !important;
}
.huellas-hero { padding:0 0 0.15rem; margin-top:-3rem; }
.huellas-title { font-family:'Montserrat','Inter',sans-serif; font-weight:800; color:#23201B; line-height:1.15; letter-spacing:0.01em; font-size:clamp(1.6rem,4vw,2rem); margin:0.1rem 0 0.1rem; }
.huellas-sub { font-size:0.95rem; color:#57503F; margin:0 0 0.9rem; }
.huellas-up { animation:huellas-up .7s ease-out both; }
@keyframes huellas-up { from { opacity:0; transform:translateY(16px); } to { opacity:1; transform:none; } }
em.u { font-style:normal; color:#E30613; position:relative; }
em.u::after { content:""; position:absolute; left:0; bottom:-4px; height:3px; background:#E30613; animation:huellas-ul 4s ease-in-out infinite; }
@keyframes huellas-ul { 0%,15% { width:0; } 45%,85% { width:100%; } 100% { width:0; } }
.huellas-heart { display:inline-block; vertical-align:-3px; animation:huellas-bt 1.4s ease-in-out infinite; }
@keyframes huellas-bt { 0%,100% { transform:scale(1); } 50% { transform:scale(1.25); } }
.huellas-vp { overflow:hidden; padding:4px 0; touch-action:pan-y; }
.huellas-trk { display:flex; width:max-content; animation:huellas-mv 32s linear infinite; }
/* La pausa al pasar el cursor solo en dispositivos con hover real (ratón):
   en táctil el toque deja :hover "enganchado" y el carrusel se quedaba parado. */
@media (hover:hover) and (pointer:fine) {
  .huellas-vp:hover .huellas-trk { animation-play-state:paused; }
}
@keyframes huellas-mv { to { transform:translateX(-50%); } }
.huellas-cd-link { text-decoration:none; color:inherit; }
.huellas-cd { width:150px; flex:none; margin-right:12px; background:#FFFFFF; border:1px solid #57503F; border-radius:10px; overflow:hidden; transition:transform .2s; }
.huellas-cd:hover { transform:translateY(-4px); }
.huellas-cd-img { height:104px; display:flex; align-items:center; justify-content:center; background:#F5F1EA; overflow:hidden; }
.huellas-cd-img img { width:100%; height:100%; object-fit:contain; object-position:center; display:block; background:#F5F1EA; }
.huellas-cd-ph { font-family:'Montserrat','Inter',sans-serif; font-weight:800; font-size:2rem; color:#23201B; }
.huellas-cd-b { padding:9px 10px 10px; }
.huellas-cd-t { font-size:0.82rem; font-weight:700; color:#23201B; }
.huellas-cd-z { font-size:0.75rem; color:#57503F; margin:2px 0 6px; }
.huellas-cd-et { font-size:0.7rem; font-weight:700; padding:2px 8px; border-radius:10px; }
/* Tarjetas del carrusel: ningún subrayado azul en su interior (ni en las
   etiquetas ni en el resto de textos). Se anula en el ancla Y en los
   descendientes porque la línea puede propagarse desde el <a>. */
[data-testid="stAppViewContainer"] a.huellas-cd-link,
[data-testid="stAppViewContainer"] a.huellas-cd-link *,
a.huellas-cd-link, a.huellas-cd-link * { text-decoration:none !important;
  text-decoration-line:none !important;
  border-bottom:none !important; box-shadow:none !important; }
.huellas-cd-et.perd { background:#E30613; color:#FFFFFF; }
.huellas-cd-et.avis { background:#23201B; color:#FFFFFF; }
.huellas-cd-et.rev { background:#E8A100; color:#23201B; }
.huellas-cd-et.cerr { background:#35AC46; color:#FFFFFF; }
.huellas-cd-et.rev, .huellas-cd-et.cerr {
  display:block; margin-top:4px; text-align:center; }
.huellas-vacio { background:#FFFFFF; border:1px solid #57503F; border-radius:10px; padding:1.2rem; text-align:center; }
.huellas-vacio-t { font-weight:800; color:#23201B; margin:0 0 0.3rem; }
.huellas-vacio-s { color:#57503F; margin:0; font-size:0.85rem; }
.huellas-counts { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; padding:14px 0 0; }
.huellas-count-link { text-decoration:none; color:inherit; display:block; border-radius:8px; transition:transform .2s; }
.huellas-count-link:hover { transform:translateY(-3px); }
.huellas-count-link:hover .huellas-count { border-color:#E30613 !important; }
[data-testid="stAppViewContainer"] .st-key-count_perdidos button,
[data-testid="stAppViewContainer"] .st-key-count_encontrados button,
[data-testid="stAppViewContainer"] .st-key-count_reencuentro button {
  background:#FFFFFF !important;
  color:#23201B !important;
  font-weight:800 !important;
  border:1px solid #57503F !important;
  border-radius:8px !important;
  padding:10px 12px !important;
  white-space:pre-line !important;
  text-align:left !important;
  line-height:1.25 !important;
  transition:transform .2s, border-color .2s !important;
}
[data-testid="stAppViewContainer"] .st-key-count_perdidos button:hover,
[data-testid="stAppViewContainer"] .st-key-count_encontrados button:hover,
[data-testid="stAppViewContainer"] .st-key-count_reencuentro button:hover {
  transform:translateY(-3px) !important;
  border-color:#E30613 !important;
}
/* Contadores con velo rojo parpadeante (relleno rojo↔blanco, velocidad media). */
[data-testid="stAppViewContainer"] div[class*="st-key-count_"] button {
  position:relative !important;
  overflow:hidden !important;
}
[data-testid="stAppViewContainer"] div[class*="st-key-count_"] button::after {
  content:"" !important;
  position:absolute !important;
  inset:0 !important;
  border-radius:8px !important;
  background:#E30613 !important;
  /* SIN !important en opacity (la animan los keyframes): con !important la base
     gana en la cascada y el velo quedaría invisible (S76 otra vez). */
  opacity:0;
  animation:huellas-fillblink 1.8s ease-in-out infinite !important;
  pointer-events:none !important;
}
@keyframes huellas-fillblink {
  0%,100% { opacity:0; }
  50% { opacity:.75; }
}
.huellas-count { background:#FFFFFF; border:1px solid #57503F; border-radius:8px; padding:10px 12px; }
.huellas-count-v { font-family:'Montserrat','Inter',sans-serif; font-size:1.4rem; font-weight:800; color:#23201B; }
.huellas-count-l { font-size:0.75rem; color:#57503F; }
/* Entrada en cascada de los campos al cargar cada pestaña (una sola vez,
   60 ms entre campos). Solo hijas directas del bloque principal. */
[data-testid="stAppViewContainer"] div.block-container
  > div[data-testid="stVerticalBlock"] > div {
  animation:huellas-cascade .45s ease-out both;
}
[data-testid="stAppViewContainer"] div.block-container
  > div[data-testid="stVerticalBlock"] > div:nth-child(1) { animation-delay:0s; }
[data-testid="stAppViewContainer"] div.block-container
  > div[data-testid="stVerticalBlock"] > div:nth-child(2) { animation-delay:.06s; }
[data-testid="stAppViewContainer"] div.block-container
  > div[data-testid="stVerticalBlock"] > div:nth-child(3) { animation-delay:.12s; }
[data-testid="stAppViewContainer"] div.block-container
  > div[data-testid="stVerticalBlock"] > div:nth-child(4) { animation-delay:.18s; }
[data-testid="stAppViewContainer"] div.block-container
  > div[data-testid="stVerticalBlock"] > div:nth-child(5) { animation-delay:.24s; }
[data-testid="stAppViewContainer"] div.block-container
  > div[data-testid="stVerticalBlock"] > div:nth-child(6) { animation-delay:.30s; }
[data-testid="stAppViewContainer"] div.block-container
  > div[data-testid="stVerticalBlock"] > div:nth-child(7) { animation-delay:.36s; }
[data-testid="stAppViewContainer"] div.block-container
  > div[data-testid="stVerticalBlock"] > div:nth-child(8) { animation-delay:.42s; }
[data-testid="stAppViewContainer"] div.block-container
  > div[data-testid="stVerticalBlock"] > div:nth-child(9) { animation-delay:.48s; }
[data-testid="stAppViewContainer"] div.block-container
  > div[data-testid="stVerticalBlock"] > div:nth-child(10) { animation-delay:.54s; }
[data-testid="stAppViewContainer"] div.block-container
  > div[data-testid="stVerticalBlock"] > div:nth-child(n+11) { animation-delay:.60s; }
@keyframes huellas-cascade {
  from { opacity:0; transform:translateY(14px); }
  to { opacity:1; transform:none; }
}
/* Huella flotante sobre la zona de foto (sube y baja suave, continuo). */
.huellas-float-paw { display:inline-block; line-height:0; margin-bottom:.2rem;
  animation:huellas-float 2.4s ease-in-out infinite alternate; }
@keyframes huellas-float {
  from { transform:translateY(-4px) rotate(-6deg); }
  to { transform:translateY(6px) rotate(6deg); }
}
/* Vista previa con línea de escaneo roja (~1,5 s) y etiqueta posterior. */
.huellas-scan { position:relative; width:fit-content; max-width:300px;
  border-radius:10px; overflow:hidden; border:1.5px solid #57503F; }
.huellas-scan img { display:block; width:100%; max-width:300px; }
.huellas-scanline { position:absolute; left:0; right:0; top:0; height:3px;
  background:#E30613; box-shadow:0 0 14px 2px rgba(227,6,19,.8);
  animation:huellas-scan 1.5s ease-in-out 1 both; }
@keyframes huellas-scan { from { top:0; } to { top:calc(100% - 3px); } }
.huellas-analizada { display:inline-block; font-weight:800;
  font-size:1.6rem; color:#23201B; background:#FFFFFF;
  border:2px solid #35AC46; border-radius:10px; padding:.9rem 1.8rem;
  position:relative; overflow:hidden;
  opacity:0; animation:huellas-fadein .4s ease 1.5s 1 both; }
/* Flecha roja hacia la foto (con leve impulso) + destello dentro de la insignia. */
.huellas-flecha { display:inline-block; width:110px; height:6px; background:#E30613;
  border-radius:3px; margin-right:1.1rem; position:relative;
  animation:huellas-nudge 1.8s ease-in-out infinite; }
.huellas-flecha::before { content:""; position:absolute; left:-3px; top:50%;
  transform:translateY(-50%); border-right:18px solid #E30613;
  border-top:12px solid transparent; border-bottom:12px solid transparent; }
@keyframes huellas-nudge {
  0%,100% { transform:translateX(0); }
  50% { transform:translateX(-8px); }
}
/* Relleno verde parpadeante sobre la miniatura (ambas fotos, consistente). */
.huellas-flash { position:absolute; inset:0; background:rgba(53,172,70,.22);
  opacity:0; pointer-events:none;
  animation:huellas-flash 1.6s ease-in-out infinite alternate; }
@keyframes huellas-flash { from { opacity:0; } to { opacity:1; } }
/* Fila imagen + etiqueta a la derecha (lado a lado, sin envolver: la
   insignia NO baja debajo aunque la columna sea estrecha). */
.huellas-scanrow { display:flex; gap:.7rem; align-items:center; flex-wrap:nowrap;
  margin-bottom:.6rem; }
.huellas-scanrow .huellas-scan { flex:0 1 240px; min-width:0; max-width:240px; }
.huellas-scanrow .huellas-scan img { width:100%; max-width:100%; }
.huellas-scanrow .huellas-scanbadge { flex:1 1 auto; min-width:0; flex-wrap:nowrap;
  display:flex; align-items:center; justify-content:center; align-self:stretch; }
.huellas-scanrow .huellas-flecha { width:56px; flex:none; margin-right:.55rem; }
.huellas-scanrow .huellas-analizada { font-size:1.05rem; padding:.55rem .9rem; }
/* Móvil: la fila foto+insignia encoge sin desbordar el ancho del panel. */
@media (max-width:480px) {
  .huellas-scanrow .huellas-scan { flex-basis:150px; }
  .huellas-scanrow .huellas-flecha { width:34px; }
  .huellas-scanrow .huellas-analizada { font-size:.95rem; padding:.45rem .6rem; }
}
/* Móvil: Streamlit apila las columnas en vertical y el botón de inicio caía
   ENCIMA del título. Solo en cabeceras con botón home se fuerza la fila y la
   columna del botón se ajusta a su contenido. */
@media (max-width:640px) {
  div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-home"]) {
    flex-direction:row !important;
    flex-wrap:nowrap !important;
  }
  div[data-testid="stColumn"]:has(div[class*="st-key-home"]) {
    flex:0 0 auto !important;
    min-width:0;
  }
}
/* Escritorio: acerca los títulos al botón (el hueco mediano queda excesivo
   en pantalla ancha). Solo vista de navegador PC; el móvil no se toca. */
@media (min-width:641px) {
  div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-home"]) {
    column-gap:0.25rem !important;
  }
}
/* Desfile lateral: gatitos y perritos trotando en fila (bucle infinito).
   Reglas acotadas a .huellas-march: la tira de dígitos (.huellas-track
   suelta) usa display:block y no debe pisarlas. */
.huellas-march { overflow:hidden; margin:.1rem 0 .3rem; }
.huellas-march .huellas-track { display:inline-flex; white-space:nowrap;
  will-change:transform;
  animation:huellas-march 4s linear infinite; }
.huellas-march .huellas-pet { display:inline-block; margin-right:16px;
  animation:huellas-trote .38s ease-in-out infinite alternate; }
@keyframes huellas-march {
  from { transform:translateX(-50%); }
  to { transform:translateX(0); } }
@keyframes huellas-trote {
  from { transform:translateY(0) rotate(-3deg); }
  to { transform:translateY(-3px) rotate(3deg); } }
/* Botón volver al inicio junto a títulos de sección: cuadrado rojo con
   flecha blanca (estilo rewind de la imagen de referencia). */
div[class*="st-key-home"] button {
  background:#E30613 !important;
  border:none !important;
  border-radius:10px !important;
  color:#FFFFFF !important;
  font-size:1.3rem !important;
  padding:.2rem .3rem !important;
  min-height:2.2rem;
}
div[class*="st-key-home"] button:hover {
  background:rgba(227,6,19,0.85) !important;
}
div[class*="st-key-home"] button p,
div[class*="st-key-home"] button span {
  color:#FFFFFF !important;
}
/* El glifo queda ~1px alto respecto a la mitad del texto: se baja el bloque.
   Las viñetas en caja llevan extra (clave homebox_*). OJO: con la columna
   centrada, el padding solo baja la mitad; aquí position+top (exacto). */
div[class*="st-key-home_"] { padding-top:1px; }
div[class*="st-key-homebox_"] { position:relative; top:4px; }
/* Segunda tira en sentido contrario: figuras espejadas (miran a la
   izquierda) y pista al revés (`0→-50%`). */
.huellas-march.inv .huellas-track { animation-direction:reverse; }
.huellas-march.inv .huellas-pet svg { transform:scaleX(-1); }

@keyframes huellas-fadein {
  from { opacity:0; transform:translateY(4px); }
  to { opacity:1; transform:none; }
}
/* Botón Confirmar: la app inyecta el pulso (si completo) o la sacudida
   (si faltan campos) solo cuando toca. Base neutra sin animación. */
div[class*="st-key-confirm_pub"] button { position:relative; }
@keyframes huellas-shake {
  0%,100% { transform:translateX(0); } 20% { transform:translateX(-8px); }
  40% { transform:translateX(8px); } 60% { transform:translateX(-5px); }
  80% { transform:translateX(5px); }
}
/* Bloque de cruce: puntos que rebotan. */
.huellas-cruce { font-weight:800; color:#23201B; background:#FFFFFF;
  border:2px solid #23201B; border-radius:10px; padding:.7rem 1rem; }
.huellas-dots span { display:inline-block; width:9px; height:9px; margin-left:5px;
  border-radius:50%; background:#E30613;
  animation:huellas-bounce 1s ease-in-out infinite; }
.huellas-dots span:nth-child(2) { animation-delay:.15s; }
.huellas-dots span:nth-child(3) { animation-delay:.30s; }
@keyframes huellas-bounce {
  0%,100% { transform:translateY(0); opacity:.5; }
  50% { transform:translateY(-7px); opacity:1; }
}
/* Tarjeta de coincidencia: entra deslizándose; el anillo barre 0→real y los
   dígitos ruedan 0→real con steps(). Los keyframes llevan valores FIJOS
   generados por tarjeta (ver ui_home.build_match_card_html): var()/counter/
   @property fallan en Chromium para este uso y se quedan en 0. */
.huellas-match-card { text-align:center; background:#FFFFFF;
  border:2px solid #23201B; border-radius:12px; padding:1rem;
  animation:huellas-cardin .5s ease-out both; }
@keyframes huellas-cardin {
  from { opacity:0; transform:translateY(18px); }
  to { opacity:1; transform:none; }
}
.huellas-match-t { font-family:'Montserrat','Inter',sans-serif; font-weight:800;
  color:#23201B; font-size:1.1rem; margin-bottom:.5rem; }
.huellas-ringwrap { position:relative; width:150px; margin:0 auto; }
.huellas-ring { width:150px; height:150px; display:block; }
.huellas-ring-bg { fill:none; stroke:#E8E0D2; stroke-width:11; }
.huellas-ring-fg { fill:none; stroke:#E30613; stroke-width:11; stroke-linecap:round;
  stroke-dasharray:100; stroke-dashoffset:100;
  transform:rotate(-90deg); transform-origin:center; }
.huellas-ring-num { position:absolute; inset:0; display:flex; align-items:center;
  justify-content:center; font-family:'Montserrat','Inter',sans-serif;
  font-weight:800; font-size:1.5rem; color:#23201B; }
.huellas-strip { display:inline-block; height:1.4em; line-height:1.4;
  overflow:hidden; vertical-align:middle; }
.huellas-track { display:block; }
.huellas-track > span { display:block; height:1.4em; line-height:1.4; }
.huellas-pctsign { margin-left:.15em; }
.huellas-match-id { margin-top:.5rem; color:#57503F; }
/* Boli escribiendo trazos (relleno del hueco al subir foto, en bucle). */
.huellas-penwrap { background:rgba(255,255,255,0.45);
  border:none; border-radius:12px; padding:.6rem .8rem; margin-top:.6rem; min-height:240px;
  display:flex; align-items:center; }
.huellas-penwrap .huellas-pen { width:100%; }
.huellas-pen { width:100%; height:auto; display:block; }
.huellas-trazo { fill:none; stroke:#57503F; stroke-width:3; stroke-linecap:round;
  stroke-dasharray:100; stroke-dashoffset:100;
  animation:huellas-trazar 3.2s ease-in-out infinite; }
.huellas-trazo.t2 { stroke:#8A7F6A; animation-delay:.5s; }
.huellas-trazo.t3 { stroke:#57503F; animation-delay:1s; }
@keyframes huellas-trazar {
  0% { stroke-dashoffset:100; }
  55% { stroke-dashoffset:0; }
  100% { stroke-dashoffset:0; }
}
.huellas-boli { transform-box:fill-box; transform-origin:center;
  animation:huellas-wob .5s ease-in-out infinite alternate; }
@keyframes huellas-wob {
  from { transform:rotate(-6deg) translateY(0); }
  to { transform:rotate(6deg) translateY(2px); }
}
/* Las fotos del sidebar (admin) nunca desbordan: tope al ancho del panel. */
[data-testid="stSidebar"] [data-testid="stImage"] img {
  max-width:100%;
  height:auto;
}
/* Esquinas de encuadre sobre la miniatura (Buscar). */
.huellas-scan i { position:absolute; width:22px; height:22px; border:3px solid #E30613; }
.huellas-scan .c1 { top:6px; left:6px; border-right:none; border-bottom:none; }
.huellas-scan .c2 { top:6px; right:6px; border-left:none; border-bottom:none; }
.huellas-scan .c3 { bottom:6px; left:6px; border-right:none; border-top:none; }
.huellas-scan .c4 { bottom:6px; right:6px; border-left:none; border-top:none; }
/* Botón Buscar: base neutra (el shake se inyecta solo al fallar). */
div[class*="st-key-b_buscar"] button { position:relative; }
/* Radar mientras se procesa la búsqueda. */
.huellas-radarwrap { text-align:center; background:#FFFFFF;
  border:2px solid #23201B; border-radius:12px; padding:1.2rem; }
.huellas-radar { position:relative; width:120px; height:120px; margin:0 auto;
  border-radius:50%; border:2px solid #23201B; overflow:hidden;
  background:repeating-radial-gradient(circle, rgba(35,32,27,.28) 0 2px, transparent 2px 20px); }
.huellas-radar::before { content:""; position:absolute; inset:0; border-radius:50%;
  background:conic-gradient(from 0deg, rgba(227,6,19,.9), transparent 32%);
  animation:huellas-spin 1.5s linear infinite; }
.huellas-radar::after { content:""; position:absolute; left:50%; top:50%;
  width:10px; height:10px; margin:-5px 0 0 -5px; border-radius:50%; background:#23201B; }
.huellas-ping { position:absolute; width:10px; height:10px; border-radius:50%;
  background:#E30613; animation:huellas-ping 1.5s ease-out infinite; }
.huellas-ping.p1 { left:30%; top:28%; }
.huellas-ping.p2 { left:62%; top:60%; animation-delay:.5s; }
@keyframes huellas-spin { to { transform:rotate(360deg); } }
@keyframes huellas-ping {
  0% { transform:scale(.4); opacity:1; }
  70% { transform:scale(1.5); opacity:.9; }
  100% { transform:scale(2.2); opacity:0; }
}
.huellas-radar-t { margin-top:.7rem; font-weight:800; color:#23201B; }
/* Resultados: envoltorio en cascada (retardo inline 80 ms) + top destacado. */
.huellas-res { animation:huellas-cardin .5s ease-out both; }
.huellas-res-top { border-color:#E30613; position:relative; }
.huellas-res-top::after { content:""; position:absolute; inset:-2px;
  border:2px solid #E30613; border-radius:14px;
  animation:huellas-ring 2s ease-out infinite; pointer-events:none; }
/* Barras Visual/Zona/Texto/Fecha (relleno 600 ms, keyframes fijos por barra). */
.huellas-bars { margin-top:.5rem; }
.huellas-bar-row { display:flex; align-items:center; gap:.5rem; margin:.25rem 0;
  font-size:.8rem; }
.huellas-bar-row > span { width:64px; flex:none; font-weight:700; color:#23201B; }
.huellas-bar { flex:1; height:10px; background:#EFE9DC; border-radius:6px; overflow:hidden; }
.huellas-barfill { height:100%; background:#E30613; border-radius:6px; width:0; }
.huellas-bar-row > b { width:48px; flex:none; text-align:right; color:#23201B; }
/* Confirmación de punto en el mapa: chincheta que cae + anillo pulsante. */
.huellas-pinok { display:flex; align-items:center; gap:.6rem; background:#FFFFFF;
  border:2px solid #23201B; border-radius:10px; padding:.5rem .8rem;
  font-weight:800; color:#23201B; margin-top:.5rem;
  animation:huellas-cardin .4s ease-out both; }
.huellas-pinwrap { position:relative; width:24px; height:24px; flex:none; }
.huellas-pindrop { position:absolute; left:5px; top:2px; width:14px; height:14px;
  background:#E30613; border-radius:50% 50% 50% 0;
  animation:huellas-drop .5s cubic-bezier(.2,1.4,.4,1) both; }
@keyframes huellas-drop {
  from { transform:translateY(-26px) rotate(-45deg); opacity:0; }
  60% { transform:translateY(3px) rotate(-45deg); opacity:1; }
  80% { transform:translateY(-2px) rotate(-45deg); }
  to { transform:translateY(0) rotate(-45deg); opacity:1; }
}
.huellas-pinring { position:absolute; inset:-5px; border:2px solid #E30613;
  border-radius:50%; animation:huellas-ring 1.8s ease-out infinite;
  pointer-events:none; }
/* Chips de días + etiqueta Nuevo + contacto desplegable. */
.huellas-chip { display:inline-block; font-size:.75rem; font-weight:800;
  padding:.2rem .7rem; border-radius:12px; margin:.15rem .25rem .15rem 0; }
.huellas-chip.verde { background:#35AC46; color:#FFFFFF; }
.huellas-chip.ambar { background:#E8A100; color:#23201B; }
.huellas-chip.rojo { background:#E30613; color:#FFFFFF; }
.huellas-chip.neutro { background:#23201B; color:#F5F1EA; }
.huellas-nuevo { display:inline-block; font-size:.75rem; font-weight:800;
  color:#23201B; margin-left:.4rem; white-space:nowrap; }
.huellas-dot { display:inline-block; width:9px; height:9px; border-radius:50%;
  background:#E30613; margin-right:.35rem;
  animation:huellas-dot 1.2s ease-in-out infinite; }
.huellas-dotv { display:inline-block; width:8px; height:8px; border-radius:50%;
  background:#35AC46; margin-right:.4rem;
  animation:huellas-dot 1.6s ease-in-out infinite; }
@keyframes huellas-dot {
  0%,100% { transform:scale(1); opacity:1; }
  50% { transform:scale(1.5); opacity:.55; }
}
.huellas-details summary { cursor:pointer; font-weight:700; color:#23201B;
  list-style:none; }
.huellas-details summary::-webkit-details-marker { display:none; }
.huellas-details summary::before { content:""; display:inline-block; width:0;
  height:0; margin-right:.45rem; border-left:8px solid #E30613;
  border-top:5px solid transparent; border-bottom:5px solid transparent;
  transition:transform .3s ease-out; }
.huellas-details[open] summary::before { transform:rotate(90deg); }
.huellas-details .mas { display:inline; }
.huellas-details .menos { display:none; }
.huellas-details[open] .mas { display:none; }
.huellas-details[open] .menos { display:inline; }
.huellas-details .huellas-slide { display:grid; grid-template-rows:0fr;
  transition:grid-template-rows .3s ease-out; }
.huellas-details[open] .huellas-slide { grid-template-rows:1fr; }
.huellas-slide > div { overflow:hidden; }
/* Foto centrada (Buscar sin insignia lateral). */
.huellas-scancenter { display:flex; justify-content:center; }
/* Botón Notificar reencuentro: base neutra (el shake se inyecta al fallar). */
div[class*="st-key-re_notif"] button { position:relative; }
/* Fiesta de reencuentro: timeline + sello. */
.huellas-fiesta { text-align:center; margin:.4rem 0; }
.huellas-tl { display:flex; align-items:center; justify-content:center; margin:.6rem 0; }
.huellas-nodo { width:86px; height:86px; flex:none; border-radius:50%;
  background:#23201B; color:#F5F1EA; display:flex; align-items:center;
  justify-content:center; font-weight:800; font-size:.8rem; text-align:center;
  opacity:0; animation:huellas-pop .5s cubic-bezier(.2,1.6,.4,1) both; }
.huellas-nodo.n1 { animation-delay:.1s; }
.huellas-nodo.n2 { animation-delay:.6s; }
.huellas-nodo.n3 { animation-delay:1.1s; background:#E30613; color:#FFFFFF; }
@keyframes huellas-pop {
  from { transform:scale(0); opacity:0; }
  to { transform:scale(1); opacity:1; }
}
.huellas-tl-linea { height:4px; width:70px; flex:none; background:#E30613;
  transform:scaleX(0); transform-origin:left center;
  animation:huellas-tl .4s ease-out both; }
.huellas-tl-linea.l1 { animation-delay:.45s; }
.huellas-tl-linea.l2 { animation-delay:.95s; }
@keyframes huellas-tl { to { transform:scaleX(1); } }
.huellas-sello { display:inline-block; margin:.8rem auto 0; padding:.7rem 1.6rem;
  background:#E30613; color:#FFFFFF; font-family:'Montserrat','Inter',sans-serif;
  font-weight:800; font-size:1.4rem; border-radius:10px;
  opacity:0; animation:huellas-sello 1.6s ease 1.4s both; }
@keyframes huellas-sello {
  0% { opacity:0; transform:scale(2.4) rotate(-8deg); }
  60% { opacity:1; transform:scale(1) rotate(-8deg); }
  100% { opacity:1; transform:scale(1) rotate(-8deg); }
}
/* Tarjeta de caso cerrado (translúcida: se ve el fondo de la web). */
.huellas-cerrado { background:rgba(255,255,255,0.55); border:2px solid #23201B;
  border-radius:12px; padding:1rem; text-align:center;
  position:relative; overflow:hidden; }
.huellas-cerrado-nota { font-style:italic; color:#57503F; font-size:.9rem;
  margin-top:.3rem; }
/* Lluvia de corazones en casos cerrados. */
.huellas-lluvia { position:absolute; inset:0; overflow:hidden; pointer-events:none; }
.huellas-lluvia svg { position:absolute; top:-26px;
  animation:huellas-llueve 3.4s linear infinite; }
@keyframes huellas-llueve {
  from { transform:translateY(-30px) rotate(-10deg); opacity:0; }
  12% { opacity:.9; }
  to { transform:translateY(340px) rotate(14deg); opacity:0; }
}
/* Ruleta de carga en casos en revisión. */
.huellas-spinner { width:26px; height:26px; margin:.2rem auto;
  border-radius:50%; border:4px solid #E8E0D2; border-top-color:#E30613;
  animation:huellas-spin 1s linear infinite; }
.huellas-cerrado-img img { width:100%; max-width:300px; border-radius:8px; }
.huellas-cerrado-imgs { display:flex; gap:.6rem; justify-content:center;
  align-items:center; flex-wrap:wrap; }
.huellas-cerrado-imgs img { width:100%; max-width:220px; border-radius:8px; }
.huellas-cerrado-imgs img:only-child { max-width:300px; }
.huellas-cerrado-t { font-family:'Montserrat','Inter',sans-serif; font-weight:800;
  color:#23201B; font-size:1.05rem; margin-top:.5rem; }
.huellas-cerrado-d { color:#57503F; margin:.2rem 0 .4rem; }
.huellas-marca { display:inline-block; font-size:.72rem; font-weight:800;
  padding:.2rem .7rem; border-radius:12px; margin-bottom:.5rem; }
.huellas-marca.verde { background:#35AC46; color:#FFFFFF; }
.huellas-marca.ambar { background:#E8A100; color:#23201B; }
.huellas-cerrado-pie { color:#57503F; font-size:.8rem; margin-top:.4rem; }
.huellas-vacio-heart { text-align:center; margin:.4rem 0; }
/* Guardar como aviso: rebote suave continuo. */
div[class*="st-key-ir_publicar"] button { animation:huellas-bob 2.6s ease-in-out infinite; }
@keyframes huellas-bob {
  0%,100% { transform:translateY(0); }
  50% { transform:translateY(-4px); }
}
/* Check verde que se dibuja solo (sin coincidencias). */
.huellas-okcheck { text-align:center; margin:.6rem 0; }
.huellas-okcheck svg { width:64px; height:64px; fill:none; stroke:#35AC46;
  stroke-width:3.5; stroke-linecap:round; stroke-linejoin:round; }
.huellas-okcheck circle { stroke-dasharray:151; stroke-dashoffset:151;
  animation:huellas-draw .7s ease-out both; }
.huellas-okcheck path { stroke-dasharray:40; stroke-dashoffset:40;
  animation:huellas-draw .45s ease-out .55s both; }
@keyframes huellas-draw { to { stroke-dashoffset:0; } }
@media (prefers-reduced-motion:reduce) {
  .huellas-trk, .huellas-up, .huellas-barrido, .huellas-perimetro-paw,
  [data-testid="stAppViewContainer"] .st-key-hero_publicar button,
  [data-testid="stAppViewContainer"] .st-key-hero_buscar button,
  [data-testid="stAppViewContainer"] div[class*="st-key-count_"] button::after,
  em.u::after, .huellas-heart { animation:none !important; }
  em.u::after { width:100% !important; }
  /* Tanda Publicar con vida: todo queda en su estado final estático. */
  [data-testid="stAppViewContainer"] div.block-container
    > div[data-testid="stVerticalBlock"] > div,
  .huellas-float-paw, .huellas-scanline, .huellas-analizada,
  .huellas-dots span, .huellas-match-card, .huellas-strip, .huellas-ringfill,
  .huellas-trazo, .huellas-boli, .huellas-radar::before, .huellas-ping,
  .huellas-res, .huellas-res-top::after, .huellas-pindrop, .huellas-pinring,
  .huellas-dot, .huellas-dotv, .huellas-pinok, .huellas-flash, .huellas-flecha,
  div[class*="st-key-ir_publicar"] button,
  .huellas-okcheck circle, .huellas-okcheck path,
  div[class*="st-key-confirm_pub"] button,
  div[class*="st-key-confirm_pub"] button::after,
  div[class*="st-key-b_buscar"] button,
  div[class*="st-key-re_notif"] button { animation:none !important; }
  .huellas-march .huellas-track, .huellas-march .huellas-pet { animation:none !important; }
  .huellas-nodo, .huellas-tl-linea, .huellas-sello { animation:none !important; }
  .huellas-nodo, .huellas-sello { opacity:1 !important; }
  .huellas-tl-linea { transform:scaleX(1) !important; }
  .huellas-strip { display:none !important; }
  .huellas-ring-fg { stroke-dashoffset:0 !important; }
  .huellas-trazo { stroke-dashoffset:0 !important; }
  .huellas-lluvia { display:none !important; }
  .huellas-spinner { animation:none !important; }
  .huellas-details .huellas-slide,
  .huellas-details summary::before { transition:none !important; }
  .huellas-analizada, .huellas-okcheck circle,
  .huellas-okcheck path { opacity:1 !important; }
  .huellas-okcheck circle, .huellas-okcheck path { stroke-dashoffset:0 !important; }
}
</style>"""
    key = _NAV_ACTIVE_MAP.get(active_page, "")
    extra = ""
    if key:
        extra = ('<style>[data-testid="stSidebar"] .st-key-' + key
                 + ' button { border-left-color:#FFFFFF !important;'
                 + ' background:#23201B !important; color:#F5F1EA !important; }</style>')
    st.markdown(base + extra, unsafe_allow_html=True)


@st.cache_data(ttl=120, show_spinner=False)
def carousel_thumb(path: str) -> str:
    """Miniatura letterbox crema 300×208 en data URI (animal entero, centrado).

    Delegada en `ui_home.make_carousel_thumb` (pura y testeada en pytest).
    """
    return make_carousel_thumb(path or "")


def get_carousel_cards(con, limit: int = 12) -> list:
    """Tarjetas seguras del carrusel (sin contacto por construcción).

    Los avisos en reencuentros siguen visibles con segunda etiqueta
    (En revisión/Caso cerrado, mismos colores que en reencuentros).
    """
    try:
        rows = con.execute(
            "SELECT id FROM avisos WHERE status='active' AND type IN ('lost','found')"
            " ORDER BY date_reported DESC").fetchall()
    except Exception:
        return []
    avisos = []
    vistos = set()
    for r in rows:
        try:
            a = dbmod.get_aviso(con, r["id"])
        except Exception:
            a = None
        if a:
            avisos.append(a)
            vistos.add(a["id"])
    extra = {}
    try:
        for rc in dbmod.list_reencuentros(con):
            marca = ("revision" if rc["estado"] == "pendiente"
                     else "cerrado" if rc["estado"] == "validada" else None)
            if not marca:
                continue
            for aid in rc["aviso_ids"]:
                extra.setdefault(aid, marca)
                if aid not in vistos:
                    try:
                        a = dbmod.get_aviso(con, aid)
                    except Exception:
                        a = None
                    if a and a.get("type") in ("lost", "found"):
                        avisos.append(a)
                        vistos.add(aid)
    except Exception:
        pass
    cards = []
    for b in select_carousel_items(avisos, limit=limit, extra=extra):
        cards.append({
            "id": b["id"], "titulo": b["titulo"], "zona": b["zona"],
            "etiqueta": b["etiqueta"], "extra": b.get("extra"),
            "img_uri": carousel_thumb(b["image_path"] or ""),
        })
    return cards


def handle_carousel_click(con) -> None:
    """Clic en tarjeta (?aviso=id) → salta a su aviso y lo resalta."""
    try:
        qp = st.query_params
        if "aviso" not in qp:
            return
        aid = str(qp["aviso"])
    except Exception:
        return
    try:
        a = dbmod.get_aviso(con, aid)
    except Exception:
        a = None
    try:
        del st.query_params["aviso"]
    except Exception:
        pass
    if a and a.get("type") in ("lost", "found"):
        st.session_state.destacar_id = aid
        st.session_state.page = "perdidos" if a["type"] == "lost" else "encontrados"
        st.session_state["_aviso_nav"] = True
        st.rerun()


_PAGE_ALIAS = {
    "perdidos": "perdidos",
    "encontrados": "encontrados",
    "reencuentro": "reencuentro",
}


def sync_page_from_url() -> None:
    """El botón atrás/adelante y los deep-links (?s= / ?page=) mandan en la sección.

    Sin ?s= ni ?page= no hace nada (la sesión manda). Tras saltar a un aviso
    (?aviso=) no interfiere: ese handler ya consumió su clave y marcó el flag.
    """
    if st.session_state.pop("_aviso_nav", False):
        return
    try:
        qp = st.query_params
    except Exception:
        return
    dest = None
    try:
        if "s" in qp and str(qp["s"]) in _PAGES:
            dest = str(qp["s"])
        elif "page" in qp and str(qp["page"]) in _PAGE_ALIAS:
            dest = _PAGE_ALIAS[str(qp["page"])]
            try:
                st.query_params["s"] = dest
                del st.query_params["page"]
            except Exception:
                pass
    except Exception:
        return
    if dest and dest != st.session_state.get("page"):
        st.session_state.page = dest
        st.session_state.pop("destacar_id", None)


def render_inicio(con, n_lost: int, n_found: int, n_reenc: int) -> None:
    """Hero + botones grandes + carrusel + contadores [REQ-UI-01/03/05/06]."""
    st.markdown(
        """<style>
        /* Solo inicio: bloques más juntos para subir el contenido tras el hero. */
        [data-testid="stAppViewContainer"] [data-testid="stVerticalBlock"] { gap:0.5rem !important; }
        </style>""",
        unsafe_allow_html=True)
    st.markdown(
        '<div class="huellas-hero">'
        '<h1 class="huellas-title">'
        '<span class="huellas-up" style="display:block">ESTOS PELUDOS</span>'
        '<span class="huellas-up" style="display:block;animation-delay:.25s">QUIEREN VOLVER A '
        '<em class="u">CASA</em> '
        '<svg class="huellas-heart" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">'
        '<path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 '
        '3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 '
        '6.86-8.55 11.54L12 21.35z" fill="#E30613"/></svg>'
        '</span></h1>'
        '<p class="huellas-up huellas-sub" style="animation-delay:.5s">'
        'Mira quién te está esperando. Si reconoces a alguno, avisa.</p>'
        '</div>',
        unsafe_allow_html=True)
    h1, h2 = st.columns(2)
    with h1:
        st.button("Publicar aviso", key="hero_publicar", type="primary",
                  use_container_width=True, on_click=nav_to, args=("publicar",))
    with h2:
        st.button("Búsqueda de coincidencias", key="hero_buscar",
                  type="primary", use_container_width=True,
                  on_click=nav_to, args=("buscar",))
    cards = get_carousel_cards(con)
    st.markdown(build_carousel_html(cards), unsafe_allow_html=True)
    if not cards:
        st.button("Publicar el primer aviso", key="hero_empty_pub", type="primary",
                  use_container_width=True, on_click=nav_to, args=("publicar",))
    # Contadores como botones Streamlit: navegación interna (misma pestaña).
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        st.button(f"{int(n_lost)}\nperdidos activos", key="count_perdidos",
                  use_container_width=True, on_click=nav_to, args=("perdidos",))
    with cc2:
        st.button(f"{int(n_found)}\navistamientos", key="count_encontrados",
                  use_container_width=True, on_click=nav_to, args=("encontrados",))
    with cc3:
        st.button(f"{int(n_reenc)}\nreencuentros", key="count_reencuentro",
                  use_container_width=True, on_click=nav_to, args=("reencuentro",))


def render_protectoras() -> None:
    """Protectoras de Jerez en página principal (mismo contenido del sidebar)."""
    st.subheader("Protectoras")
    for p in PERRERAS:
        with st.container(border=True):
            st.markdown(
                '<div style="background:#000000;border-radius:8px;padding:.5rem .6rem;'
                'color:#FFFFFF;font-weight:800;margin-bottom:.4rem;">'
                f"{p['nombre'].upper()}</div>", unsafe_allow_html=True)
            st.markdown(f"**Dirección:** {p['direccion']}")
            st.markdown(f"**Contacto:** {p['contacto']}")
            st.caption(p["nota"])
    st.info("Animal vagabundo en la calle: avisa a Policía Local o SEPRONA; "
            "el Servicio de Laceros lo traslada al CMPA.")


def render_tiempo() -> None:
    """Tiempo en Jerez con el perro según el tiempo (igual que el panel)."""
    st.subheader("Tiempo en Jerez")
    with st.container(border=True):
        try:
            import streamlit.components.v1 as _components

            d = get_tiempo()
            cur = d.get("current") or {}
            dia = (d.get("daily") or {})
            _, modo = estado_perro(d)
            noche = es_de_noche(d)
            _components.html(perro_html(modo, noche=noche), height=190)
            st.markdown(f"**{WMO_ES.get(cur.get('weather_code', 0), '—')} · "
                        f"{(cur.get('temperature_2m') or 0):.0f}º**")
            st.write(f"- Viento: {(cur.get('wind_speed_10m') or 0):.0f} km/h")
            mx = (dia.get("temperature_2m_max") or [None])[0]
            mn = (dia.get("temperature_2m_min") or [None])[0]
            pv = (dia.get("precipitation_probability_max") or [None])[0]
            if mx is not None:
                st.write(f"- Máx/mín hoy: {mx:.0f}º / {mn:.0f}º")
            if pv is not None:
                st.write(f"- Prob. lluvia: {pv:.0f} %")
            st.caption("Fuente: Open-Meteo (sin claves).")
        except Exception as e:
            st.caption(f"Tiempo no disponible ({e}).")


def render_legal() -> None:
    """Aviso legal en página principal (mismo texto único del sidebar)."""
    st.subheader("Aviso legal")
    st.write("Este análisis no promete una coincidencia inequívoca respecto al animal buscado. "
             "Una imagen no permite confirmar la identidad, verifique en persona.")


# ── UI Inicio: CSS + clics del carrusel (?aviso=) y contadores (?page=) ──
inject_ui_css(st.session_state.get("page", "inicio"))
handle_carousel_click(con)
sync_page_from_url()

# ── Barra lateral (REQ-UI-02 v1.4): 6 elementos en orden ─────────────
with st.sidebar:
    st.button("Inicio", key="nav_inicio", icon=":material/home:",
              use_container_width=True, type="tertiary",
              on_click=nav_to, args=("inicio",))
    st.button("Funcionalidades", key="tgl_func", icon=":material/apps:",
              use_container_width=True, type="tertiary",
              on_click=_toggle, args=("side_func",))
    if st.session_state.get("side_func", True):
        st.button("Publicar aviso", key="nav_publicar_side", type="primary",
                  use_container_width=True, on_click=nav_to, args=("publicar",))
        st.button("Búsqueda de coincidencias", key="nav_buscar_side",
                  type="primary", use_container_width=True,
                  on_click=nav_to, args=("buscar",))
    st.button("Puntualizaciones web", key="tgl_punt", icon=":material/warning:",
              use_container_width=True, type="tertiary",
              on_click=_toggle, args=("side_punt",))
    if st.session_state.get("side_punt", False):
        with st.expander("Cómo puntúa (fórmula cerrada)", expanded=False,
                          key="exp_punt1"):
            st.markdown("**0.55·VISUAL + 0.25·TEXTO + 0.10·TEMPORAL + 0.10·GEO**")
            for _txt in ("≥80% · ALERTA", "VISUAL ≥95% · ALERTA",
                          "≥65% · EN LISTA", "RADIO 15 KM",
                          "VENTANA 30 DÍAS"):
                st.markdown('<div style="background:#000000;border-radius:8px;'
                            'padding:.4rem .2rem;margin-bottom:.4rem;'
                            'text-align:center;color:#FFFFFF;font-weight:800;font-size:.72rem;">'
                            f'{_txt}</div>', unsafe_allow_html=True)
        with st.expander("Aviso legal", expanded=False, key="exp_punt2"):
            st.write("Este análisis no promete una coincidencia inequívoca respecto al animal buscado. "
                     "Una imagen no permite confirmar la identidad, verifique en persona.")
    st.button("Más", key="tgl_mas", icon=":material/add:",
              use_container_width=True, type="tertiary",
              on_click=_toggle, args=("side_mas",))
    if st.session_state.get("side_mas", False):
        with st.expander("Protectoras", key="exp_mas1"):
            for _p in PERRERAS:
                st.markdown(build_alt_list([
                    (_p["nombre"], True),
                    (_p["direccion"], False),
                    (_p["contacto"], False),
                ]), unsafe_allow_html=True)
        with st.expander("Tiempo en Jerez", key="exp_mas2"):
            try:
                import streamlit.components.v1 as _comp

                _td = get_tiempo()
                _cur = _td.get("current") or {}
                _w, _modo = estado_perro(_td)
                _comp.html(perro_html(_modo, es_de_noche(_td)), height=150)
                st.markdown(build_alt_list([
                    (f"{WMO_ES.get(_cur.get('weather_code', 0), '—')} · "
                     f"{(_cur.get('temperature_2m') or 0):.0f}º · {_w}", True),
                    (f"Viento {(_cur.get('wind_speed_10m') or 0):.0f} km/h · Jerez",
                     False),
                ]), unsafe_allow_html=True)
            except Exception as _e:
                st.caption(f"No disponible ({_e}).")
    st.button("Administración", key="tgl_admin", icon=":material/key:",
              use_container_width=True, type="tertiary",
              on_click=_toggle, args=("side_admin",))
    if st.session_state.get("side_admin", False):
        _sa, _adm = st.columns([0.12, 0.88])
        with _adm:
            TIPO_ES = {"todos": "Todos", "lost": "Perdidos", "found": "Avistamientos"}
            ESTADO_ES = {"active": "Activo", "resolved": "Resuelto", "expired": "Expirado"}

            def _expected_pw() -> str:
                try:
                    v = st.secrets.get("ADMIN_PASSWORD", "")
                    if v:
                        return str(v)
                except Exception:
                    pass
                import os
                return os.environ.get("HUELLAS_ADMIN_PASSWORD", "")

            if not _expected_pw():
                st.caption("Administración desactivada en este despliegue: "
                           "configura `ADMIN_PASSWORD` (Secrets de Cloud o "
                           "`.streamlit/secrets.toml` local) o la variable "
                           "`HUELLAS_ADMIN_PASSWORD`.")
            elif not st.session_state.get("admin_ok"):
                pw = st.text_input("Contraseña de administrador", type="password", key="admin_pw")
                if st.button("Entrar"):
                    if admmod.check_password(pw, _expected_pw()):
                        st.session_state.admin_ok = True
                        st.success("Sesión de administrador iniciada.")
                        st.rerun()
                    else:
                        st.error("Contraseña incorrecta.")
            else:
                f_tipo = st.selectbox("Tipo", ["todos", "lost", "found"], key="adm_tipo",
                                      format_func=lambda t: TIPO_ES.get(t, t))
                f_txt = st.text_input("Buscar texto", key="adm_txt")
                if st.button("Salir"):
                    st.session_state.admin_ok = False
                    st.rerun()
                st.subheader("Reencuentros")
                _re_est = st.selectbox(
                    "Reencuentros por estado",
                    ["pendiente", "validada", "rechazada", "todos"],
                    key="adm_re_est",
                    format_func=lambda s: {"pendiente": "Pendientes",
                                           "validada": "Validados",
                                           "rechazada": "Rechazados",
                                           "todos": "Todos"}.get(s, s))
                _reencs = (dbmod.list_reencuentros(con) if _re_est == "todos"
                           else dbmod.list_reencuentros(con, _re_est))
                with st.expander(f"Revisar reencuentros ({len(_reencs)})",
                                 expanded=True):
                    if not _reencs:
                        st.caption("Nada que mostrar con ese filtro.")
                    for r in _reencs:
                        st.markdown(f"**`{r['id']}`** [{r['estado']}] · resuelve "
                                    f"{', '.join(f'`{x}`' for x in r['aviso_ids'])}")
                        if r["nota"]:
                            st.write(r["nota"])
                        for fp in r["fotos"][:2]:
                            show_image(fp, caption="Prueba", fluido=True)
                        if r["estado"] == "pendiente":
                            c_ok, c_no = st.columns(2)
                            with c_ok:
                                if st.button("Validar y cerrar", key=f"rv_ok_{r['id']}",
                                             type="primary"):
                                    for aid in r["aviso_ids"]:
                                        admmod.resolve_aviso(con, aid)
                                    dbmod.set_reencuentro(con, r["id"], "validada")
                                    admmod.log_action(
                                        f"REENCUENTRO {r['id']} validado; "
                                        f"resueltos {', '.join(r['aviso_ids'])}")
                                    st.success("Caso cerrado.")
                                    st.rerun()
                            with c_no:
                                if st.button("Rechazar", key=f"rv_no_{r['id']}"):
                                    dbmod.set_reencuentro(con, r["id"], "rechazada")
                                    admmod.log_action(
                                        f"REENCUENTRO {r['id']} rechazado "
                                        "(posible vandalismo); avisos intactos")
                                    st.info("Rechazado: los avisos siguen activos.")
                                    st.rerun()
                        if st.session_state.get("confirm_renc") == r["id"]:
                            if st.button("Confirmar eliminación", key=f"rc_{r['id']}",
                                         type="primary"):
                                dbmod.delete_reencuentro(con, r["id"])
                                admmod.log_action(
                                    f"REENCUENTRO {r['id']} eliminado "
                                    f"(estaba {r['estado']}); avisos intactos")
                                st.session_state.pop("confirm_renc", None)
                                st.success(f"Reencuentro {r['id']} eliminado.")
                                st.rerun()
                        elif st.button("Eliminar", key=f"rd_{r['id']}"):
                            st.session_state.confirm_renc = r["id"]
                            st.rerun()
                st.subheader("Avisos")
                for a in admmod.list_avisos(con, tipo=f_tipo, texto=f_txt):
                    with st.container(border=True):
                        show_image(a["image_url"], caption=a["id"], fluido=True)
                        st.markdown(f"### {animal_tag(a)}")
                        st.write(f"- Tipo: {TIPO_ES.get(a['type'], a['type'])}")
                        st.write(f"- Estado: {ESTADO_ES.get(a['status'], a['status'])}")
                        st.write(a["description_text"])
                        if st.session_state.get("confirm_del") == a["id"]:
                            if st.button("Confirmar eliminación", key=f"cf_{a['id']}", type="primary"):
                                admmod.delete_aviso(con, a["id"])
                                st.session_state.pop("confirm_del", None)
                                st.success(f"Aviso {a['id']} eliminado.")
                                st.rerun()
                        elif st.button("Eliminar", key=f"del_{a['id']}"):
                            st.session_state.confirm_del = a["id"]
                            st.rerun()
                        if a["status"] == "active" and st.button("Marcar resuelto", key=f"ok_{a['id']}"):
                            admmod.resolve_aviso(con, a["id"])
                            st.success(f"Aviso {a['id']} resuelto.")
                            st.rerun()
                        with st.expander(f"Editar datos · {a['id']}"):
                            e_tipo = st.selectbox("Tipo", ["lost", "found"],
                                                  index=["lost", "found"].index(a["type"]),
                                                  key=f"e_tipo_{a['id']}",
                                                  format_func=lambda t: TIPO_ES.get(t, t))
                            e_animal = st.selectbox("Animal", ["dog", "cat", "other"],
                                                    index=["dog", "cat", "other"].index(a["animal"]),
                                                    key=f"e_an_{a['id']}",
                                                    format_func=lambda x: {"dog": "Perro", "cat": "Gato",
                                                                           "other": "Otro"}.get(x, x))
                            e_breed = st.text_input("Raza aprox.", value=a.get("breed_guess") or "",
                                                    key=f"e_br_{a['id']}")
                            e_c1 = st.text_input("Color principal", value=a.get("color_primary") or "",
                                                 key=f"e_c1_{a['id']}")
                            e_c2 = st.text_input("Color secundario", value=a.get("color_secondary") or "",
                                                 key=f"e_c2_{a['id']}")
                            e_marks = st.text_input("Marcas (separadas por comas)",
                                                    value=", ".join(a.get("markings") or ""),
                                                    key=f"e_mk_{a['id']}")
                            e_size = st.selectbox("Tamaño", ["small", "medium", "large"],
                                                  index=["small", "medium", "large"].index(a["size"]),
                                                  key=f"e_sz_{a['id']}",
                                                  format_func=lambda s: {"small": "Pequeño", "medium": "Mediano",
                                                                         "large": "Grande"}.get(s, s))
                            e_collar = st.checkbox("Lleva collar", value=bool(a.get("has_collar")),
                                                   key=f"e_co_{a['id']}")
                            e_collar_d = st.text_input("Descripción collar",
                                                       value=a.get("collar_description") or "",
                                                       key=f"e_cd_{a['id']}")
                            e_desc = st.text_area("Descripción", value=a.get("description_text") or "",
                                                  key=f"e_de_{a['id']}")
                            e_addr = st.text_input("Dirección",
                                                   value=(a.get("location") or {}).get("address_text") or "",
                                                   key=f"e_ad_{a['id']}")
                            e_status = st.selectbox("Estado", ["active", "resolved", "expired"],
                                                    index=["active", "resolved", "expired"].index(a["status"]),
                                                    key=f"e_st_{a['id']}",
                                                    format_func=lambda s: ESTADO_ES.get(s, s))
                            e_rep = st.text_input("Fecha reporte (ISO)",
                                                  value=a.get("date_reported") or "",
                                                  key=f"e_rp_{a['id']}")
                            e_seen = st.text_input("Visto por última vez (ISO, vacío=ninguna)",
                                                   value=a.get("date_last_seen") or "",
                                                   key=f"e_ls_{a['id']}")
                            if st.button("Guardar cambios", key=f"e_sv_{a['id']}", type="primary"):
                                try:
                                    from agents.ingestor import validate_aviso

                                    nuevo = dict(a)
                                    nuevo.update({
                                        "type": e_tipo, "animal": e_animal,
                                        "breed_guess": (e_breed.strip() or None) if e_animal != "other" else None,
                                        "color_primary": e_c1.strip().lower(),
                                        "color_secondary": e_c2.strip().lower() or None,
                                        "markings": [m.strip().lower() for m in e_marks.split(",") if m.strip()],
                                        "size": e_size, "has_collar": bool(e_collar),
                                        "collar_description": e_collar_d.strip() or None,
                                        "description_text": e_desc.strip(), "status": e_status,
                                        "date_reported": e_rep.strip(),
                                        "date_last_seen": e_seen.strip() or None})
                                    nuevo["location"] = dict(a.get("location") or {},
                                                             address_text=e_addr.strip() or None)
                                    errs = validate_aviso(nuevo)
                                    if errs:
                                        st.error("Revisa: " + "; ".join(errs))
                                    else:
                                        campos = ("type", "animal", "breed_guess", "color_primary",
                                                  "color_secondary", "markings", "size", "has_collar",
                                                  "collar_description", "description_text", "status",
                                                  "date_reported", "date_last_seen")
                                        cambiados = [k for k in campos if nuevo.get(k) != a.get(k)]
                                        if (nuevo.get("location") or {}).get("address_text") != (
                                                a.get("location") or {}).get("address_text"):
                                            cambiados.append("address_text")
                                        dbmod.upsert_aviso(con, nuevo)
                                        admmod.log_action(
                                            f"EDIT {a['id']} ({', '.join(cambiados) if cambiados else 'sin cambios'})")
                                        st.success(f"Aviso {a['id']} actualizado.")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                loga = Path("data/admin.log")
                if loga.exists():
                    with st.expander("Ver registro de administración"):
                        st.code(loga.read_text(encoding="utf-8")[-2000:])
    st.divider()
    st.markdown('<div style="text-align:center;font-weight:800;">Métricas rápidas</div>',
                unsafe_allow_html=True)
    try:
        from datetime import datetime as _dtm, timedelta as _tdl

        _hace7 = (_dtm.now().astimezone() - _tdl(days=7)).isoformat()
        _n_sem = con.execute(
            "SELECT COUNT(*) FROM avisos WHERE type='found' "
            "AND status='active' AND date_reported >= ?",
            (_hace7,)).fetchone()[0]
        _todas_lost = [dbmod.get_aviso(con, r["id"]) for r in
                       con.execute("SELECT id FROM avisos WHERE status='active'"
                                   " AND type='lost'").fetchall()]
        _urg = sum(1 for _a in _todas_lost if _a and dias_perdido(
            _a.get("date_last_seen"), _a.get("date_reported")) >= 7)
    except Exception:
        _n_sem, _urg = 0, 0
    stat_side(_n_sem, "Avistamientos 7 días")
    stat_side(_urg, "Casos urgentes ≥7 días")
    st.markdown(
        '<div style="margin-top:.8rem;text-align:center;">'
        '<span class="huellas-dotv"></span>'
        '<span style="font-weight:800;font-size:.72rem;">'
        'Estado del Servicio: Activo (Jerez)</span></div>',
        unsafe_allow_html=True)
    st.divider()
    st.markdown('<div style="text-align:center;font-weight:800;">Soporte</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="huellas-sup">CONTACTO: '
        '<a href="https://instagram.com/mariop.17" style="color:#E30613;">'
        'https://instagram.com/mariop.17</a></div>',
        unsafe_allow_html=True)
    st.markdown(
        '<div class="huellas-sup">Aporta para mantener '
        'los servidores: '
        '<a href="https://paypal.me/mariop1706" style="color:#E30613;">'
        'https://paypal.me/mariop1706</a></div>',
        unsafe_allow_html=True)
    st.divider()
    st.markdown(build_marcha_html(), unsafe_allow_html=True)
    st.markdown(build_marcha_html(invertida=True), unsafe_allow_html=True)

page = st.session_state.get("page", "inicio")

# ── Página: Inicio ────────────────────────────────────────────────────
if page == "inicio":
    render_inicio(con, n_lost, n_found, n_reenc)

# ── Páginas: Protectoras / Tiempo / Aviso legal ───────────────────────
if page == "protectoras":
    render_protectoras()

if page == "tiempo":
    render_tiempo()

if page == "legal":
    render_legal()

# ── Página: Buscar ────────────────────────────────────────────────────
if page == "buscar":
    titulo_barrido("Análisis preliminar de similitudes respecto al registro")
    st.subheader("1. ¿Dónde buscas?")
    lado = st.selectbox("Canal *", ["found", "lost"], key="b_lado", index=None,
                        placeholder="SELECCIONAR",
                        format_func=lambda t: ("Entre avistamientos (perdí mi mascota)"
                                               if t == "found" else
                                               "Entre perdidos (encontré un animal)"
                                               if t == "lost" else "SELECCIONAR"),
                        on_change=lambda: st.session_state.pop("b_search", None))
    # Quien busca es el caso inverso al canal elegido. Sin elegir, se asume
    # perdido (el caso más común) y el mapa ya muestra avistamientos.
    if lado is None:
        st.info("Elige primero dónde buscas para empezar.")
        qtype = "lost"
    else:
        qtype = "lost" if lado == "found" else "found"
    st.subheader("2. Foto actual")
    foto_b = st.file_uploader("Sube una foto de tu mascota *",
                              type=["jpg", "jpeg", "png"], key="b_foto")
    if foto_b:
        import base64 as _b64

        _raw = foto_b.getvalue()
        _mime = "image/png" if _raw[:8] == b"\x89PNG\r\n\x1a\n" else "image/jpeg"
        _uri = f"data:{_mime};base64," + _b64.b64encode(_raw).decode()
        st.markdown('<div class="huellas-scancenter">'
                    + build_foto_scan_html(
                        _uri, getattr(foto_b, "name", "tu foto"), None,
                        esquinas=True)
                    + '</div>',
                    unsafe_allow_html=True)
    else:
        st.caption("Sin foto no hay búsqueda: súbela para empezar.")

    st.subheader("3. Zona")
    with st.container(border=True):
        if "q_lat" not in st.session_state:
            st.session_state.q_lat, st.session_state.q_lon = 36.6826, -6.1376
        if "q_addr_pending" in st.session_state:
            # La dirección del clic se aplica ANTES de instanciar el widget
            # (asignarla después revienta con DuplicateWidgetID).
            st.session_state.q_addr_in = st.session_state.pop("q_addr_pending")
        q_addr = st.text_input("Calle, número y zona", value="Centro, Jerez", key="q_addr_in")
        if st.button("Buscar dirección en el mapa", key="q_geocode"):
            res = geocode_nominatim(q_addr)
            if res:
                st.session_state.q_lat, st.session_state.q_lon = round(res[0], 4), round(res[1], 4)
                st.success(f"Localizada: {res[2][:90]}")
            else:
                st.warning("Dirección no encontrada. Marca el punto en el mapa o ajusta manual.")
        st.caption("O marca el punto clicando 2 veces en el mapa (la dirección se autocompleta)")
        try:
            import folium
            from folium.plugins import MarkerCluster
            from streamlit_folium import st_folium

            fmap = folium.Map(location=[st.session_state.q_lat, st.session_state.q_lon],
                              zoom_start=14)
            folium.Marker([st.session_state.q_lat, st.session_state.q_lon],
                          tooltip="TU ZONA",
                          popup=("TU ZONA · "
                                 f"{st.session_state.get('q_addr_in', '')}"),
                          icon=folium.Icon(color="red")).add_to(fmap)
            # Radio de búsqueda: círculo de 2 km alrededor de tu zona.
            folium.Circle([st.session_state.q_lat, st.session_state.q_lon],
                          radius=2000, color="#E30613", weight=2,
                          fill=True, fill_opacity=0.06).add_to(fmap)
            # El mapa de zona es de referencia: muestra AMBOS lados (perdidos en
            # azul y avistamientos en verde). El cruce sí va solo contra el canal.
            _zona_perd = dbmod.get_active_opuestos(con, "found")
            _zona_av = dbmod.get_active_opuestos(con, "lost")
            cl_perd = MarkerCluster(name="Perdidos").add_to(fmap)
            for c in _zona_perd:
                folium.Marker(
                    [c["location"]["lat"], c["location"]["lng"]],
                    tooltip=c["id"],
                    popup=folium.Popup(popup_html(c), max_width=260),
                    icon=folium.Icon(color=pin_color(c))).add_to(cl_perd)
            cl_av = MarkerCluster(name="Avistamientos").add_to(fmap)
            for c in _zona_av:
                folium.Marker(
                    [c["location"]["lat"], c["location"]["lng"]],
                    tooltip=c["id"],
                    popup=folium.Popup(popup_html(c), max_width=260),
                    icon=folium.Icon(color=pin_color(c))).add_to(cl_av)
            out = st_folium(fmap, key=f"cerca_map_{huella_mapa(con)}",
                            center=(st.session_state.q_lat, st.session_state.q_lon),
                            zoom=14, height=380, use_container_width=True)
            leyenda_mapa(n_perd=len(_zona_perd), n_av=len(_zona_av))
            if out and out.get("last_clicked"):
                nlat = round(out["last_clicked"]["lat"], 4)
                nlng = round(out["last_clicked"]["lng"], 4)
                if (nlat, nlng) != (st.session_state.q_lat, st.session_state.q_lon):
                    st.session_state.q_lat, st.session_state.q_lon = nlat, nlng
                    st.session_state.q_pin_nuevo = True
                    rev = reverse_geocode_nominatim(nlat, nlng)
                    if rev:
                        st.session_state.q_addr_pending = rev[:120]
                    st.rerun()
            if st.session_state.pop("q_pin_nuevo", False):
                # La chincheta "cae" con rebote + anillo pulsante del radio.
                st.markdown(
                    '<div class="huellas-pinok"><span class="huellas-pinwrap">'
                    '<span class="huellas-pinring"></span>'
                    '<span class="huellas-pindrop"></span></span>'
                    f"Punto fijado: {st.session_state.q_lat}, "
                    f"{st.session_state.q_lon} · radio 2 km</div>",
                    unsafe_allow_html=True)
        except Exception as e:
            st.caption(f"Mapa no disponible ({e}). Usa el ajuste manual.")
        st.write(f"- Punto seleccionado: {st.session_state.q_lat}, {st.session_state.q_lon}")
        with st.expander("Ajuste manual de coordenadas"):
            st.number_input("Latitud", format="%.4f", key="q_lat")
            st.number_input("Longitud", format="%.4f", key="q_lon")

    st.subheader("4. Descripción")
    d1, d2 = st.columns(2)
    with d1:
        b_animal = st.selectbox("Animal *", ["dog", "cat", "other"], key="b_animal",
                                index=None, placeholder="SELECCIONAR",
                                format_func=lambda a: {"dog": "Perro", "cat": "Gato",
                                                       "other": "Otro"}.get(a, "SELECCIONAR"))
        b_color = st.text_input("Color principal *", "", key="b_color",
                                placeholder="Ej. marrón")
        b_size = st.selectbox("Tamaño *", ["small", "medium", "large"], key="b_size",
                              index=None, placeholder="SELECCIONAR",
                              format_func=lambda s: {"small": "Pequeño", "medium": "Mediano",
                                                     "large": "Grande"}.get(s, "SELECCIONAR"))
    with d2:
        b_marks = st.text_input("Marcas (separadas por comas)", "", key="b_marks",
                                placeholder="Ej. mancha blanca, cola anillada")
        b_collar = st.checkbox("¿Lleva collar?", False, key="b_collar")
        b_breed = st.text_input("Raza aprox. (opcional)", "", key="b_breed",
                                placeholder="Ej. bodeguero")
    b_desc = st.text_area("Descripción libre *", "", key="b_desc",
                          placeholder="Describe al animal: color, marcas, collar…")

    st.subheader("5. Lanza la búsqueda")
    f1, f2 = st.columns(2)
    with f1:
        umbral_vista = st.slider("Mostrar a partir de este porcentaje de coincidencia", 50, 100, 65,
                                 format="%d %%")
    with f2:
        topn = st.slider("Máx. resultados", 3, 15, 8)
    _b_n = st.session_state.get("b_shake_n", 0)
    if st.session_state.pop("b_shake_pending", False):
        st.markdown(SHAKE_BUSCAR_STYLE, unsafe_allow_html=True)
    if st.session_state.get("b_faltan"):
        st.warning("Te falta: " + ", ".join(st.session_state.pop("b_faltan")) + ".")
    if st.button("Buscar coincidencias", type="primary", key=f"b_buscar_{_b_n}"):
        _bf = faltantes_buscar(lado, bool(foto_b), b_animal, b_size, b_color, b_desc)
        if _bf:
            st.session_state.b_shake_n = _b_n + 1
            st.session_state.b_shake_pending = True
            st.session_state.b_faltan = _bf
            st.rerun()
        else:
            from datetime import datetime as _dt
            import time as _tb

            Path("data/uploads").mkdir(parents=True, exist_ok=True)
            qpath = "data/uploads/_busqueda.jpg"
            Path(qpath).write_bytes(foto_b.getbuffer())
            from agents.vision import embed_candidato, embedida_con_espacio

            radar_box = st.empty()
            with radar_box.container():
                st.markdown(build_radar_html(), unsafe_allow_html=True)
            _t0 = _tb.time()
            try:
                q_emb, espacio = embedida_con_espacio(qpath)
                q = normalize_aviso({
                    "type": qtype, "animal": b_animal,
                    "breed_guess": (b_breed.strip() or None) if b_animal != "other" else None,
                    "color_primary": b_color.strip().lower(), "size": b_size,
                    "has_collar": bool(b_collar), "markings": b_marks,
                    "description_text": b_desc.strip(),
                    "location": {"lat": float(st.session_state.q_lat),
                                 "lng": float(st.session_state.q_lon),
                                 "address_text": st.session_state.get("q_addr_in", "")},
                    "date_reported": _dt.now().astimezone().isoformat(),
                    "image_url": qpath, "contact_info": "", "status": "active"})
                q["image_embedding"] = q_emb
                cands = dbmod.get_active_opuestos(con, qtype)
                matches = retrieve(q, cands,
                                   lambda a, _e=espacio: embed_candidato(a, _e),
                                   semantic_similarity)
            finally:
                _dtb = _tb.time() - _t0
                if _dtb < 1.5:
                    _tb.sleep(1.5 - _dtb)
                radar_box.empty()
            # Preliminar y transitoria: se guarda en sesión para no replegarse,
            # pero no persiste ni escribe alertas (eso nace al publicar).
            st.session_state.b_search = {"q": q, "matches": matches}
            if any(m["notifica"] for m in matches):
                celebrate_search()

    res = st.session_state.get("b_search")
    if res:
        q, matches = res["q"], res["matches"]
        if st.button("Limpiar resultados", key="b_limpiar"):
            st.session_state.pop("b_search", None)
            st.rerun()
        k1, k2 = st.columns(2)
        with k1:
            stat_box(sum(1 for m in matches if m["notifica"]), "Destacadas ≥80%", mini=True)
        with k2:
            stat_box(len(matches), "En lista ≥65%", mini=True)
        visibles = [m for m in matches if m["score"] * 100 >= umbral_vista][:topn]
        if not visibles:
            st.info("Sin candidatos con ese filtro. Baja el umbral de vista o espera nuevos avisos.")
        for idx, m in enumerate(visibles):
            c = m["candidato"]
            badge = "POSIBLE COINCIDENCIA DESTACADA" if m["notifica"] else "Posible coincidencia"
            with st.container(border=True):
                st.markdown(build_result_card_html(
                    c["id"], m["score"], m["dist_km"], badge, idx, top=(idx == 0)),
                    unsafe_allow_html=True)
                st.markdown(build_bars_html(c["id"], m["visual"], m["geo"],
                                            m["texto"], m["temporal"]),
                            unsafe_allow_html=True)
                r1, r2 = st.columns(2)
                with r1:
                    show_image(q["image_url"], caption="Tu foto")
                    with r2:
                        show_image(c["image_url"], caption=f"{'Avistamiento' if c['type'] == 'found' else 'Perdido'} · {c['id']}")
                        st.write(c["description_text"])
                    with st.expander("Por qué este resultado"):
                        s1, s2, s3, s4 = st.columns(4)
                        with s1:
                            stat_box(f"{m['visual']:.2f}", "Visual", mini=True)
                        with s2:
                            stat_box(f"{m['texto']:.2f}", "Texto", mini=True)
                        with s3:
                            stat_box(f"{m['temporal']:.2f}", "Tiempo", mini=True)
                        with s4:
                            stat_box(f"{m['geo']:.2f}", "Geo", mini=True)
                        st.code(explain(m))
        if visibles:
            st.subheader("Mapa de candidatos")
            st.caption(("Verdes: avistamientos (DESTACADA si ≥80%) · roja: tu caso."
                        if q["type"] == "lost" else
                        "Azules: perdidos (DESTACADA si ≥80%) · roja: tu caso."))
            render_mapa_avistados(q, visibles, key="res_map")
        destacados = [m for m in matches if m["notifica"]]
        if destacados:
            top = destacados[0]
            with st.container(border=True):
                st.markdown(f"### ¡Posible coincidencia! `{top['candidato_id']}` · "
                            f"**{top['score']*100:.1f}%**")
                _tc = dbmod.get_aviso(con, top["candidato_id"])
                st.button("Ver coincidencia", key="ver_co_busqueda", type="primary",
                          use_container_width=True, on_click=ir_a_caso,
                          args=(top["candidato_id"], (_tc or {}).get("type", "found")))
        st.divider()
        if visibles:
            st.subheader("¿No es ninguno? Publícalo")
            st.caption("Hayas encontrado o no coincidencia, desde aquí publicas el aviso "
                       "(de perdido o de avistamiento, lo decides allí).")
        else:
            st.subheader("Sin coincidencias por ahora")
            st.caption("Guarda tu aviso y te avisaremos si aparece algo compatible.")
        st.button("Guardar como aviso", key="ir_publicar", type="primary",
                  use_container_width=True, on_click=ir_a_publicar_con, args=(q, lado))

# ── Página: Perdidos activos ──────────────────────────────────────────
if page == "perdidos":
    titulo_perimetro("Mascotas desaparecidas")
    st.markdown(VISTA_FIJA_STYLE, unsafe_allow_html=True)
    lost_list = [dbmod.get_aviso(con, r["id"]) for r in
                 con.execute("SELECT id FROM avisos WHERE status='active' AND type='lost'").fetchall()]
    lost_list = [a for a in lost_list if a]
    if not lost_list:
        st.info("No hay mascotas desaparecidas.")
    else:
        lista_p = aplicar_filtros(lost_list, "lost")
        stat_box(len(lista_p), "Mascotas desaparecidas")
        lista_p.sort(key=lambda a: 0 if tarjeta_destacada(a["id"]) else 1)
        for a in lista_p:
            with st.container(border=True):
                if tarjeta_destacada(a["id"]):
                    st.markdown("**COINCIDENCIA DE TU BÚSQUEDA**")
                c1, c2 = st.columns([1, 1])
                with c1:
                    show_image(a["image_url"], caption=f"Foto · {a['id']}", fluido=True)
                with c2:
                    st.markdown(f"### {animal_tag(a)}")
                    linea_chips_perdido(a)
                    st.write(a["description_text"])
                    st.write(f"- Collar: {'sí' if a['has_collar'] else 'no'}")
                    st.write(f"- Visto: {fmt_corta(effective_date(a))}")
                    st.write(f"- {a['location'].get('address_text', '')}")
                    bloque_contacto(a)

# ── Página: Encontrados ───────────────────────────────────────────────
if page == "encontrados":
    titulo_perimetro("Rastros compartidos")
    st.markdown(VISTA_FIJA_STYLE, unsafe_allow_html=True)
    found = dbmod.get_active_opuestos(con, "lost")
    if not found:
        st.info("Aún no hay rastros compartidos.")
    else:
        lista = aplicar_filtros(found, "found")
        stat_box(len(lista), "Rastros compartidos")
        lista.sort(key=lambda a: 0 if tarjeta_destacada(a["id"]) else 1)
        for a in lista:
            with st.container(border=True):
                if tarjeta_destacada(a["id"]):
                    st.markdown("**COINCIDENCIA DE TU BÚSQUEDA**")
                c1, c2 = st.columns([1, 1])
                with c1:
                    show_image(a["image_url"], caption=f"Foto · {a['id']}", fluido=True)
                with c2:
                    st.markdown(f"### {animal_tag(a)}")
                    linea_chips_avist(a)
                    st.write(a["description_text"])
                    st.write(f"- Collar: {'sí' if a['has_collar'] else 'no'}")
                    st.write(f"- Visto: {fmt_corta(effective_date(a))}")
                    st.write(f"- {a['location'].get('address_text', '')}")
                    bloque_contacto(a)

# ── Página: Publicar ──────────────────────────────────────────────────
if page == "publicar":
    titulo_barrido("Publica un aviso de perdido o avistamiento")
    # Banner del último aviso publicado (tras el rerun que refresca métricas):
    # repite el resultado del cruce para no perderlo con la recarga.
    _pub_res = st.session_state.get("pub_result")
    if _pub_res:
        st.success(f"Aviso `{_pub_res['aviso_id']}` publicado.")
        if _pub_res.get("top_id"):
            if not _pub_res.get("visto"):
                celebrate_search()
                _pub_res["visto"] = True
            st.success(f"Cruce automático: {_pub_res['n']} alerta(s) ≥80%.")
            st.markdown(build_match_card_html(_pub_res["top_id"], _pub_res["top_score"]),
                        unsafe_allow_html=True)
            st.button("Ver aviso y contactar", key=f"ver_co_{_pub_res['aviso_id']}_r",
                      type="primary", use_container_width=True,
                      on_click=ir_a_caso,
                      args=(_pub_res["top_id"], _pub_res.get("top_tipo", "found")))
        elif _pub_res.get("cruce_error"):
            st.caption(f"Cruce automático no disponible ({_pub_res['cruce_error']}).")
        else:
            st.markdown(build_check_html(), unsafe_allow_html=True)
            st.info("Cruce automático: sin coincidencias ≥80% por ahora. "
                    "Te avisaremos si aparece algo.")
        if st.button("Publicar otro aviso", key="pub_otro"):
            st.session_state.pop("pub_result", None)
            st.rerun()
        st.divider()
    # Los widgets se borran rotando la época (el navegador restaura valores
    # aunque se vacíe su clave: solo una clave nueva garantiza un campo limpio).
    _pe = st.session_state.get("pub_epoch", 0)
    pre = st.session_state.get("pub_prefill") or {}
    if pre and not st.session_state.get("pub_init"):
        st.session_state[f"pub_tipo_{_pe}"] = pre.get("tipo", "lost")
        st.session_state[f"pub_animal_{_pe}"] = pre.get("animal", "dog")
        st.session_state[f"pub_desc_{_pe}"] = pre.get("desc", "")
        st.session_state[f"pub_color_{_pe}"] = pre.get("color", "")
        st.session_state[f"pub_size_{_pe}"] = pre.get("size", "medium")
        st.session_state[f"pub_collar_{_pe}"] = bool(pre.get("collar", False))
        st.session_state[f"reg_lat_{_pe}"] = float(pre.get("lat", 36.6826))
        st.session_state[f"reg_lon_{_pe}"] = float(pre.get("lng", -6.1376))
        st.session_state[f"addr_in_{_pe}"] = pre.get("addr", "Centro, Jerez")
        st.session_state.pub_init = True
        st.info("Datos traídos de tu búsqueda: revísalos y confirma.")
    if pre:
        if st.button("Empezar de cero", key="pub_limpiar"):
            st.session_state.pop("pub_prefill", None)
            st.session_state.pop("pub_init", None)
            st.session_state.pub_epoch = _pe + 1
            st.rerun()
    if f"pub_collar_{_pe}" not in st.session_state:
        st.session_state[f"pub_collar_{_pe}"] = False
    with st.container(border=True):
        r1, r2 = st.columns([1, 1])
        with r1:
            tipo = st.selectbox("Tipo de aviso *", ["lost", "found"], key=f"pub_tipo_{_pe}",
                                index=None, placeholder="SELECCIONAR",
                                format_func=lambda t: ("Mascota perdida" if t == "lost"
                                                       else "Animal encontrado" if t == "found"
                                                       else "SELECCIONAR"))
            animal = st.selectbox("Animal *", ["dog", "cat", "other"], key=f"pub_animal_{_pe}",
                                  index=None, placeholder="SELECCIONAR",
                                  format_func=lambda a: {"dog": "Perro", "cat": "Gato",
                                                         "other": "Otro"}.get(a, "SELECCIONAR"))
            st.markdown(FOTO_PUB_STYLE, unsafe_allow_html=True)
            foto = st.file_uploader("Foto del animal", type=["jpg", "jpeg", "png"],
                                    key=f"pub_foto_{_pe}")
            if foto:
                vista_previa_scan(foto)
            elif pre.get("qpath") and Path(pre["qpath"]).exists():
                st.image(imagen_cuadrada(pre["qpath"]), caption="Foto de tu búsqueda",
                         width=360)
            comp = st.text_input("Comportamiento", "", key=f"c_comp_{_pe}",
                                 placeholder="Ej. sociable, se deja coger")
            est = st.text_input("Estado del animal", "", key=f"c_est_{_pe}",
                                placeholder="Ej. sano, bien alimentado")
            paso = st.text_area("Cómo lo perdiste / qué hiciste tras avistar", "", key=f"c_paso_{_pe}",
                                placeholder="Ej. se escapó en el parque y no volvió")
        with r2:
            desc = st.text_area("Descripción libre *", "", key=f"pub_desc_{_pe}",
                                placeholder="Describe al animal: color, marcas, collar…")
            c1 = st.text_input("Color principal *", "", key=f"pub_color_{_pe}",
                               placeholder="Ej. marrón")
            size = st.selectbox("Tamaño *", ["small", "medium", "large"], key=f"pub_size_{_pe}",
                                index=None, placeholder="SELECCIONAR",
                                format_func=lambda s: {"small": "Pequeño", "medium": "Mediano",
                                                       "large": "Grande"}.get(s, "SELECCIONAR"))
            collar = st.checkbox("¿Lleva collar?", key=f"pub_collar_{_pe}")
            st.markdown("**Contacto ***")
            st.caption("Obligatorio al menos uno: móvil, correo o red social.")
            c_movil = st.text_input("Móvil", "", key=f"c_movil_{_pe}")
            c_mail = st.text_input("Correo", "", key=f"c_mail_{_pe}")
            c_rrss = st.text_input("Red social", "", key=f"c_rrss_{_pe}")
            if foto or (pre.get("qpath") and Path(pre["qpath"]).exists()):
                # La foto alarga la columna izquierda: el boli rellena el hueco
                # que queda abajo a la derecha. Solo aparece con foto, no antes.
                st.markdown(build_pen_html(), unsafe_allow_html=True)
    st.subheader("Ubicación exacta")
    with st.container(border=True):
        if f"reg_lat_{_pe}" not in st.session_state:
            st.session_state[f"reg_lat_{_pe}"] = 36.6826
            st.session_state[f"reg_lon_{_pe}"] = -6.1376
        addr_in = st.text_input("Calle, número y zona", value="Centro, Jerez", key=f"addr_in_{_pe}")
        if st.button("Buscar dirección en el mapa"):
            res = geocode_nominatim(addr_in)
            if res:
                st.session_state[f"reg_lat_{_pe}"] = round(res[0], 4)
                st.session_state[f"reg_lon_{_pe}"] = round(res[1], 4)
                st.success(f"Localizada: {res[2][:90]}")
            else:
                st.warning("Dirección no encontrada. Marca el punto en el mapa o ajusta manual.")
        st.caption("O marca el punto exacto clicando 2 veces en el mapa:")
        try:
            import folium
            from streamlit_folium import st_folium

            fmap = folium.Map(location=[st.session_state[f"reg_lat_{_pe}"],
                                        st.session_state[f"reg_lon_{_pe}"]], zoom_start=14)
            folium.Marker([st.session_state[f"reg_lat_{_pe}"], st.session_state[f"reg_lon_{_pe}"]],
                          tooltip="TU PUNTO",
                          popup=("TU PUNTO · "
                                 f"{st.session_state.get(f'addr_in_{_pe}', '')}"),
                          icon=folium.Icon(color="red")).add_to(fmap)
            from folium.plugins import MarkerCluster as _MC
            _reg_perd = dbmod.get_active_opuestos(con, "found")
            _reg_av = dbmod.get_active_opuestos(con, "lost")
            _cl_perd = _MC(name="Perdidos").add_to(fmap)
            for _c in _reg_perd:
                folium.Marker(
                    [_c["location"]["lat"], _c["location"]["lng"]],
                    tooltip=_c["id"],
                    popup=folium.Popup(popup_html(_c), max_width=260),
                    icon=folium.Icon(color=pin_color(_c))).add_to(_cl_perd)
            _cl_av = _MC(name="Avistamientos").add_to(fmap)
            for _c in _reg_av:
                folium.Marker(
                    [_c["location"]["lat"], _c["location"]["lng"]],
                    tooltip=_c["id"],
                    popup=folium.Popup(popup_html(_c), max_width=260),
                    icon=folium.Icon(color=pin_color(_c))).add_to(_cl_av)
            out = st_folium(fmap, key=f"reg_map_{huella_mapa(con)}",
                            center=(st.session_state[f"reg_lat_{_pe}"],
                                    st.session_state[f"reg_lon_{_pe}"]),
                            zoom=14, height=380, use_container_width=True)
            leyenda_mapa(n_perd=len(_reg_perd), n_av=len(_reg_av))
            if out and out.get("last_clicked"):
                st.session_state[f"reg_lat_{_pe}"] = round(out["last_clicked"]["lat"], 4)
                st.session_state[f"reg_lon_{_pe}"] = round(out["last_clicked"]["lng"], 4)
        except Exception as e:
            st.caption(f"Mapa no disponible ({e}). Usa el ajuste manual.")
        st.write(f"- Punto seleccionado: {st.session_state[f'reg_lat_{_pe}']}, "
                 f"{st.session_state[f'reg_lon_{_pe}']}")
        with st.expander("Ajuste manual de coordenadas"):
            st.number_input("Latitud", format="%.4f", key=f"reg_lat_{_pe}")
            st.number_input("Longitud", format="%.4f", key=f"reg_lon_{_pe}")
    _shake_n = st.session_state.get("pub_shake_n", 0)
    if st.session_state.pop("pub_shake_pending", False):
        # El botón remonta con clave nueva: la sacudida suena una sola vez.
        st.markdown(SHAKE_CONFIRM_STYLE, unsafe_allow_html=True)
    if st.session_state.get("pub_faltan"):
        st.warning("Te falta: " + ", ".join(st.session_state.pop("pub_faltan")) + ".")
    if not faltantes_publicar(tipo, animal, size, c1, desc, c_movil, c_mail, c_rrss):
        # Formulario completo: pulso suave invitando a publicar.
        st.markdown(PULSE_CONFIRM_STYLE, unsafe_allow_html=True)
    if st.button("Confirmar y publicar", type="primary", key=f"confirm_pub_{_shake_n}"):
        _faltan = faltantes_publicar(tipo, animal, size, c1, desc,
                                     c_movil, c_mail, c_rrss)
        if _faltan:
            st.session_state.pub_shake_n = _shake_n + 1
            st.session_state.pub_shake_pending = True
            st.session_state.pub_faltan = _faltan
            st.rerun()
        try:
            lat = float(st.session_state.get(f"reg_lat_{_pe}", 36.6826))
            lng = float(st.session_state.get(f"reg_lon_{_pe}", -6.1376))
            addr = st.session_state.get(f"addr_in_{_pe}", "Centro, Jerez")
            Path("data/uploads").mkdir(parents=True, exist_ok=True)
            pre_q = (st.session_state.get("pub_prefill") or {}).get("qpath", "")
            if foto:
                img_path = f"data/uploads/{foto.name}"
                Path(img_path).write_bytes(foto.getbuffer())
            elif pre_q and Path(pre_q).exists():
                from datetime import datetime as _dtp
                import shutil as _sh

                img_path = f"data/uploads/pub_{_dtp.now().strftime('%Y%m%d%H%M%S')}.jpg"
                _sh.copy(pre_q, img_path)
            else:
                img_path = "data/seed/images/perrete 3.jpg"
            desc_full = desc.strip()
            if comp.strip():
                desc_full += f" Comportamiento: {comp.strip()}."
            if est.strip():
                desc_full += f" Estado: {est.strip()}."
            if paso.strip():
                desc_full += f" Lo ocurrido: {paso.strip()}."
            av = normalize_aviso({"type": tipo, "animal": animal, "color_primary": c1, "size": size,
                                  "has_collar": collar, "markings": [], "description_text": desc_full,
                                  "location": {"lat": lat, "lng": lng, "address_text": addr},
                                  "date_reported": "2026-09-23T12:00:00+02:00", "image_url": img_path,
                                  "contact_info": " · ".join(x.strip() for x in
                                                             [c_movil, c_mail, c_rrss] if x.strip()),
                                  "status": "active"})
            av["image_embedding"] = get_image_embedding(img_path)
            dbmod.upsert_aviso(con, av)
            st.session_state.pop("pub_prefill", None)
            st.session_state.pop("pub_init", None)
            celebrate_search()
            st.success(f"Aviso `{av['id']}` publicado.")
            cruce_box = None
            try:
                from agents.vision import embed_candidato as _ec, embedida_con_espacio as _ee
                import time as _time

                _, espacio_pub = _ee(img_path)
                cands_auto = dbmod.get_active_opuestos(con, tipo)
                cruce_box = st.empty()
                with cruce_box.container():
                    st.markdown(build_crossing_html(len(cands_auto)),
                                unsafe_allow_html=True)
                    _barra = st.progress(0)
                _t0 = _time.time()
                _barra.progress(30)
                ms_auto = retrieve(av, cands_auto,
                                   lambda a, _e=espacio_pub: _ec(a, _e),
                                   semantic_similarity)
                _barra.progress(70)
                auto = notificar(con, av["id"], ms_auto)
                _barra.progress(90)
                _dt = _time.time() - _t0
                if _dt < 1.5:
                    _time.sleep(1.5 - _dt)
                _barra.progress(100)
                cruce_box.empty()
                cruce_box = None
                if auto:
                    top = auto[0]
                    _tc = dbmod.get_aviso(con, top["candidato_id"])
                    st.session_state.pub_result = {
                        "aviso_id": av["id"], "n": len(auto),
                        "top_id": top["candidato_id"], "top_score": top["score"],
                        "top_tipo": (_tc or {}).get("type", "found")}
                else:
                    st.session_state.pub_result = {"aviso_id": av["id"], "n": 0}
            except Exception as e:
                try:
                    if cruce_box is not None:
                        cruce_box.empty()
                except Exception:
                    pass
                st.session_state.pub_result = {"aviso_id": av["id"],
                                               "cruce_error": str(e)}
            # Recarga: sidebar/inicio recalculan métricas con el aviso ya
            # guardado; el banner de arriba repite el resultado del cruce.
            # También rota la época: el formulario vuelve limpio (sin doble envío).
            st.session_state.pub_epoch = _pe + 1
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# ── Página: Volvió a casa ─────────────────────────────────────────────
if page == "reencuentro":
    titulo_perimetro("Volvió a casa")
    st.caption("Notifica que un animal volvió con su dueño. El administrador "
               "revisa el caso y decide si se cierran los avisos.")
    perd_opts = [dbmod.get_aviso(con, r["id"]) for r in
                 con.execute("SELECT id FROM avisos WHERE status='active' AND type='lost'").fetchall()]
    perd_opts = [a for a in perd_opts if a]
    found_opts = dbmod.get_active_opuestos(con, "lost")
    _re_e = st.session_state.get("re_epoch", 0)
    with st.container(border=True):
        sel_lost = st.multiselect("Perdidos que se resuelven",
                                  [a["id"] for a in perd_opts],
                                  format_func=lambda i: next(
                                      (f"[{x['id']}] {animal_tag(x)}" for x in perd_opts
                                       if x["id"] == i), i),
                                  key=f"re_lost_{_re_e}", placeholder="Elige una opción")
        sel_found = st.multiselect("Avistamientos que se resuelven",
                                   [a["id"] for a in found_opts],
                                   format_func=lambda i: next(
                                       (f"[{x['id']}] {animal_tag(x)}" for x in found_opts
                                        if x["id"] == i), i),
                                   key=f"re_found_{_re_e}", placeholder="Elige una opción")
        _prev_sel(sel_lost, perd_opts)
        _prev_sel(sel_found, found_opts)
        nota = st.text_area("Cómo fue el reencuentro", "", key=f"re_nota_{_re_e}",
                            placeholder="Ej. apareció en el portal de casa")
        fotos_r = st.file_uploader("Fotos del reencuentro", type=["jpg", "jpeg", "png"],
                                   accept_multiple_files=True,
                                   key=f"re_fotos_{_re_e}")
        if fotos_r:
            _fp_cols = st.columns(min(3, len(fotos_r)))
            for _fc, _f in zip(_fp_cols, fotos_r[:3]):
                with _fc:
                    st.image(_f, caption=getattr(_f, "name", "foto"), width=150)
    if st.button("Empezar de cero", key="re_limpiar"):
        for _k in ("re_shake_n", "re_shake_pending", "re_faltan"):
            st.session_state.pop(_k, None)
        # Los widgets se borran rotando la época (el navegador restaura valores
        # aunque se vacíe su clave: solo una clave nueva garantiza limpieza).
        st.session_state.re_epoch = _re_e + 1
        st.rerun()
    _re_n = st.session_state.get("re_shake_n", 0)
    if st.session_state.pop("re_shake_pending", False):
        st.markdown(SHAKE_RE_STYLE, unsafe_allow_html=True)
    if st.session_state.get("re_faltan"):
        st.warning("Te falta: " + ", ".join(st.session_state.pop("re_faltan")) + ".")
    if st.button("Notificar reencuentro", type="primary", key=f"re_notif_{_re_n}"):
        elegidos = list(dict.fromkeys(list(sel_lost) + list(sel_found)))
        if not elegidos:
            st.session_state.re_shake_n = _re_n + 1
            st.session_state.re_shake_pending = True
            st.session_state.re_faltan = ["elegir al menos un aviso"]
            st.rerun()
        else:
            rev_box = None
            try:
                from datetime import datetime as _dtr
                import time as _tr

                rev_box = st.empty()
                with rev_box.container():
                    st.markdown(build_revision_html(), unsafe_allow_html=True)
                _t0 = _tr.time()
                Path("data/uploads").mkdir(parents=True, exist_ok=True)
                sello = _dtr.now().strftime("%Y%m%d%H%M%S")
                guardadas = []
                for i, f in enumerate(fotos_r or []):
                    dest = f"data/uploads/reencuentro_{sello}_{i}.jpg"
                    Path(dest).write_bytes(f.getbuffer())
                    guardadas.append(dest)
                rid = dbmod.save_reencuentro(con, elegidos, guardadas, nota)
                admmod.log_action(f"REENCUENTRO {rid} pendiente: {', '.join(elegidos)}")
                st.session_state.re_epoch = _re_e + 1
                _dt = _tr.time() - _t0
                if _dt < 1.5:
                    _tr.sleep(1.5 - _dt)
                rev_box.empty()
                rev_box = None
                st.markdown(build_fiesta_html(), unsafe_allow_html=True)
                celebrate_search()
                st.success(f"Reencuentro `{rid}` notificado al administrador. "
                           "Él revisará las pruebas y cerrará (o no) los avisos.")
            except Exception as e:
                try:
                    if rev_box is not None:
                        rev_box.empty()
                except Exception:
                    pass
                st.error(f"Error: {e}")

    st.subheader("Casos cerrados")
    cerrados = dbmod.list_reencuentros(con, "validada")
    pendientes = dbmod.list_reencuentros(con, "pendiente")
    if pendientes:
        st.caption(f"{len(pendientes)} caso(s) en revisión por el administrador.")
    if not cerrados and not pendientes:
        st.markdown(
            '<div class="huellas-vacio-heart">'
            '<svg class="huellas-heart" viewBox="0 0 24 24" width="44" height="44" '
            'aria-hidden="true"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 '
            '2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 '
            '16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" '
            'fill="#E30613"/></svg></div>',
            unsafe_allow_html=True)
        st.info("Aún no hay reencuentros. Sé el primero en cerrar un caso.")
    for base in range(0, len(cerrados), 3):
        fila = cerrados[base:base + 3]
        cols = st.columns(len(fila))
        for j, (col, r) in enumerate(zip(cols, fila)):
            with col:
                _av0, _uri, _uri_av = _datos_caso(con, r)
                _tit = titulo_corto(_av0) if _av0 else "Aviso"
                if _av0:
                    _eff = _av0.get("date_last_seen") or _av0.get("date_reported")
                    _dias = texto_dias_casa(dias_entre(_eff, r.get("created_at")))
                else:
                    _dias = "Reencuentro cerrado"
                st.markdown(build_cerrado_card_html(
                    _uri, _tit, _dias, base + j, marca="Caso cerrado",
                    pie=f"Resuelve {', '.join(r['aviso_ids'])}",
                    nota=r["nota"], estado="cerrada", foto2_uri=_uri_av),
                    unsafe_allow_html=True)
    for r in pendientes:
        _av0, _uri, _uri_av = _datos_caso(con, r)
        _tit = titulo_corto(_av0) if _av0 else "Aviso"
        st.markdown(build_cerrado_card_html(
            _uri, _tit, "En revisión por el administrador", 0,
            marca="En revisión", marca_clase="ambar",
            pie=f"Resuelve {', '.join(r['aviso_ids'])}",
            nota=r["nota"], estado="revision", foto2_uri=_uri_av),
            unsafe_allow_html=True)
        if len(r["fotos"]) > 1:
            fcols = st.columns(min(3, len(r["fotos"]) - 1))
            for fc, fp in zip(fcols, r["fotos"][1:4]):
                with fc:
                    show_image(fp, caption="Reencuentro", width=220)

