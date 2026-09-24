"""Panel lateral: auto-apertura al cambiar de pestaña (REQ-UI-02 v1.10).

A nivel de fuente (sin importar Streamlit): el snippet expansor debe pulsar el
control de apertura y dispararse solo cuando cambia `page`; la navegación solo
reabre FUNCIONALIDADES (revert de S70).
"""
from pathlib import Path

SRC = Path("app.py").read_text(encoding="utf-8")


def test_expand_snippet_pulsa_control_colapsado():
    assert "stSidebarCollapsedControl" in SRC
    assert ".click()" in SRC
    assert "_side_prev_page" in SRC  # solo actúa al cambiar de pestaña


def test_solo_funcionalidades_reabre_al_navegar():
    assert 'st.session_state["side_func"] = True' in SRC
    # Sin reapertura general de secciones (S70 revertido):
    assert '("side_func", "side_punt", "side_demo", "side_mas", "side_admin")' not in SRC
