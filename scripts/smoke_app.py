"""Smoke test headless de app.py (sin navegador). Falla si el script lanza excepción."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"
at = AppTest.from_file(str(APP))
at.run()
assert not at.exception, f"La app lanzó excepción: {at.exception}"
print(f"SMOKE OK: app.py ejecuta sin excepciones ({len(at.tabs)} tabs)")
