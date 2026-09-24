"""Sidebar: comportamiento al navegar (REQ-UI-02 v1.11).

El intento de auto-apertura del PANEL (v1.10) se abandonó: sin API en
Streamlit para desplegar el sidebar y los trucos (iframe custom component,
st.html con JS) quedan bloqueados. La navegación reabre solo FUNCIONALIDADES.
"""
from pathlib import Path

SRC = Path("app.py").read_text(encoding="utf-8")


def test_solo_funcionalidades_reabre_al_navegar():
    assert 'st.session_state["side_func"] = True' in SRC
    # Sin reapertura general de secciones (S70 revertido):
    assert '("side_func", "side_punt", "side_demo", "side_mas", "side_admin")' not in SRC


def test_sin_experimentos_de_panel():
    assert "stExpandSidebarButton" not in SRC  # expansor JS abandonado (v1.11)
    assert "_side_prev_page" not in SRC
