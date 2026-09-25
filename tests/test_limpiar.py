"""Regresión: Empezar de cero limpia selects+texto y ROTA el uploader.

El file_uploader ignora el borrado de su clave (quirk Streamlit): solo se
vacía cambiando la clave. El test fija valores, pulsa limpiar y verifica.
"""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path("app.py").resolve())


def _ir_reencuentro():
    at = AppTest.from_file(APP)
    at.session_state["page"] = "reencuentro"
    at.run(timeout=60)
    assert not at.exception, at.exception
    return at


def test_limpiar_vacia_formulario_y_rota_uploader():
    at = _ir_reencuentro()
    assert [f.key for f in at.file_uploader] == ["re_fotos_0"]
    at.multiselect(key="re_lost").set_value(["lost_001"])
    at.text_area(key="re_nota").set_value("THTHTHT")
    at.run(timeout=60)
    assert at.multiselect(key="re_lost").value == ["lost_001"]
    at.button(key="re_limpiar").click()
    at.run(timeout=60)
    assert not at.exception, at.exception
    assert at.multiselect(key="re_lost").value in (None, [])
    assert (at.text_area(key="re_nota").value or "") == ""
    assert [f.key for f in at.file_uploader] == ["re_fotos_1"]
