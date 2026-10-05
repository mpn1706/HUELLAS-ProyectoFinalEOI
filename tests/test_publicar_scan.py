"""Publicar: scan lado a lado + confirmación abajo sin análisis + popup buscar-primero."""
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


def test_confirmacion_abajo_sin_analisis():
    # Publicar solo registra: éxito abajo del todo, sin tarjeta de
    # coincidencia ni alertas (eso vive solo en Buscar).
    at = _ir_publicar(pub_dialog_ok=True, pub_ok="av_x")
    ok = " ".join(str(s.value) for s in at.success)
    assert "av_x" in ok and "publicado" in ok
    assert "alerta" not in ok
    md = " ".join(str(m.value) for m in at.markdown)
    assert "Cruce automático" not in md


def test_publicar_otro_limpia_confirmacion():
    at = _ir_publicar(pub_dialog_ok=True, pub_ok="av_y")
    at.button(key="pub_otro").click()
    at.run(timeout=120)
    assert not at.exception, at.exception
    assert "pub_ok" not in at.session_state
    assert all("av_y" not in str(s.value) for s in at.success)


def test_dialog_buscar_primero_no_rompe():
    # Entrada fresca: el popup se ejecuta y la página sigue renderizando.
    at = _ir_publicar()
    md = " ".join(str(m.value) for m in at.markdown)
    assert "Publica un aviso" in md


def test_dialog_no_se_autoconsume():
    # El popup sobrevive a reruns hasta que elijas: la entrada fresca NO
    # deja el flag puesto (antes se lo tragaba el rerun del mapa).
    at = _ir_publicar()
    assert "pub_dialog_ok" not in at.session_state


def test_pin_fijado_sobrevive_rerun():
    # Tras clicar el mapa, el mensaje con la chincheta y el anillo sigue
    # visible (no se lo traga el re-render del mapa).
    at = _ir_publicar(pub_dialog_ok=True, reg_pin_nuevo_0=True)
    md = " ".join(str(m.value) for m in at.markdown)
    assert "Punto fijado" in md and "huellas-pinok" in md
    assert at.session_state.get("reg_pin_nuevo_0") is True
