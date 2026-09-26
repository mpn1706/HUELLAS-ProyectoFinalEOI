"""Sidebar: divisoria tras Soporte + desfile de mascotas (S110)."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

from ui_home import build_marcha_html

APP = str(Path("app.py").resolve())
SRC = Path("app.py").read_text(encoding="utf-8")


def test_contenido_no_queda_bajo_la_barra():
    # Con el sidebar abierto el header se cortaba por arriba (padding 0.2rem):
    # aire de 1rem para librar la barra fija.
    assert "padding-top: 1rem !important" in SRC


def test_marcha_duplica_pista_y_alterna():
    h = build_marcha_html()
    assert 'class="huellas-march"' in h and 'class="huellas-track"' in h
    assert h.count('class="huellas-pet"') == 24  # 12 + 12 (pista larga, sin vacíos)
    assert h.count("<svg") == 24
    assert "#23201B" in h and "#E30613" in h  # paleta negro/rojo


def test_marcha_no_colisiona_con_tira_digitos():
    # La tira de dígitos (.huellas-track suelta, display:block) pisaba el
    # desfile: las reglas van acotadas a .huellas-march (más especificidad).
    assert ".huellas-march .huellas-track" in SRC
    assert ".huellas-march .huellas-pet" in SRC


def test_marcha_invertida_va_a_la_izquierda():
    h = build_marcha_html(invertida=True)
    assert 'class="huellas-march inv"' in h
    assert h.count('class="huellas-pet"') == 24
    assert ".huellas-march.inv .huellas-track" in SRC  # pista al revés
    assert ".huellas-march.inv .huellas-pet svg" in SRC  # figuras espejadas


def test_sidebar_muestra_divisoria_y_desfile():
    at = AppTest.from_file(APP)
    at.run(timeout=120)
    assert not at.exception, at.exception
    md = " ".join(str(m.value) for m in at.markdown)
    assert md.count("huellas-march") >= 2  # tira + contratiira
    assert "huellas-march inv" in md
    assert len(at.divider) >= 1  # divisoria(s) negra(s) del sidebar
