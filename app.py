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

DB = "data/huellas.db"
LOGO = next((p for p in ("assets/logo.png", "assets/logo.jpg", "assets/logo.jpeg", "assets/logo.webp")
             if Path(p).exists()), None)
FONDO = next((p for p in ("assets/fondo.png", "assets/fondo.jpg", "assets/fondo.jpeg")
              if Path(p).exists()), None)
ANIMAL_ES = {"dog": "Perro", "cat": "Gato", "other": "Otro"}
SIZE_ES = {"small": "Pequeño", "medium": "Mediano", "large": "Grande"}
TAGLINE = "Agente de Búsqueda y Comparativa Visual de Animales Perdidos"
SUBTITLE = "Encuentra a tu mascota entre los avisos de avistamientos en Jerez de la Frontera"

st.set_page_config(page_title="HUELLAS", page_icon=LOGO if LOGO else None, layout="wide")


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


def show_image(path: str, caption: str = "", width: int = 380):
    """Muestra imagen si existe; si no, placeholder textual (rutas locales ausentes en Cloud)."""
    if path and Path(path).exists():
        st.image(path, caption=caption, width=width)
    else:
        st.info("[ IMAGEN NO DISPONIBLE EN ESTE DESPLIEGUE ]" + (f" {caption}" if caption else ""))


def stat_box(value, label: str, mini: bool = False):
    """Caja de destacado: cuadrada, negra, alto contraste (sustituye a st.metric)."""
    cls = "huellas-stat huellas-stat-mini" if mini else "huellas-stat"
    st.markdown(f'<div class="{cls}"><div class="huellas-stat-value">{value}</div>'
                f'<div class="huellas-stat-label">{label}</div></div>', unsafe_allow_html=True)


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
    """Verde = encontrados · azul = perdidos activos (el query va en rojo).

    Las destacadas ≥80% se anuncian en el popup, sin cambiar el color.
    """
    return "green" if a.get("type") == "found" else "blue"


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


def leyenda_mapa():
    """Leyenda al lado del mapa: rojo = tu mascota, azul = perdidos, verde = encontrados."""
    st.markdown(
        '<div style="background:#23201B;border-radius:10px;padding:.6rem .5rem;font-size:.72rem;'
        'font-weight:700;color:#FFFFFF;line-height:2.1;">'
        '<div><span style="display:inline-block;width:12px;height:12px;border-radius:50%;'
        'background:#E30613;margin-right:.4rem;"></span>TU MASCOTA</div>'
        '<div><span style="display:inline-block;width:12px;height:12px;border-radius:50%;'
        'background:#3388FF;margin-right:.4rem;"></span>PERDIDOS</div>'
        '<div><span style="display:inline-block;width:12px;height:12px;border-radius:50%;'
        'background:#35AC46;margin-right:.4rem;"></span>ENCONTRADOS</div>'
        '<div style="font-weight:400;font-size:.68rem;line-height:1.5;margin-top:.3rem;">'
        'PULSA CADA CHINCHETA PARA VER DIRECCIÓN Y DISTANCIA.</div></div>',
        unsafe_allow_html=True)


def render_mapa_avistados(q: dict, items: list, key: str, otros_lost: list | None = None,
                          zoom: int = 13):
    """Mapa Leaflet con chinchetas + leyenda al lado.

    Roja = tu mascota · azules = perdidos activos · verdes = encontrados.
    Los avisos con la misma ubicación se agrupan (círculo con el nº);
    pulsa para desplegarlos. Cada chincheta lleva foto + datos en el popup
    y marca DESTACADA si ≥80%. Si folium no está, aviso sin romper.
    """
    try:
        import folium
        from folium.plugins import MarkerCluster
        from streamlit_folium import st_folium

        c_map, c_leg = st.columns([5, 1])
        with c_map:
            fmap = folium.Map(location=[q["location"]["lat"], q["location"]["lng"]], zoom_start=zoom)
            folium.Marker(
                [q["location"]["lat"], q["location"]["lng"]],
                tooltip=f"PERDIDO {q['id']}",
                popup=folium.Popup(popup_html(q, marca=" · TU MASCOTA"), max_width=260),
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
            cl_found = MarkerCluster(name="Encontrados").add_to(fmap)
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
            st_folium(fmap, key=key, width=900, height=450)
        with c_leg:
            leyenda_mapa()
    except Exception as e:
        st.caption(f"Mapa no disponible ({e}).")


def geocode_nominatim(q: str):
    """Calle/número → (lat, lng, nombre) vía Nominatim OSM con sesgo a Jerez.

    Sin dependencias ni claves. Devuelve None si no hay red o no se encuentra.
    """
    import json as _json
    import urllib.parse
    import urllib.request

    url = ("https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "json", "limit": 1,
         "viewbox": "-6.25,36.75,-6.00,36.60", "bounded": 0}))
    req = urllib.request.Request(url, headers={"User-Agent": "HUELLAS-EOI-MVP/1.0"})
    with urllib.request.urlopen(req, timeout=8) as r:
        data = _json.loads(r.read().decode("utf-8"))
    if not data:
        return None
    return float(data[0]["lat"]), float(data[0]["lon"]), data[0].get("display_name", q)


def reverse_geocode_nominatim(lat: float, lng: float):
    """Coords → dirección legible vía Nominatim OSM (para autocompletar al clicar).

    Sin dependencias ni claves. Devuelve None si no hay red o no se encuentra.
    """
    import urllib.parse
    import urllib.request
    import json as _json

    url = ("https://nominatim.openstreetmap.org/reverse?" + urllib.parse.urlencode(
        {"lat": lat, "lon": lng, "format": "json"}))
    req = urllib.request.Request(url, headers={"User-Agent": "HUELLAS-EOI-MVP/1.0"})
    with urllib.request.urlopen(req, timeout=8) as r:
        data = _json.loads(r.read().decode("utf-8"))
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


def perro_html(modo: str) -> str:
    """Perro SVG con animación según el tiempo. Solo CSS, sin dependencias."""
    extra = ""
    if modo == "lluvia":
        extra = ('<g fill="#3388FF">'
                 '<rect x="30" y="4" width="5" height="16" rx="2" class="lluvia l1"/>'
                 '<rect x="80" y="4" width="5" height="16" rx="2" class="lluvia l2"/>'
                 '<rect x="130" y="4" width="5" height="16" rx="2" class="lluvia l3"/></g>'
                 '<ellipse cx="85" cy="26" rx="46" ry="16" fill="#9AA3AD"/>')
    elif modo == "contento":
        extra = ('<circle cx="150" cy="28" r="16" fill="#F5B301"/>'
                 '<g stroke="#F5B301" stroke-width="4" stroke-linecap="round">'
                 '<line x1="150" y1="4" x2="150" y2="10"/><line x1="150" y1="46" x2="150" y2="52"/>'
                 '<line x1="126" y1="28" x2="132" y2="28"/><line x1="168" y1="28" x2="174" y2="28"/></g>')
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
    </style><div class="perro-wrap"><svg class="perro-svg {modo}" viewBox="0 0 180 130" width="200" height="145">
    {extra}
    <ellipse cx="85" cy="118" rx="62" ry="7" fill="#000" opacity="0.12"/>
    <ellipse cx="85" cy="92" rx="42" ry="24" fill="#C68A4B"/>
    <circle cx="92" cy="58" r="26" fill="#D89A55"/>
    <ellipse cx="62" cy="40" rx="10" ry="20" fill="#8A5A2B" transform="{orejas}"/>
    <ellipse cx="118" cy="42" rx="10" ry="20" fill="#8A5A2B"/>
    <circle cx="83" cy="54" r="4" fill="#111"/><circle cx="103" cy="54" r="4" fill="#111"/>
    <ellipse cx="93" cy="68" rx="6" ry="5" fill="#111"/>{lengua}{lagrima}
    <path d="M44 84 Q22 78 28 60" stroke="#8A5A2B" stroke-width="9" fill="none" stroke-linecap="round" class="perro-cola"/>
    <rect x="58" y="102" width="12" height="16" rx="5" fill="#8A5A2B"/><rect x="102" y="102" width="12" height="16" rx="5" fill="#8A5A2B"/>
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
n_lost_total = con.execute("SELECT COUNT(*) FROM avisos WHERE type='lost'").fetchone()[0]
n_lost_res = con.execute(
    "SELECT COUNT(*) FROM avisos WHERE type='lost' AND status!='active'").fetchone()[0]
n_found = con.execute("SELECT COUNT(*) FROM avisos WHERE status='active' AND type='found'").fetchone()[0]
n_notif = con.execute("SELECT COUNT(*) FROM notifications").fetchone()[0]
n_total = con.execute("SELECT COUNT(*) FROM avisos").fetchone()[0]

if "page" not in st.session_state:
    st.session_state.page = "buscar"


def nav_to(dest: str):
    st.session_state.page = dest


# ── Navegación superior: botones negros (cuenta + acceso directo) ──────
m1, m2, m3 = st.columns(3)
with m1:
    st.button(f"PERDIDOS ACTIVOS ({n_lost})", key="nav_perdidos",
              use_container_width=True, on_click=nav_to, args=("perdidos",),
              help="Muestra los avisos de mascotas perdidas activos, con filtros por animal, color y tamaño.")
with m2:
    st.button(f"AVISTAMIENTOS ({n_found})", key="nav_encontrados",
              use_container_width=True, on_click=nav_to, args=("encontrados",),
              help="Muestra los avistamientos: animales encontrados pendientes de reunir con su dueño.")
with m3:
    st.button(f"ALERTAS ({n_notif})", key="nav_alertas",
              use_container_width=True, on_click=nav_to, args=("alertas",),
              help="Posibles coincidencias destacadas con un 80 % o más. Se generan solas al cruzar avisos.")
# ── Justo debajo: PUBLICAR + BUSCAR, centrados y rojos ─────────────────
_, b1, b2, _ = st.columns([1, 2, 2, 1])
with b1:
    st.button("Publicar aviso", key="top_publicar", type="primary",
              use_container_width=True, on_click=nav_to, args=("publicar",),
              help="Publica un aviso de perdido o avistamiento. Al publicar se cruza solo y avisa si supera el 80 por ciento.")
with b2:
    st.button("Buscar a mi mascota", key="top_buscar", type="primary",
              use_container_width=True, on_click=nav_to, args=("buscar",),
              help="Permite realizar una búsqueda de coincidencias entre tu mascota perdida y los avistamientos antes de publicar un aviso.")

# ── Barra lateral ─────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("Funcionamiento web")
    with st.expander("Cómo puntúa (fórmula cerrada)"):
        st.markdown("**0.40·VISUAL + 0.30·TEXTO + 0.20·TEMPORAL + 0.10·GEO**")
        u1, u2 = st.columns(2)
        with u1:
            st.markdown('<div style="background:#000000;border-radius:8px;padding:.55rem .3rem;'
                        'text-align:center;color:#FFFFFF;font-weight:800;margin-bottom:.5rem;">'
                        '≥80%<br>ALERTA</div>', unsafe_allow_html=True)
        with u2:
            st.markdown('<div style="background:#000000;border-radius:8px;padding:.55rem .3rem;'
                        'text-align:center;color:#FFFFFF;font-weight:800;margin-bottom:.5rem;">'
                        '≥65%<br>EN LISTA</div>', unsafe_allow_html=True)
        u3, u4 = st.columns(2)
        with u3:
            st.markdown('<div style="background:#000000;border-radius:8px;padding:.55rem .3rem;'
                        'text-align:center;color:#FFFFFF;font-weight:800;">'
                        'RADIO<br>15 KM</div>', unsafe_allow_html=True)
        with u4:
            st.markdown('<div style="background:#000000;border-radius:8px;padding:.55rem .3rem;'
                        'text-align:center;color:#FFFFFF;font-weight:800;">'
                        'VENTANA<br>30 DÍAS</div>', unsafe_allow_html=True)
    with st.expander("Aviso legal"):
        st.write("Este análisis no promete una coincidencia inequívoca respecto al animal buscado. "
                 "Una imagen no permite confirmar la identidad, verifique en persona.")
    st.divider()
    st.subheader("Datos demo")
    if st.button("Cargar seed Jerez (16 avisos activos)"):
        import json as _json

        con2 = get_con()
        dbmod.wipe_all(con2)
        total = 0
        for folder in ("lost", "found"):
            for fp in sorted(Path("data/seed", folder).glob("*.json")):
                dbmod.upsert_aviso(con2, normalize_aviso(_json.loads(fp.read_text(encoding="utf-8"))))
                total += 1
        dbmod.set_seed_version(con2)
        from agents.vision import backfill_embeddings as _bf, sync_seed_embeddings as _sy

        _bf(con2)
        _sy(con2)
        retirar_alerta_demo(con2)
        st.success(f"Seed cargada: 16 avisos activos "
                   f"(5 perdidos + 11 encontrados, +1 resuelto demo).")
        st.rerun()
    if st.button("Expirar avisos >30 días"):
        n = dbmod.expire_old(get_con(), 30)
        st.info(f"Avisos expirados: {n}")
    st.divider()
    st.subheader("Administración")
    TIPO_ES = {"todos": "Todos", "lost": "Perdidos", "found": "Encontrados"}
    ESTADO_ES = {"active": "Activo", "resolved": "Resuelto", "expired": "Expirado"}

    def _expected_pw() -> str:
        try:
            v = st.secrets.get("ADMIN_PASSWORD", "")
            if v:
                return str(v)
        except Exception:
            pass
        import os
        return os.environ.get("HUELLAS_ADMIN_PASSWORD", admmod.DEFAULT_ADMIN_PASSWORD)

    if not st.session_state.get("admin_ok"):
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
        for a in admmod.list_avisos(con, tipo=f_tipo, texto=f_txt):
            with st.container(border=True):
                show_image(a["image_url"], caption=a["id"])
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
                                "description_text": e_desc.strip(), "status": e_status})
                            nuevo["location"] = dict(a.get("location") or {},
                                                     address_text=e_addr.strip() or None)
                            errs = validate_aviso(nuevo)
                            if errs:
                                st.error("Revisa: " + "; ".join(errs))
                            else:
                                campos = ("type", "animal", "breed_guess", "color_primary",
                                          "color_secondary", "markings", "size", "has_collar",
                                          "collar_description", "description_text", "status")
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

page = st.session_state.get("page", "buscar")

# ── Página: Buscar ────────────────────────────────────────────────────
if page == "buscar":
    st.subheader("1. Foto actual")
    foto_b = st.file_uploader("Sube una foto de tu mascota (pesa el 40%)",
                              type=["jpg", "jpeg", "png"], key="b_foto")
    if foto_b:
        st.image(foto_b, caption="Vista previa de tu foto", width=360)
    else:
        st.caption("Sin foto no hay búsqueda: súbela para empezar.")

    st.subheader("2. Zona")
    with st.container(border=True):
        if "q_lat" not in st.session_state:
            st.session_state.q_lat, st.session_state.q_lon = 36.6826, -6.1376
        q_addr = st.text_input("Calle, número y zona", value="Centro, Jerez", key="q_addr_in")
        if st.button("Buscar dirección en el mapa", key="q_geocode"):
            res = geocode_nominatim(q_addr)
            if res:
                st.session_state.q_lat, st.session_state.q_lon = round(res[0], 4), round(res[1], 4)
                st.success(f"Localizada: {res[2][:90]}")
            else:
                st.warning("Dirección no encontrada. Marca el punto en el mapa o ajusta manual.")
        st.caption("O marca el punto clicando en el mapa (la dirección se autocompleta). "
                   "Verdes: avistamientos · azules: perdidos · roja: tu zona.")
        try:
            import folium
            from folium.plugins import MarkerCluster
            from streamlit_folium import st_folium

            c_map, c_leg = st.columns([5, 1])
            with c_map:
                fmap = folium.Map(location=[st.session_state.q_lat, st.session_state.q_lon],
                                  zoom_start=14)
                folium.Marker([st.session_state.q_lat, st.session_state.q_lon],
                              tooltip="TU ZONA",
                              popup=("TU ZONA · "
                                     f"{st.session_state.get('q_addr_in', '')}"),
                              icon=folium.Icon(color="red")).add_to(fmap)
                cl_lost = MarkerCluster(name="Perdidos").add_to(fmap)
                for o in (dbmod.get_aviso(con, r["id"]) for r in
                          con.execute("SELECT id FROM avisos WHERE status='active'"
                                      " AND type='lost'").fetchall()):
                    if not o:
                        continue
                    folium.Marker(
                        [o["location"]["lat"], o["location"]["lng"]],
                        tooltip=f"PERDIDO {o['id']}",
                        popup=folium.Popup(popup_html(o), max_width=260),
                        icon=folium.Icon(color="blue")).add_to(cl_lost)
                cl_found = MarkerCluster(name="Avistamientos").add_to(fmap)
                for c in dbmod.get_active_opuestos(con, "lost"):
                    folium.Marker(
                        [c["location"]["lat"], c["location"]["lng"]],
                        tooltip=c["id"],
                        popup=folium.Popup(popup_html(c), max_width=260),
                        icon=folium.Icon(color="green")).add_to(cl_found)
                out = st_folium(fmap, key="cerca_map",
                                center=(st.session_state.q_lat, st.session_state.q_lon),
                                zoom=14, width=900, height=380)
            with c_leg:
                leyenda_mapa()
            if out and out.get("last_clicked"):
                nlat = round(out["last_clicked"]["lat"], 4)
                nlng = round(out["last_clicked"]["lng"], 4)
                if (nlat, nlng) != (st.session_state.q_lat, st.session_state.q_lon):
                    st.session_state.q_lat, st.session_state.q_lon = nlat, nlng
                    rev = reverse_geocode_nominatim(nlat, nlng)
                    if rev:
                        st.session_state.q_addr_in = rev[:120]
                    st.rerun()
        except Exception as e:
            st.caption(f"Mapa no disponible ({e}). Usa el ajuste manual.")
        st.write(f"- Punto seleccionado: {st.session_state.q_lat}, {st.session_state.q_lon}")
        with st.expander("Ajuste manual de coordenadas"):
            st.number_input("Latitud", format="%.4f", key="q_lat")
            st.number_input("Longitud", format="%.4f", key="q_lon")

    st.subheader("3. Descripción")
    d1, d2 = st.columns(2)
    with d1:
        b_animal = st.selectbox("Animal", ["dog", "cat", "other"], key="b_animal",
                                format_func=lambda a: {"dog": "Perro", "cat": "Gato",
                                                       "other": "Otro"}.get(a, a))
        b_color = st.text_input("Color principal", "marrón", key="b_color")
        b_size = st.selectbox("Tamaño", ["small", "medium", "large"], key="b_size",
                              format_func=lambda s: {"small": "Pequeño", "medium": "Mediano",
                                                     "large": "Grande"}.get(s, s))
    with d2:
        b_marks = st.text_input("Marcas (separadas por comas)", "", key="b_marks")
        b_collar = st.checkbox("¿Lleva collar?", False, key="b_collar")
        b_breed = st.text_input("Raza aprox. (opcional)", "", key="b_breed")
    b_desc = st.text_area("Descripción libre", "Gato naranja atigrado con rayas marcadas.", key="b_desc")

    st.subheader("4. Lanza la búsqueda")
    f1, f2 = st.columns(2)
    with f1:
        umbral_vista = st.slider("Mostrar a partir de este porcentaje de coincidencia", 50, 100, 65,
                                 format="%d %%",
                                 help="Solo filtra lo que se muestra, no cambia el score.")
    with f2:
        topn = st.slider("Máx. resultados", 3, 15, 8)
    b_guardar = st.checkbox("Guardar esta búsqueda como aviso de perdido",
                            key="b_guardar",
                            help="Aparecerá en PERDIDOS ACTIVOS y entrará en cruces futuros.")
    if st.session_state.get("b_saved_id"):
        st.info(f"Búsqueda ya guardada como `{st.session_state.b_saved_id}`.")
    if st.button("Buscar coincidencias", type="primary"):
        if not foto_b:
            st.warning("Sube una foto para buscar: sin imagen no hay comparativa visual.")
        elif not (b_color or "").strip() or not (b_desc or "").strip():
            st.warning("Indica al menos color principal y descripción para buscar.")
        else:
            from datetime import datetime as _dt

            Path("data/uploads").mkdir(parents=True, exist_ok=True)
            qpath = "data/uploads/_busqueda.jpg"
            Path(qpath).write_bytes(foto_b.getbuffer())
            from agents.vision import embed_candidato, embedida_con_espacio

            q_emb, espacio = embedida_con_espacio(qpath)
            q = normalize_aviso({
                "type": "lost", "animal": b_animal,
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
            cands = dbmod.get_active_opuestos(con, "lost")
            matches = retrieve(q, cands,
                               lambda a, _e=espacio: embed_candidato(a, _e),
                               semantic_similarity)
            # Se guarda en sesión: si un mapa/widget provoca otro rerun,
            # los resultados NO se repliegan (antes vivían solo en el run del clic).
            st.session_state.b_search = {"q": q, "matches": matches}
            if b_guardar and not st.session_state.get("b_saved_id"):
                persist = dict(q)
                img_path = f"data/uploads/busqueda_{q['id'][:8]}.jpg"
                Path(img_path).write_bytes(foto_b.getbuffer())
                persist["image_url"] = img_path
                dbmod.upsert_aviso(con, persist)
                st.session_state.b_saved_id = q["id"]
                nuevos = notificar(con, q["id"], matches)
                celebrate_search()
                st.success(f"Búsqueda guardada como aviso `{q['id']}`."
                           + (f" {len(nuevos)} alerta(s) generada(s)." if nuevos else ""))

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
        for m in visibles:
            c = m["candidato"]
            badge = "POSIBLE COINCIDENCIA DESTACADA" if m["notifica"] else "Posible coincidencia"
            with st.container(border=True):
                st.markdown(f"**{badge}** · `{c['id']}` · **{m['score']*100:.1f}%** · {m['dist_km']} km")
                st.progress(min(max(m["score"], 0.0), 1.0))
                r1, r2 = st.columns(2)
                with r1:
                    show_image(q["image_url"], caption="Tu foto")
                with r2:
                    show_image(c["image_url"], caption=f"Avistamiento · {c['id']}")
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
            st.caption("Verdes: encontrados (DESTACADA si ≥80%) · roja: tu mascota.")
            render_mapa_avistados(q, visibles, key="res_map")

# ── Página: Perdidos activos ──────────────────────────────────────────
if page == "perdidos":
    st.subheader("Animales perdidos activos")
    st.caption(f"{n_lost} activos de {n_lost_total} perdidos totales "
               f"({n_lost_res} resuelto demo: el gatito gris que volvió a casa).")
    lost_list = [dbmod.get_aviso(con, r["id"]) for r in
                 con.execute("SELECT id FROM avisos WHERE status='active' AND type='lost'").fetchall()]
    lost_list = [a for a in lost_list if a]
    if not lost_list:
        st.info("No hay perdidos activos.")
    else:
        lista_p = aplicar_filtros(lost_list, "lost")
        stat_box(len(lista_p), "Perdidos activos")
        for a in lista_p:
            with st.container(border=True):
                c1, c2 = st.columns([1, 1])
                with c1:
                    show_image(a["image_url"], caption=f"Foto · {a['id']}")
                with c2:
                    st.markdown(f"### {animal_tag(a)}")
                    st.write(a["description_text"])
                    st.write(f"- Collar: {'sí' if a['has_collar'] else 'no'}")
                    st.write(f"- Visto: {effective_date(a).date()}")
                    st.write(f"- {a['location'].get('address_text', '')}")
                    if a.get("contact_info"):
                        st.write(f"- Contacto: {a['contact_info']}")

# ── Página: Encontrados ───────────────────────────────────────────────
if page == "encontrados":
    st.subheader("Avistamientos")
    found = dbmod.get_active_opuestos(con, "lost")
    if not found:
        st.info("Aún no hay avisos de avistamientos.")
    else:
        lista = aplicar_filtros(found, "found")
        stat_box(len(lista), "Avistamientos")
        for a in lista:
            with st.container(border=True):
                c1, c2 = st.columns([1, 1])
                with c1:
                    show_image(a["image_url"], caption=f"Foto · {a['id']}")
                with c2:
                    st.markdown(f"### {animal_tag(a)}")
                    st.write(a["description_text"])
                    st.write(f"- Collar: {'sí' if a['has_collar'] else 'no'}")
                    st.write(f"- Visto: {effective_date(a).date()}")
                    st.write(f"- {a['location'].get('address_text', '')}")
                    if a.get("contact_info"):
                        st.write(f"- Contacto: {a['contact_info']}")

# ── Página: Publicar ──────────────────────────────────────────────────
if page == "publicar":
    st.subheader("Publica un aviso de perdido o avistamiento")
    with st.container(border=True):
        r1, r2 = st.columns([1, 1])
        with r1:
            tipo = st.selectbox("Tipo de aviso", ["lost", "found"],
                                format_func=lambda t: "Mascota perdida" if t == "lost" else "Animal encontrado")
            animal = st.selectbox("Animal", ["dog", "cat", "other"],
                                  format_func=lambda a: {"dog": "Perro", "cat": "Gato",
                                                         "other": "Otro"}.get(a, a))
            foto = st.file_uploader("Foto del animal", type=["jpg", "jpeg", "png"])
            if foto:
                st.image(foto, caption="Vista previa", width=360)
            else:
                st.caption("Sube una foto: es la señal que más pesa (40%).")
        with r2:
            desc = st.text_area("Descripción libre",
                                "Perro marrón mediano con mancha blanca en el pecho, collar rojo.")
            c1 = st.text_input("Color principal", "marrón")
            size = st.selectbox("Tamaño", ["small", "medium", "large"],
                                format_func=lambda s: {"small": "Pequeño", "medium": "Mediano",
                                                       "large": "Grande"}.get(s, s))
            collar = st.checkbox("¿Lleva collar?", True)
            st.markdown("**Contacto (opcional)**")
            c_movil = st.text_input("Móvil", "", key="c_movil")
            c_mail = st.text_input("Correo", "", key="c_mail")
            c_rrss = st.text_input("Red social", "", key="c_rrss")
    st.subheader("Ubicación exacta")
    with st.container(border=True):
        if "reg_lat" not in st.session_state:
            st.session_state.reg_lat, st.session_state.reg_lon = 36.6826, -6.1376
        addr_in = st.text_input("Calle, número y zona", value="Centro, Jerez", key="addr_in")
        if st.button("Buscar dirección en el mapa"):
            res = geocode_nominatim(addr_in)
            if res:
                st.session_state.reg_lat, st.session_state.reg_lon = round(res[0], 4), round(res[1], 4)
                st.success(f"Localizada: {res[2][:90]}")
            else:
                st.warning("Dirección no encontrada. Marca el punto en el mapa o ajusta manual.")
        st.caption("O marca el punto exacto clicando en el mapa:")
        try:
            import folium
            from streamlit_folium import st_folium

            fmap = folium.Map(location=[st.session_state.reg_lat, st.session_state.reg_lon], zoom_start=14)
            folium.Marker([st.session_state.reg_lat, st.session_state.reg_lon],
                          icon=folium.Icon(color="red")).add_to(fmap)
            out = st_folium(fmap, key="reg_map",
                            center=(st.session_state.reg_lat, st.session_state.reg_lon),
                            zoom=14, width=900, height=380)
            if out and out.get("last_clicked"):
                st.session_state.reg_lat = round(out["last_clicked"]["lat"], 4)
                st.session_state.reg_lon = round(out["last_clicked"]["lng"], 4)
        except Exception as e:
            st.caption(f"Mapa no disponible ({e}). Usa el ajuste manual.")
        st.write(f"- Punto seleccionado: {st.session_state.reg_lat}, {st.session_state.reg_lon}")
        with st.expander("Ajuste manual de coordenadas"):
            st.number_input("Latitud", format="%.4f", key="reg_lat")
            st.number_input("Longitud", format="%.4f", key="reg_lon")
    if st.button("Confirmar y publicar", type="primary"):
        try:
            lat = float(st.session_state.get("reg_lat", 36.6826))
            lng = float(st.session_state.get("reg_lon", -6.1376))
            addr = st.session_state.get("addr_in", "Centro, Jerez")
            Path("data/uploads").mkdir(parents=True, exist_ok=True)
            img_path = f"data/uploads/{foto.name}" if foto else "data/seed/images/perrete 3.jpg"
            if foto:
                Path(img_path).write_bytes(foto.getbuffer())
            av = normalize_aviso({"type": tipo, "animal": animal, "color_primary": c1, "size": size,
                                  "has_collar": collar, "markings": [], "description_text": desc,
                                  "location": {"lat": lat, "lng": lng, "address_text": addr},
                                  "date_reported": "2026-09-23T12:00:00+02:00", "image_url": img_path,
                                  "contact_info": " · ".join(x.strip() for x in
                                                             [c_movil, c_mail, c_rrss] if x.strip()),
                                  "status": "active"})
            av["image_embedding"] = get_image_embedding(img_path)
            dbmod.upsert_aviso(con, av)
            celebrate_search()
            st.success(f"Aviso `{av['id']}` publicado.")
            try:
                from agents.vision import embed_candidato as _ec, embedida_con_espacio as _ee

                _, espacio_pub = _ee(img_path)
                cands_auto = dbmod.get_active_opuestos(con, tipo)
                ms_auto = retrieve(av, cands_auto,
                                   lambda a, _e=espacio_pub: _ec(a, _e),
                                   semantic_similarity)
                auto = notificar(con, av["id"], ms_auto)
                if auto:
                    top = auto[0]
                    st.success(f"Cruce automático: {len(auto)} alerta(s) ≥80%.")
                    with st.container(border=True):
                        st.markdown(f"### ¡Posible coincidencia! `{top['candidato_id']}` · "
                                    f"**{top['score']*100:.1f}%**")
                        celebrate_search()
                        st.button("Ver la alerta", key=f"ver_al_{av['id']}", type="primary",
                                  use_container_width=True,
                                  on_click=nav_to, args=("alertas",))
                else:
                    st.info("Cruce automático: sin coincidencias ≥80% por ahora. "
                            "Si aparece el par contrario, se avisará solo.")
            except Exception as e:
                st.caption(f"Cruce automático no disponible ({e}).")
        except Exception as e:
            st.error(f"Error: {e}")

# ── Página: Alertas ───────────────────────────────────────────────────
if page == "alertas":
    st.subheader("Alertas automáticas (score ≥80%)")
    rows = con.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT 50").fetchall()
    if not rows:
        st.info("Aún no hay alertas. Lanza una búsqueda: si algún candidato supera el 80%, "
                "aparecerá aquí como posible coincidencia destacada.")
    else:
        stat_box(len(rows), "Total alertas")
        for r in rows:
            qa = dbmod.get_aviso(con, r["aviso_id"])
            ca = dbmod.get_aviso(con, r["candidato_id"])
            if qa and ca:
                with st.container(border=True):
                    st.markdown(f"**POSIBLE COINCIDENCIA DESTACADA** · `{r['aviso_id']}` → "
                                f"`{r['candidato_id']}` · **{r['score']*100:.1f}%**")
                    d1, d2 = st.columns(2)
                    with d1:
                        show_image(qa["image_url"], caption=f"Perdido · {qa['id']}")
                        st.write(qa["description_text"])
                    with d2:
                        show_image(ca["image_url"], caption=f"Encontrado · {ca['id']}")
                        st.write(ca["description_text"])
                        st.write(f"- {ca['location'].get('address_text', '')}")
            else:
                st.write(dict(r))
        with st.expander("Ver tabla técnica"):
            st.table([dict(r) for r in rows])
    logp = Path("data/notifications.log")
    if logp.exists():
        with st.expander("Ver log técnico"):
            st.code(logp.read_text(encoding="utf-8")[-2000:])

# ── Pie: perreras + tiempo (abajo del todo) ─────────────────────────────
if "top_panel" not in st.session_state:
    st.session_state.top_panel = None
st.divider()
tp1, tp2 = st.columns(2)
with tp1:
    st.button("Perreras de Jerez", key="top_perreras", use_container_width=True,
              on_click=toggle_top, args=("perreras",),
              help="Direcciones y contacto de la perrera municipal y protectoras.")
with tp2:
    st.button("Tiempo en Jerez", key="top_tiempo", use_container_width=True,
              on_click=toggle_top, args=("tiempo",),
              help="Meteo actual de Jerez con el perro según el tiempo.")
if st.session_state.top_panel == "perreras":
    st.markdown("### Perreras y protectoras de Jerez")
    pc1, pc2 = st.columns(2)
    for col, p in zip((pc1, pc2), PERRERAS):
        with col:
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
elif st.session_state.top_panel == "tiempo":
    with st.container(border=True):
        st.markdown("### Tiempo en Jerez")
        try:
            import streamlit.components.v1 as _components

            d = get_tiempo()
            cur = d.get("current") or {}
            dia = (d.get("daily") or {})
            _, modo = estado_perro(d)
            w1, w2 = st.columns([1, 1])
            with w1:
                _components.html(perro_html(modo), height=190)
            with w2:
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

