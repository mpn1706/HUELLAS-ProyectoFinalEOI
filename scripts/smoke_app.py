"""Smoke test headless de app.py (sin navegador). Falla si el script lanza excepción."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def _texts(at) -> str:
    try:
        return " ".join(str(t.value) for t in at.text) + " " + " ".join(str(m.value) for m in at.markdown)
    except Exception:
        return ""


for pagina in ("inicio", "buscar", "perdidos", "encontrados", "reencuentro",
                 "publicar", "protectoras", "tiempo", "legal"):
    at = AppTest.from_file(str(APP))
    at.session_state["page"] = pagina
    at.run(timeout=60)
    assert not at.exception, f"La app lanzó excepción en {pagina}: {at.exception}"
print("SMOKE OK: app.py ejecuta sin excepciones (9 páginas: inicio/buscar/perdidos/encontrados/reencuentro/publicar/protectoras/tiempo/legal)")
