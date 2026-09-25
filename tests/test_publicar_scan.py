"""Publicar: scan lado a lado + banner post-publicación con métricas frescas."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path("app.py").resolve())
SRC = Path("app.py").read_text(encoding="utf-8")


def test_scanrow_no_envuelve_insignia():
    # La insignia va a la DERECHA de la foto (REQ-UI-21): fila sin wrap y
    # tamaños contenidos para que quepa en la columna estrecha de Publicar.
    i = SRC.index(".huellas-scanrow {")
    bloque = SRC[i:i + 700]
    assert "flex-wrap:nowrap" in bloque
    assert ".huellas-scanrow .huellas-scanbadge" in SRC
    assert ".huellas-scanrow .huellas-analizada" in SRC


def _ir_publicar(**state):
    at = AppTest.from_file(APP)
    at.session_state["page"] = "publicar"
    for k, v in state.items():
        at.session_state[k] = v
    at.run(timeout=120)
    assert not at.exception, at.exception
    return at


def test_banner_repite_resultado_del_cruce():
    at = _ir_publicar(pub_result={"aviso_id": "av_x", "n": 1, "top_id": "found_001",
                                  "top_score": 0.85, "top_tipo": "found"})
    ok = " ".join(str(s.value) for s in at.success)
    assert "av_x" in ok and "1 alerta(s)" in ok
    md = " ".join(str(m.value) for m in at.markdown)
    assert "found_001" in md  # tarjeta de coincidencia


def test_banner_sin_coincidencias_y_descarte():
    at = _ir_publicar(pub_result={"aviso_id": "av_y", "n": 0})
    info = " ".join(str(s.value) for s in at.info)
    assert "sin coincidencias" in info
    at.button(key="pub_otro").click()
    at.run(timeout=120)
    assert not at.exception, at.exception
    assert "pub_result" not in at.session_state
    assert all("av_y" not in str(s.value) for s in at.success)
