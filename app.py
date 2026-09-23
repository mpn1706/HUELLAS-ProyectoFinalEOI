"""MascotasLost&Found — MVP Streamlit (REQ-09, CU-01..CU-05).

Ejecución local: streamlit run app.py
Habla solo español. Nunca afirma identidad: solo "posible coincidencia".
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
st.set_page_config(page_title="HUELLAS", page_icon="🐾", layout="wide")
st.title("🐾 HUELLAS")
st.subheader("MascotasLost&Found — Jerez de la Frontera")
st.caption("Sistema de posibles coincidencias lost ↔ found. " + AVISO_LEGAL)


def show_image(path: str, caption: str = ""):
    """Muestra imagen si existe; si no, placeholder textual (rutas locales ausentes en Cloud)."""
    if path and Path(path).exists():
        st.image(path, caption=caption, use_container_width=True)
    else:
        st.info("📷 Imagen no disponible en este despliegue." + (f" {caption}" if caption else ""))


def get_con():
    return dbmod.connect(DB)


def ensure_db():
    """Conecta y auto-carga el seed si la DB está vacía.

    En Streamlit Cloud el filesystem es efímero y data/huellas.db no viaja
    en el repo (gitignored): los JSON de data/seed sí, así que la app se
    auto-abastece sin comandos ni secretos. Trazable a REQ-03.8 + REQ-09.
    """
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


with st.sidebar:
    st.header("Datos demo")
    if st.button("Cargar seed Jerez (17 avisos)"):
        import subprocess

        subprocess.run(["python", "scripts/make_seed.py"], check=False)
        subprocess.run(["python", "scripts/load_seed.py", DB], check=False)
        st.success("Seed cargada.")
    if st.button("Expirar avisos >30 días"):
        con = get_con()
        n = dbmod.expire_old(con, 30)
        st.info(f"Avisos expirados: {n}")
    st.divider()
    st.markdown("Umbrales: **>=85%** notifica · **>=65%** lista · Fórmula `0.40V+0.30G+0.20T+0.10t`")

con = ensure_db()

avisos_lost = dbmod.get_active_opuestos(con, "found")  # lost activos
avisos_found = dbmod.get_active_opuestos(con, "lost")  # found activos
all_lost = [a for a in (dbmod.get_aviso(con, r["id"]) for r in con.execute("SELECT id FROM avisos WHERE status='active' AND type='lost'").fetchall()) if a]

tab1, tab2, tab3 = st.tabs(["🔍 Buscar coincidencias", "➕ Registrar aviso", "🔔 Notificaciones"])

with tab1:
    st.subheader("Busca a tu mascota entre los avisos de encontrados")
    if not all_lost:
        st.info("No hay avisos lost activos.")
    else:
        etiquetas = {a["id"]: f"[{a['id']}] {a['animal']} · {a['color_primary']} · {a['size']}" for a in all_lost}
        qid = st.selectbox("Aviso perdido", [a["id"] for a in all_lost],
                           format_func=lambda i: etiquetas.get(i, i))
        q = dbmod.get_aviso(con, qid)
        col_foto, col_datos = st.columns([1, 1])
        with col_foto:
            show_image(q["image_url"], caption=f"Foto registrada · {q['id']}")
        with col_datos:
            st.markdown(f"### [{q['id']}] {q['animal']} · {q['color_primary']} · {q['size']}")
            st.write(q["description_text"])
            st.write(f"Collar: {'sí' if q['has_collar'] else 'no'} · Fecha: {effective_date(q).date()} · {q['location'].get('address_text', '')}")
        foto_q = st.file_uploader("Sube una foto actual para refinar la búsqueda visual (opcional)",
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
            st.caption("Búsqueda visual con tu foto subida.")
        if st.button("Buscar"):
            cands = dbmod.get_active_opuestos(con, "lost")
            matches = retrieve(q, cands, embed_fn, semantic_similarity)
            notificados = notificar(con, q["id"], matches)
            if notificados:
                st.success(f"{len(notificados)} posible(s) coincidencia(s) destacada(s) >=85% (ver Notificaciones).")
            if not matches:
                st.info("Sin candidatos >=65%. Quedan indexados.")
            for m in matches:
                c = m["candidato"]
                etiqueta = "🌟 Posible coincidencia destacada" if m["notifica"] else "Posible coincidencia"
                with st.expander(f"{etiqueta} — {c['id']} · {m['score']*100:.1f}% · {m['dist_km']} km"):
                    col1, col2 = st.columns(2)
                    for col, av, tag in ((col1, q, "PERDIDO"), (col2, c, "ENCONTRADO")):
                        with col:
                            st.markdown(f"**{tag}** `{av['id']}`")
                            show_image(av["image_url"])
                            st.write(av["description_text"])
                            st.write(f"{av['color_primary']} · {av['size']} · collar {av['has_collar']} · {av['location'].get('address_text','')}")
                    st.code(explain(m))
            # Mapa
            try:
                import folium
                from streamlit_folium import st_folium

                fmap = folium.Map(location=[q["location"]["lat"], q["location"]["lng"]], zoom_start=13)
                folium.Marker([q["location"]["lat"], q["location"]["lng"]], tooltip=f"PERDIDO {q['id']}",
                              icon=folium.Icon(color="red")).add_to(fmap)
                for m in matches[:10]:
                    c = m["candidato"]
                    folium.Marker([c["location"]["lat"], c["location"]["lng"]],
                                  tooltip=f"{c['id']} {m['score']*100:.0f}%",
                                  icon=folium.Icon(color="green" if m["notifica"] else "blue")).add_to(fmap)
                st_folium(fmap, width=900, height=450)
            except Exception as e:
                st.caption(f"Mapa no disponible ({e}).")

with tab2:
    st.subheader("Nuevo aviso (foto + texto + ubicación + fecha)")
    tipo = st.selectbox("Tipo", ["lost", "found"])
    animal = st.selectbox("Animal", ["dog", "cat", "other"])
    foto = st.file_uploader("Foto", type=["jpg", "jpeg", "png"])
    if foto:
        st.image(foto, caption="Vista previa", use_container_width=True)
    desc = st.text_area("Descripción libre", "Perro marrón mediano con mancha blanca en el pecho, collar rojo.")
    c1 = st.text_input("color_primary", "marrón")
    size = st.selectbox("Tamaño", ["small", "medium", "large"])
    collar = st.checkbox("¿Lleva collar?", True)
    lat = st.number_input("lat", value=36.6826, format="%.4f")
    lng = st.number_input("lng", value=-6.1376, format="%.4f")
    addr = st.text_input("Dirección (texto)", "Centro, Jerez")
    if st.button("Guardar y buscar coincidencias"):
        try:
            Path("data/uploads").mkdir(parents=True, exist_ok=True)
            img_path = f"data/uploads/{foto.name}" if foto else "data/seed/images/perro_marron_arenal.jpg"
            if foto:
                Path(img_path).write_bytes(foto.getbuffer())
            raw = {"type": tipo, "animal": animal, "color_primary": c1, "size": size,
                   "has_collar": collar, "markings": [], "description_text": desc,
                   "location": {"lat": lat, "lng": lng, "address_text": addr},
                   "date_reported": "2026-09-23T12:00:00+02:00", "image_url": img_path,
                   "contact_info": "", "status": "active"}
            av = normalize_aviso(raw)
            av["image_embedding"] = get_image_embedding(img_path)
            dbmod.upsert_aviso(con, av)
            st.success(f"Aviso {av['id']} guardado. Recarga y búscalo en la pestaña 1.")
        except Exception as e:
            st.error(f"Error: {e}")

with tab3:
    st.subheader("Log de notificaciones (>=85%)")
    rows = con.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT 50").fetchall()
    if rows:
        st.table([dict(r) for r in rows])
    else:
        st.info("Aún no hay notificaciones.")
    logp = Path("data/notifications.log")
    if logp.exists():
        st.code(logp.read_text(encoding="utf-8")[-2000:])
