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


def test_fichas_ciñen_foto_solo_en_perdidos_y_encontrados():
    # La foto fija de 380px desbordaba la columna en el móvil y la página se
    # podía mover en horizontal. El estilo solo se emite en esas dos páginas
    # (el resto, que va bien, queda intacto).
    assert SRC.count("FICHA_IMG_STYLE, unsafe_allow_html=True") == 2
    assert "[data-testid=\"stImage\"] img" in SRC
    for pagina in ("perdidos", "encontrados"):
        at = AppTest.from_file(APP)
        at.session_state["page"] = pagina
        at.run(timeout=120)
        assert not at.exception, (pagina, at.exception)
        md = " ".join(str(m.value) for m in at.markdown)
        assert "max-width:100%" in md
