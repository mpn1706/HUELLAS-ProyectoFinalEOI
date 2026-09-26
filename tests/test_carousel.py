"""Tests carrusel Inicio — REQ-UI-06 (privacidad: nunca contacto)."""
import base64
import io
from pathlib import Path

from ui_home import (
    build_carousel_html,
    build_counts_html,
    make_carousel_thumb,
    select_carousel_items,
)


def _aviso(i, tipo="lost", contact="610 204 518 · a@x.es"):
    return {
        "id": f"t_{i:02d}", "type": tipo, "animal": "dog",
        "color_primary": "marrón", "size": "medium", "has_collar": False,
        "markings": [], "description_text": "perro marrón",
        "location": {"lat": 36.68, "lng": -6.13, "address_text": "Calle Larga"},
        "date_reported": f"2026-09-{10 + i:02d}T10:00:00+02:00",
        "date_last_seen": None, "image_url": "data/seed/images/x.jpg",
        "image_embedding": None, "contact_info": contact, "status": "active",
    }


def test_select_excluye_contacto_y_limita_a_12():
    avisos = [_aviso(i, tipo="lost" if i % 2 else "found") for i in range(15)]
    cards = select_carousel_items(avisos)
    assert len(cards) == 12
    for c in cards:
        assert "contact_info" not in c
        assert "contact" not in " ".join(c.keys()).lower()


def test_select_solo_activos_y_con_etiqueta():
    avisos = [_aviso(1), _aviso(2, tipo="found")]
    avisos[0]["status"] = "resolved"
    cards = select_carousel_items(avisos)
    assert [c["id"] for c in cards] == ["t_02"]
    assert cards[0]["etiqueta"] == "Avistado"
    assert "·" in cards[0]["titulo"]  # Especie · color
    assert cards[0]["zona"] == "Calle Larga"


def test_html_no_incluye_contacto_ni_telefono():
    cards = select_carousel_items([_aviso(1), _aviso(2, tipo="found")])
    with_uri = [dict(c, img_uri="data:image/jpeg;base64,AAA") for c in cards]
    out = build_carousel_html(with_uri)
    assert "610 204 518" not in out
    assert "a@x.es" not in out
    assert "contact" not in out.lower()
    assert "?aviso=t_01" in out and "?aviso=t_02" in out
    assert "Perdido" in out and "Avistado" in out
    assert 'target="_self"' in out


def test_extra_reencuentros_y_resueltos_visibles():
    avisos = [_aviso(1), _aviso(2, tipo="found")]
    avisos[0]["status"] = "resolved"
    cards = select_carousel_items(avisos, extra={"t_01": "cerrado"})
    assert [c["id"] for c in cards] == ["t_02", "t_01"] or \
        {c["id"] for c in cards} == {"t_01", "t_02"}
    por_id = {c["id"]: c for c in cards}
    assert por_id["t_01"]["extra"] == "Caso cerrado"
    assert por_id["t_02"]["extra"] is None
    cards2 = select_carousel_items(avisos, extra={"t_02": "revision"})
    assert {c["id"]: c["extra"] for c in cards2} == {"t_02": "En revisión"}
    with_uri = [dict(c, img_uri="") for c in cards]
    out = build_carousel_html(with_uri)
    assert "Caso cerrado" in out and "huellas-cd-et cerr" in out
    assert "610 204 518" not in out


def test_html_vacio_invita_a_publicar():
    out = build_carousel_html([])
    assert "Publica el primero" in out
    assert "contact" not in out.lower()


def test_thumb_letterbox_300x208_y_centrada(tmp_path):
    from PIL import Image

    ancha = tmp_path / "ancha.jpg"
    Image.new("RGB", (800, 200), (200, 30, 30)).save(ancha)
    alta = tmp_path / "alta.jpg"
    Image.new("RGB", (100, 800), (30, 30, 200)).save(alta)
    for fp in (ancha, alta):
        uri = make_carousel_thumb(str(fp))
        assert uri.startswith("data:image/jpeg;base64,")
        img = Image.open(io.BytesIO(base64.b64decode(uri.split(",", 1)[1])))
        assert img.size == (300, 208)  # lienzo fijo: sin recortes, animal entero
    assert make_carousel_thumb(str(tmp_path / "noexiste.jpg")) == ""


def test_counts_con_links_y_sin_contacto():
    out = build_counts_html(5, 11, 0)
    assert "?page=perdidos" in out
    assert "?page=encontrados" in out
    assert "?page=reencuentro" in out
    assert ">5<" in out and ">11<" in out and ">0<" in out
    assert "perdidos activos" in out and "avistamientos" in out and "reencuentros" in out
    assert "contact" not in out.lower()
    assert out.count('target="_self"') == 3


def test_etiquetas_sin_subrayado_azul():
    # Toda la tarjeta es un <a>: se anula el subrayado en el ancla Y en los
    # descendientes (la línea puede propagarse desde el <a> y el none en el
    # hijo solo no la quita).
    css = Path("app.py").read_text(encoding="utf-8")
    assert "a.huellas-cd-link" in css
    assert "a.huellas-cd-link *" in css
    assert "text-decoration:none" in css
    assert "border-bottom:none" in css


def test_subtitulo_en_tira_hacia_la_derecha():
    # Una sola copia que cruza todo el ancho; entrada con ease-out para
    # enlazar suave con el crucero lineal (sin tirón) + congelado reducido.
    css = Path("app.py").read_text(encoding="utf-8")
    assert "huellas-tira-track" in css
    assert css.count("Mira quién te está esperando. Si reconoces a alguno, avisa.</span>") == 1
    assert "@keyframes huellas-tira" in css
    assert "contain:layout" in css  # recalcula solo la tira, sin tirones
    assert "animation-delay:1.5s" in css  # arranca tras la tormenta de carga
    assert "animation-fill-mode:backwards" in css  # espera oculta, sin salto
    assert "cubic-bezier(0.25, 0, 0.7, 0.85)" in css  # S suave: sin latigazo
    assert "30% { left:0;" in css
    assert "8s linear infinite" in css
    assert ".huellas-tira-track { animation:none !important; }" in css


def test_inicio_compacto_tras_hero():
    # Todo lo que cuelga del hero (botones, carrusel, contadores) sube con
    # bloques más juntos, solo en inicio.
    from streamlit.testing.v1 import AppTest

    css = Path("app.py").read_text(encoding="utf-8")
    assert "Solo inicio: bloques más juntos" in css
    at = AppTest.from_file(str(Path("app.py").resolve()))
    at.session_state["page"] = "inicio"
    at.run(timeout=120)
    assert not at.exception, at.exception
