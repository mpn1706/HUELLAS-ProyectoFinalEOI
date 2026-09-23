"""HUELLAS — MascotasLost&Found (Jerez de la Frontera).

MVP Streamlit — REQ-09, CU-01..CU-05.
Nunca afirma identidad: solo "posible coincidencia" + aviso legal.
Logo: assets/logo.png si existe (si no, huella 🐾).
"""
from pathlib import Path

import streamlit as st

from agents import db as dbmod
from agents.ingestor import effective_date, normalize_aviso
from agents.matcher import explain
from agents.notifier import AVISO_LEGAL, notificar
from agents.vision import get_image_embedding
from rag.embeddings import semantic_similarity
from rag.retrieval import retrieve

DB = "data/huellas.db"
LOGO = next((p for p in ("assets/logo.png", "assets/logo.jpg", "assets/logo.jpeg", "assets/logo.webp")
             if Path(p).exists()), None)
FONDO = next((p for p in ("assets/fondo.png", "assets/fondo.jpg", "assets/fondo.jpeg")
              if Path(p).exists()), None)
ANIMAL_EMOJI = {"dog": "🐶", "cat": "🐱", "other": "🐾"}
TAGLINE = "Agente de Búsqueda y Comparativa Visual de Animales Perdidos"
SUBTITLE = "Encuentra a tu mascota entre los avisos de avistamientos en Jerez de la Frontera"

st.set_page_config(page_title="HUELLAS", page_icon=LOGO if LOGO else "🐾", layout="wide")


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
        [data-testid="stDivider"] {{
            border-top: 2px solid #23201B !important;
            background: transparent;
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
        st.image(path, caption=caption, use_container_width=True)
    else:
        st.info("📷 Imagen no disponible en este despliegue." + (f" {caption}" if caption else ""))


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


def animal_tag(a: dict) -> str:
    return f"{ANIMAL_EMOJI.get(a.get('animal'), '🐾')} {a.get('animal')} · {a.get('color_primary')} · {a.get('size')}"


def etiqueta_corta(a: dict) -> str:
    return f"[{a['id']}] {animal_tag(a)}"


# ── Cabecera (si hay logo con wordmark, no se duplica el título) ──
if LOGO:
    hc1, hc2 = st.columns([2, 5])
    with hc1:
        st.image(get_logo_img(), use_container_width=True)
    with hc2:
        st.markdown(f"## {TAGLINE}")
        st.caption(SUBTITLE)
else:
    hc1, hc2 = st.columns([1, 6])
    with hc1:
        st.markdown("# 🐾")
    with hc2:
        st.title("HUELLAS")
        st.markdown(f"## {TAGLINE}")
        st.caption(SUBTITLE)

con = ensure_db()

n_lost = con.execute("SELECT COUNT(*) FROM avisos WHERE status='active' AND type='lost'").fetchone()[0]
n_found = con.execute("SELECT COUNT(*) FROM avisos WHERE status='active' AND type='found'").fetchone()[0]
n_notif = con.execute("SELECT COUNT(*) FROM notifications").fetchone()[0]
m1, m2, m3 = st.columns(3)
m1.metric("🔴 Perdidos activos", n_lost)
m2.metric("🟢 Encontrados activos", n_found)
m3.metric("🔔 Alertas ≥85%", n_notif)

# ── Barra lateral ─────────────────────────────────────────────────────
with st.sidebar:
    if LOGO:
        st.image(get_logo_img(), use_container_width=True)
    else:
        st.header("🐾 HUELLAS")
    st.caption(TAGLINE)
    with st.expander("⚙️ Cómo puntúa (fórmula cerrada)"):
        st.code("0.40·visual + 0.30·geo\n+ 0.20·texto + 0.10·temporal")
        st.caption("≥85% alerta · ≥65% en lista · radio 15 km · ventana 30 días")
    st.divider()
    st.subheader("Datos demo")
    if st.button("🔄 Cargar seed Jerez (17 avisos)"):
        import subprocess

        subprocess.run(["python", "scripts/make_seed.py"], check=False)
        subprocess.run(["python", "scripts/load_seed.py", DB], check=False)
        st.success("Seed cargada.")
    if st.button("🗂️ Expirar avisos >30 días"):
        n = dbmod.expire_old(get_con(), 30)
        st.info(f"Avisos expirados: {n}")

all_lost = [a for a in (dbmod.get_aviso(con, r["id"]) for r in
                        con.execute("SELECT id FROM avisos WHERE status='active' AND type='lost'").fetchall()) if a]

tab1, tab2, tab3 = st.tabs(["🔍 Buscar a mi mascota", "➕ Publicar aviso", "🔔 Alertas"])

# ── TAB 1: Buscar ─────────────────────────────────────────────────────
with tab1:
    if not all_lost:
        st.info("No hay avisos de perdidos activos. Publica uno en la pestaña ➕.")
    else:
        st.subheader("1️⃣ Elige tu aviso")
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
                st.caption(f"Collar: {'sí' if q['has_collar'] else 'no'} · "
                           f"Visto: {effective_date(q).date()} · {q['location'].get('address_text', '')}")

        st.subheader("2️⃣ Foto actual (opcional)")
        foto_q = st.file_uploader("Sube una foto reciente para afinar la búsqueda visual",
                                  type=["jpg", "jpeg", "png"], key="q_foto")
        embed_fn = visual_fn_factory()
        if foto_q:
            st.image(foto_q, caption="Vista previa de tu foto", use_container_width=True)
            Path("data/uploads").mkdir(parents=True, exist_ok=True)
            qpath = "data/uploads/_query_preview.jpg"
            Path(qpath).write_bytes(foto_q.getbuffer())
            q_emb = get_image_embedding(qpath)
            base_fn = embed_fn
            embed_fn = lambda a, _b=base_fn, _q=q_emb, _qid=q["id"]: _q if a["id"] == _qid else _b(a)
            st.caption("✅ Búsqueda visual con tu foto subida.")

        st.subheader("3️⃣ Lanza la búsqueda")
        f1, f2 = st.columns(2)
        with f1:
            umbral_vista = st.slider("Mostrar desde (%)", 50, 100, 65,
                                     help="Solo filtra lo que se muestra, no cambia el score.")
        with f2:
            topn = st.slider("Máx. resultados", 3, 15, 8)
        if st.button("🔍 Buscar coincidencias", type="primary"):
            cands = dbmod.get_active_opuestos(con, "lost")
            matches = retrieve(q, cands, embed_fn, semantic_similarity)
            notificados = notificar(con, q["id"], matches)
            k1, k2 = st.columns(2)
            k1.metric("🌟 Destacadas ≥85%", sum(1 for m in matches if m["notifica"]))
            k2.metric("📋 En lista ≥65%", len(matches))
            if notificados:
                st.success("Nueva alerta generada: hay coincidencias destacadas (ver pestaña 🔔).")
            visibles = [m for m in matches if m["score"] * 100 >= umbral_vista][:topn]
            if not visibles:
                st.info("Sin candidatos con ese filtro. Baja el umbral de vista o espera nuevos avisos.")
            for m in visibles:
                c = m["candidato"]
                badge = "🌟 POSIBLE COINCIDENCIA DESTACADA" if m["notifica"] else "🔎 Posible coincidencia"
                with st.container(border=True):
                    st.markdown(f"**{badge}** · `{c['id']}` · **{m['score']*100:.1f}%** · 📍 {m['dist_km']} km")
                    st.progress(min(max(m["score"], 0.0), 1.0))
                    r1, r2 = st.columns(2)
                    with r1:
                        show_image(q["image_url"], caption=f"Perdido · {q['id']}")
                    with r2:
                        show_image(c["image_url"], caption=f"Encontrado · {c['id']}")
                        st.write(c["description_text"])
                    with st.expander("📊 Por qué este resultado"):
                        s1, s2, s3, s4 = st.columns(4)
                        s1.metric("👁️ Visual", f"{m['visual']:.2f}")
                        s2.metric("📍 Geo", f"{m['geo']:.2f}")
                        s3.metric("📝 Texto", f"{m['texto']:.2f}")
                        s4.metric("🕒 Tiempo", f"{m['temporal']:.2f}")
                        st.code(explain(m))
            if visibles:
                st.subheader("🗺️ Mapa de candidatos")
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
                    st_folium(fmap, width=900, height=450)
                except Exception as e:
                    st.caption(f"Mapa no disponible ({e}).")

# ── TAB 2: Registrar ──────────────────────────────────────────────────
with tab2:
    st.subheader("Publica un aviso de perdido o encontrado")
    with st.container(border=True):
        r1, r2 = st.columns([1, 1])
        with r1:
            tipo = st.selectbox("Tipo de aviso", ["lost", "found"],
                                format_func=lambda t: "🔴 Mascota PERDIDA" if t == "lost" else "🟢 Animal ENCONTRADO")
            animal = st.selectbox("Animal", ["dog", "cat", "other"],
                                  format_func=lambda a: {"dog": "🐶 Perro", "cat": "🐱 Gato",
                                                         "other": "🐾 Otro"}.get(a, a))
            foto = st.file_uploader("Foto del animal", type=["jpg", "jpeg", "png"])
            if foto:
                st.image(foto, caption="Vista previa", use_container_width=True)
            else:
                st.caption("📷 Sube una foto: es la señal que más pesa (40%).")
        with r2:
            desc = st.text_area("Descripción libre",
                                "Perro marrón mediano con mancha blanca en el pecho, collar rojo.")
            c1 = st.text_input("Color principal", "marrón")
            size = st.selectbox("Tamaño", ["small", "medium", "large"],
                                format_func=lambda s: {"small": "Pequeño", "medium": "Mediano",
                                                       "large": "Grande"}.get(s, s))
            collar = st.checkbox("¿Lleva collar?", True)
            lat = st.number_input("Latitud", value=36.6826, format="%.4f")
            lng = st.number_input("Longitud", value=-6.1376, format="%.4f")
            addr = st.text_input("Zona (texto)", "Centro, Jerez")
    if st.button("💾 Publicar aviso", type="primary"):
        try:
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
            st.balloons()
            st.success(f"Aviso `{av['id']}` publicado. Búscalo en la pestaña 🔍.")
        except Exception as e:
            st.error(f"Error: {e}")

# ── TAB 3: Alertas ────────────────────────────────────────────────────
with tab3:
    st.subheader("Alertas automáticas (score ≥85%)")
    st.caption("Se generan solas al buscar. " + AVISO_LEGAL)
    rows = con.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT 50").fetchall()
    if rows:
        st.metric("Total alertas", len(rows))
        st.table([dict(r) for r in rows])
    else:
        st.info("Aún no hay alertas. Lanza una búsqueda en 🔍.")
    logp = Path("data/notifications.log")
    if logp.exists():
        with st.expander("📄 Ver log técnico"):
            st.code(logp.read_text(encoding="utf-8")[-2000:])
