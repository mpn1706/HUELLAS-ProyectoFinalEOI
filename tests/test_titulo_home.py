"""Títulos con botón rojo ⏪ a Inicio (S111) + aire por viewport (S118)."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path("app.py").resolve())
SRC = Path("app.py").read_text(encoding="utf-8")
PAGES = ["buscar", "publicar", "perdidos", "encontrados", "reencuentro"]


def _ir(pagina):
    at = AppTest.from_file(APP)
    at.session_state["page"] = pagina
    at.run(timeout=120)
    assert not at.exception, (pagina, at.exception)
    return at


def _home_keys(at):
    return [b.key for b in at.button
            if (b.key or "").startswith(("home_", "homebox_"))]


def test_titulos_llevan_boton_inicio():
    for page in PAGES:
        at = _ir(page)
        assert len(_home_keys(at)) == 1, page


def test_caja_lleva_clave_propia_con_extra():
    at = _ir("perdidos")  # viñeta en caja
    assert any(k.startswith("homebox_") for k in _home_keys(at))
    at = _ir("publicar")  # barrido normal
    assert any(k.startswith("home_") and not k.startswith("homebox_")
               for k in _home_keys(at))
    assert "st-key-homebox_" in SRC  # 1px extra abajo solo en caja
    assert "top:4px" in SRC  # desplazamiento exacto (el padding se recentra)


def test_boton_inicio_navega():
    at = _ir("publicar")
    key = _home_keys(at)[0]
    at.button(key=key).click()
    at.run(timeout=120)
    assert not at.exception, at.exception
    assert at.session_state["page"] == "inicio"


def test_aire_titulo_solo_segun_viewport():
    # Móvil (≤640px): fila forzada + columna ajustada; escritorio (≥641px):
    # hueco estrecho 0.5rem. Ninguna regla pisa a la otra.
    assert "@media (max-width:640px)" in SRC
    assert "@media (min-width:641px)" in SRC
    i_mob = SRC.index("@media (max-width:640px)")
    i_desk = SRC.index("@media (min-width:641px)")
    assert "column-gap:0.5rem" in SRC[i_desk:]
    assert "column-gap" not in SRC[i_mob:SRC.index("@media (min-width:641px)")]
