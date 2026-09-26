"""Móvil: carrusel no se traba al tocar, fotos sin desbordar, sin scroll lateral (S114)."""
from pathlib import Path

SRC = Path("app.py").read_text(encoding="utf-8")


def test_pausa_carrusel_solo_con_hover_real():
    # En táctil :hover se queda "enganchado" y paraba el carrusel: la pausa
    # vive dentro de @media (hover:hover) y solo aparece una vez.
    assert "@media (hover:hover)" in SRC
    assert SRC.count(".huellas-vp:hover .huellas-trk") == 1
    assert SRC.index("@media (hover:hover)") < SRC.index(".huellas-vp:hover .huellas-trk")
    assert "touch-action:pan-y" in SRC  # el scroll vertical no lucha con el marquee


def test_imagenes_no_desbordan_columna():
    # show_image() fija width=380: en móvil la columna es más estrecha y la
    # foto sobresalía a la derecha. Se ciñe por CSS sin tocar el Python.
    assert '[data-testid="stImage"] img' in SRC
    assert "max-width:100%" in SRC
    assert '[data-testid="stColumn"]' in SRC and "min-width:0" in SRC


def test_pagina_sin_desplazamiento_lateral():
    # Algún elemento ancho permitía mover la vista a izq/der y descuadraba
    # la navegación: el contenedor principal recorta el desborde (clip con
    # fallback a hidden para navegadores viejos).
    assert '[data-testid="stAppViewContainer"]' in SRC
    assert "overflow-x:clip" in SRC
    assert "overflow-x:hidden" in SRC
