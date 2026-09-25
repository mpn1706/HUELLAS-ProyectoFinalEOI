"""Sidebar: divisoria tras Soporte + desfile de mascotas (S110)."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

from ui_home import build_marcha_html

APP = str(Path("app.py").resolve())


def test_marcha_duplica_pista_y_alterna():
    h = build_marcha_html()
    assert 'class="huellas-march"' in h and 'class="huellas-track"' in h
    assert h.count('class="huellas-pet"') == 24  # 12 + 12 (pista larga, sin vacíos)
    assert h.count("<svg") == 24
    assert "#23201B" in h and "#E30613" in h  # paleta negro/rojo


def test_sidebar_muestra_divisoria_y_desfile():
    at = AppTest.from_file(APP)
    at.run(timeout=120)
    assert not at.exception, at.exception
    md = " ".join(str(m.value) for m in at.markdown)
    assert "huellas-march" in md and "huellas-track" in md
    assert len(at.divider) >= 1  # divisoria(s) negra(s) del sidebar
