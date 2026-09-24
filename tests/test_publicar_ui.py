"""Tests tanda Publicar con vida — REQ-UI-13..16 (solo UI, sin BD)."""
from ui_home import (
    build_check_html,
    build_crossing_html,
    build_match_card_html,
    faltantes_publicar,
)


def test_faltantes_todo_vacio():
    f = faltantes_publicar("", "", "", "", "", "")
    assert f == ["tipo de aviso", "animal", "tamaño",
                 "contacto (móvil, correo o red social)"]


def test_faltantes_completo_sin_falta():
    assert faltantes_publicar("lost", "dog", "small", "610 204 518", "", "") == []
    assert faltantes_publicar("found", "cat", "large", "", "a@x.es", "") == []


def test_faltantes_solo_contacto():
    f = faltantes_publicar("lost", "dog", "small", "", "", "")
    assert f == ["contacto (móvil, correo o red social)"]


def test_match_card_con_porcentaje_y_sin_contacto():
    out = build_match_card_html("found_011", 0.843)
    assert "found_011" in out
    assert "84 %" in out
    assert "huellas-match-card" in out and "huellas-ring-fg" in out
    assert "huellas-ringfill-84" in out and "steps(84)" in out
    assert "stroke-dashoffset:16" in out  # 100 - 84
    assert "<span>0</span>" in out and "<span>84</span>" in out
    assert "huellas-track" in out
    assert "contact" not in out.lower()


def test_match_card_clampea_score():
    assert "huellas-ringfill-100" in build_match_card_html("x", 1.9)
    out0 = build_match_card_html("x", -0.2)
    assert "0 %" in out0 and "steps(" not in out0


def test_crossing_con_n_sin_contacto():
    out = build_crossing_html(11)
    assert "11 aviso" in out and "huellas-dots" in out
    assert "contact" not in out.lower()


def test_check_sin_contacto():
    out = build_check_html()
    assert "huellas-okcheck" in out and "<svg" in out
    assert "contact" not in out.lower()
