"""Títulos con botón rojo ⏪ a Inicio (S111)."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path("app.py").resolve())
PAGES = ["buscar", "publicar", "perdidos", "encontrados", "reencuentro"]


def _ir(pagina):
    at = AppTest.from_file(APP)
    at.session_state["page"] = pagina
    at.run(timeout=120)
    assert not at.exception, (pagina, at.exception)
    return at


def test_titulos_llevan_boton_inicio():
    for page in PAGES:
        at = _ir(page)
        assert any(b.key.startswith("home_") for b in at.button), page


def test_boton_inicio_navega():
    at = _ir("publicar")
    key = next(b.key for b in at.button if b.key.startswith("home_"))
    at.button(key=key).click()
    at.run(timeout=120)
    assert not at.exception, at.exception
    assert at.session_state["page"] == "inicio"
