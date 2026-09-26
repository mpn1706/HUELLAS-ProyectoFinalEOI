"""Móvil: el carrusel no se traba al tocar (S115) + fichas sin deriva lateral (S116)."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path("app.py").resolve())
SRC = Path("app.py").read_text(encoding="utf-8")


def test_pausa_carrusel_solo_con_hover_real():
    # En táctil :hover se queda "enganchado" y paraba el carrusel: la pausa
    # vive dentro de @media (hover:hover) y solo aparece una vez.
    assert "@media (hover:hover)" in SRC
    assert SRC.count(".huellas-vp:hover .huellas-trk") == 1
    assert SRC.index("@media (hover:hover)") < SRC.index(".huellas-vp:hover .huellas-trk")
    assert "touch-action:pan-y" in SRC  # el scroll vertical no lucha con el marquee


def test_fichas_usan_foto_fluida_en_perdidos_y_encontrados():
    # La foto fija de 380px desbordaba la columna en el móvil y la página se
    # podía mover en horizontal. Las fichas usan show_image(fluido=True), que
    # ocupa el ancho de la columna sin desbordar. Sin CSS global: el header,
    # los filtros y las descripciones quedan intactos.
    assert "FICHA_IMG_STYLE" not in SRC
    assert SRC.count('caption=f"Foto · {a[\'id\']}", fluido=True') == 2
    for pagina in ("perdidos", "encontrados"):
        at = AppTest.from_file(APP)
        at.session_state["page"] = pagina
        at.run(timeout=120)
        assert not at.exception, (pagina, at.exception)
