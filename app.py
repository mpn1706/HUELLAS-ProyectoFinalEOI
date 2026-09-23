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
from agents.matcher import explain
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


def show_image(path: str, caption: str = ""):
    """Muestra imagen si existe; si no, placeholder textual (rutas locales ausentes en Cloud)."""
    if path and Path(path).exists():
        st.image(path, caption=caption, width="stretch")
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
    if n == 0:
        with st.spinner("Cargando corpus demo de Jerez (17 avisos)…"):
            total = 0
            for folder in ("lost", "found"):
                for fp in sorted(Path("data/seed", folder).glob("*.json")):
                    dbmod.upsert_aviso(con, normalize_aviso(json.loads(fp.read_text(encoding="utf-8"))))
                    total += 1
        st.toast(f"Seed cargada: {total} avisos.")
    from agents.vision import backfill_embeddings
    backfill_embeddings(con)
    return con


def visual_fn_factory():
    """Devuelve embed_fn(aviso) -> vector. El coseno lo calcula retrieval."""
    cache = {}

    def fn(a):
        if a.get("image_embedding"):
            return a["image_embedding"]
        if a["id"] in cache:
            return cache[a["id"]]
        try:
            v = get_image_embedding(a["image_url"])
        except Exception:
            from agents.vision import _fallback_embedding

            v = _fallback_embedding(f"img:{a['id']}")
        cache[a["id"]] = v
        return v

    return fn


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


def animal_tag(a: dict) -> str:
    return (f"{ANIMAL_ES.get(a.get('animal'), a.get('animal'))} · "
            f"{a.get('color_primary')} · {SIZE_ES.get(a.get('size'), a.get('size'))}")


def etiqueta_corta(a: dict) -> str:
    return f"[{a['id']}] {animal_tag(a)}"


# ── Cabecera (si hay logo con wordmark, no se duplica el título) ──
if LOGO:
    hc1, hc2 = st.columns([2, 5])
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

n_lost = con.execute("SELECT COUNT(*) FROM avisos WHERE status='active' AND type='lost'").fetchone()[0]
n_found = con.execute("SELECT COUNT(*) FROM avisos WHERE status='active' AND type='found'").fetchone()[0]
n_notif = con.execute("SELECT COUNT(*) FROM notifications").fetchone()[0]
m1, m2, m3 = st.columns(3)
with m1:
    stat_box(n_lost, "Perdidos activos")
with m2:
    stat_box(n_found, "Encontrados")
with m3:
    stat_box(n_notif, "Alertas ≥85%")

# ── Barra lateral ─────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("Funcionamiento web")
    with st.expander("Cómo puntúa (fórmula cerrada)"):
        st.code("0.40·visual + 0.30·geo\n+ 0.20·texto + 0.10·temporal")
        st.caption("≥85% alerta · ≥65% en lista · radio 15 km · ventana 30 días")
    with st.expander("Aviso legal"):
        st.write("Este análisis no promete una coincidencia inequívoca respecto al animal buscado. "
                 "Una imagen no permite confirmar la identidad, verifique en persona.")
    st.divider()
    st.subheader("Datos demo")
    if st.button("Cargar seed Jerez (17 avisos)"):
        import subprocess

        subprocess.run(["python", "scripts/make_seed.py"], check=False)
        subprocess.run(["python", "scripts/load_seed.py", DB], check=False)
        st.success("Seed cargada.")
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
        loga = Path("data/admin.log")
        if loga.exists():
            with st.expander("Ver registro de administración"):
                st.code(loga.read_text(encoding="utf-8")[-2000:])

all_lost = [a for a in (dbmod.get_aviso(con, r["id"]) for r in
                        con.execute("SELECT id FROM avisos WHERE status='active' AND type='lost'").fetchall()) if a]

tabP, tab1, tabF, tab3 = st.tabs(["Publicar aviso", "Buscar a mi mascota", "Encontrados",
                                  "Alertas"])

# ── TAB 1: Buscar ─────────────────────────────────────────────────────
with tab1:
    if not all_lost:
        st.info("No hay avisos de perdidos activos. Publica uno en la pestaña de publicar.")
    else:
        st.subheader("1. Elige tu aviso")
        etiquetas = {a["id"]: etiqueta_corta(a) for a in all_lost}
        qid = st.selectbox("Tu mascota perdida", [a["id"] for a in all_lost],
                           format_func=lambda i: etiquetas.get(i, i))
        q = dbmod.get_aviso(con, qid)
        with st.container(border=True):
            c_foto, c_datos = st.columns([1, 1])
            with c_foto:
                show_image(q["image_url"], caption=f"Foto registrada · {q['id']}")
            with c_datos:
                st.markdown(f"### {animal_tag(q)}")
                st.write(q["description_text"])
                st.write(f"- Collar: {'sí' if q['has_collar'] else 'no'}")
                st.write(f"- Visto: {effective_date(q).date()}")
                st.write(f"- {q['location'].get('address_text', '')}")

        st.subheader("2. Foto actual (opcional)")
        foto_q = st.file_uploader("Sube una foto reciente para afinar la búsqueda visual",
                                  type=["jpg", "jpeg", "png"], key="q_foto")
        embed_fn = visual_fn_factory()
        if foto_q:
            st.image(foto_q, caption="Vista previa de tu foto", width="stretch")
            Path("data/uploads").mkdir(parents=True, exist_ok=True)
            qpath = "data/uploads/_query_preview.jpg"
            Path(qpath).write_bytes(foto_q.getbuffer())
            q_emb = get_image_embedding(qpath)
            base_fn = embed_fn
            embed_fn = lambda a, _b=base_fn, _q=q_emb, _qid=q["id"]: _q if a["id"] == _qid else _b(a)
            st.caption("Búsqueda visual con tu foto subida.")

        st.subheader("3. Lanza la búsqueda")
        f1, f2 = st.columns(2)
        with f1:
            umbral_vista = st.slider("Mostrar desde (%)", 50, 100, 65,
                                     help="Solo filtra lo que se muestra, no cambia el score.")
        with f2:
            topn = st.slider("Máx. resultados", 3, 15, 8)
        if st.button("Buscar coincidencias", type="primary"):
            cands = dbmod.get_active_opuestos(con, "lost")
            matches = retrieve(q, cands, embed_fn, semantic_similarity)
            notificados = notificar(con, q["id"], matches)
            k1, k2 = st.columns(2)
            with k1:
                stat_box(sum(1 for m in matches if m["notifica"]), "Destacadas ≥85%", mini=True)
            with k2:
                stat_box(len(matches), "En lista ≥65%", mini=True)
            if notificados:
                st.success("Nueva alerta generada: hay coincidencias destacadas (ver pestaña de alertas).")
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
                        show_image(q["image_url"], caption=f"Perdido · {q['id']}")
                    with r2:
                        show_image(c["image_url"], caption=f"Encontrado · {c['id']}")
                        st.write(c["description_text"])
                    with st.expander("Por qué este resultado"):
                        s1, s2, s3, s4 = st.columns(4)
                        with s1:
                            stat_box(f"{m['visual']:.2f}", "Visual", mini=True)
                        with s2:
                            stat_box(f"{m['geo']:.2f}", "Geo", mini=True)
                        with s3:
                            stat_box(f"{m['texto']:.2f}", "Texto", mini=True)
                        with s4:
                            stat_box(f"{m['temporal']:.2f}", "Tiempo", mini=True)
                        st.code(explain(m))
            if visibles:
                st.subheader("Mapa de candidatos")
                try:
                    import folium
                    from streamlit_folium import st_folium

                    fmap = folium.Map(location=[q["location"]["lat"], q["location"]["lng"]], zoom_start=13)
                    folium.Marker([q["location"]["lat"], q["location"]["lng"]],
                                  tooltip=f"PERDIDO {q['id']}",
                                  icon=folium.Icon(color="red")).add_to(fmap)
                    for m in visibles:
                        c = m["candidato"]
                        folium.Marker([c["location"]["lat"], c["location"]["lng"]],
                                      tooltip=f"{c['id']} {m['score']*100:.0f}%",
                                      icon=folium.Icon(color="green" if m["notifica"] else "blue")).add_to(fmap)
                    st_folium(fmap, key="res_map", width=900, height=450)
                except Exception as e:
                    st.caption(f"Mapa no disponible ({e}).")

# ── TAB: Encontrados ────────────────────────────────────────────────
with tabF:
    st.subheader("Animales encontrados")
    found = dbmod.get_active_opuestos(con, "lost")
    if not found:
        st.info("Aún no hay avisos de encontrados.")
    else:
        f_filtro = st.selectbox("Filtrar por animal", ["Todos", "Perro", "Gato", "Otro"], key="filtro_found")
        inv = {"Todos": None, "Perro": "dog", "Gato": "cat", "Otro": "other"}
        lista = [a for a in found if not inv[f_filtro] or a["animal"] == inv[f_filtro]]
        stat_box(len(lista), "Encontrados")
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

# ── TAB: Publicar ───────────────────────────────────────────────────
with tabP:
    st.subheader("Publica un aviso de perdido o encontrado")
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
                st.image(foto, caption="Vista previa", width="stretch")
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
    if st.button("Publicar aviso", type="primary"):
        try:
            lat = float(st.session_state.get("reg_lat", 36.6826))
            lng = float(st.session_state.get("reg_lon", -6.1376))
            addr = st.session_state.get("addr_in", "Centro, Jerez")
            Path("data/uploads").mkdir(parents=True, exist_ok=True)
            img_path = f"data/uploads/{foto.name}" if foto else "data/seed/images/perro_marron_arenal.jpg"
            if foto:
                Path(img_path).write_bytes(foto.getbuffer())
            av = normalize_aviso({"type": tipo, "animal": animal, "color_primary": c1, "size": size,
                                  "has_collar": collar, "markings": [], "description_text": desc,
                                  "location": {"lat": lat, "lng": lng, "address_text": addr},
                                  "date_reported": "2026-09-23T12:00:00+02:00", "image_url": img_path,
                                  "contact_info": "", "status": "active"})
            av["image_embedding"] = get_image_embedding(img_path)
            dbmod.upsert_aviso(con, av)
            celebrate_search()
            st.success(f"Aviso `{av['id']}` publicado. Búscalo en la pestaña de buscar.")
        except Exception as e:
            st.error(f"Error: {e}")

# ── TAB 3: Alertas ────────────────────────────────────────────────────
with tab3:
    st.subheader("Alertas automáticas (score ≥85%)")
    rows = con.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT 50").fetchall()
    if rows:
        stat_box(len(rows), "Total alertas")
        st.table([dict(r) for r in rows])
    else:
        st.info("Aún no hay alertas. Lanza una búsqueda en la pestaña de buscar.")
    logp = Path("data/notifications.log")
    if logp.exists():
        with st.expander("Ver log técnico"):
            st.code(logp.read_text(encoding="utf-8")[-2000:])

