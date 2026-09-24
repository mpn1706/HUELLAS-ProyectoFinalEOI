"""Tests carrusel Inicio — REQ-UI-06 (privacidad: nunca contacto)."""
from ui_home import build_carousel_html, select_carousel_items


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


def test_html_vacio_invita_a_publicar():
    out = build_carousel_html([])
    assert "Publica el primero" in out
    assert "contact" not in out.lower()
