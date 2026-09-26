"""Móvil: carrusel táctil (S115) + fichas sin deriva (S116) + botón junto al título (S117)."""
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


def test_vista_fija_solo_en_perdidos_y_encontrados_movil():
    # Esas dos páginas "bailaban" a los lados en móvil. El recorte lateral
    # solo se emite en ellas y solo bajo 640px: ni escritorio ni el resto
    # de páginas lo reciben.
    assert SRC.count("VISTA_FIJA_STYLE, unsafe_allow_html=True") == 2
    assert "@media (max-width:640px)" in SRC
    assert "overflow-x:clip" in SRC
    for pagina in ("perdidos", "encontrados"):
        at = AppTest.from_file(APP)
        at.session_state["page"] = pagina
        at.run(timeout=120)
        assert not at.exception, (pagina, at.exception)
        md = " ".join(str(m.value) for m in at.markdown)
        assert "overflow-x:clip" in md
    for pagina in ("inicio", "buscar", "publicar", "reencuentro"):
        at = AppTest.from_file(APP)
        at.session_state["page"] = pagina
        at.run(timeout=120)
        assert not at.exception, (pagina, at.exception)
        md = " ".join(str(m.value) for m in at.markdown)
        assert "VISTA_FIJA_STYLE" not in md and "overflow-x:clip" not in md


def test_boton_inicio_al_lado_del_titulo_en_movil():
    # Estado 1d8706b: hueco mediano en las filas de título (móvil y escritorio
    # iguales) + fila forzada en móvil para que el botón no caiga encima.
    assert SRC.count('[1, 30], gap="medium"') == 2
    i_mob = SRC.index("@media (max-width:640px)")
    i_desk = SRC.index("@media (min-width:641px)")
    assert "column-gap" not in SRC[i_mob:i_desk]  # en móvil manda la fila, no el hueco
    assert "@media (max-width:640px)" in SRC
    assert 'stHorizontalBlock"]:has(div[class*="st-key-home"])' in SRC
    assert "flex-direction:row" in SRC
    assert 'stColumn"]:has(div[class*="st-key-home"])' in SRC


def test_aire_inicio_solo_en_movil():
    # El compactado dejó pegados cabecera-hero y carrusel-contadores: se
    # devuelve aire solo bajo 640px (escritorio intacto).
    moviles = SRC.split("@media (max-width:640px)")[1:]
    assert any(".huellas-hero { margin-top:0; }" in b
               and ".huellas-vp { margin-bottom:1rem; }" in b for b in moviles)
    desks = SRC.split("@media (min-width:641px)")[1:]
    assert any(".huellas-vp { margin-bottom:0.75rem; }" in b for b in desks)  # aire contadores solo PC
