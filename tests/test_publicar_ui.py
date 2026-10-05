"""Tests tanda Publicar con vida — REQ-UI-13..16 (solo UI, sin BD)."""
from datetime import date

from ui_home import (
    build_check_html,
    build_crossing_html,
    build_match_card_html,
    build_pen_html,
    faltantes_publicar,
    fechas_publicar,
)


def test_faltantes_todo_vacio():
    f = faltantes_publicar()
    assert f == ["tipo de aviso", "animal", "tamaño", "color principal",
                 "descripción", "contacto (móvil, correo o red social)"]


def test_faltantes_completo_sin_falta():
    assert faltantes_publicar("lost", "dog", "small", "marrón", "perro noble",
                              "610 204 518", "", "") == []
    assert faltantes_publicar("found", "cat", "large", "negro", "gata tranquila",
                              "", "a@x.es", "") == []


def test_faltantes_solo_contacto():
    f = faltantes_publicar("lost", "dog", "small", "marrón", "perro noble",
                           "", "", "")
    assert f == ["contacto (móvil, correo o red social)"]


def test_faltantes_color_y_desc():
    f = faltantes_publicar("lost", "dog", "small", "", "", "610", "", "")
    assert "color principal" in f and "descripción" in f


def test_fechas_lost_hoy_y_elegida():
    rep, seen = fechas_publicar("lost", date(2026, 9, 20), date(2026, 10, 5))
    assert rep == "2026-10-05T12:00:00+02:00"  # día de publicación
    assert seen == "2026-09-20T18:00:00+02:00"  # fecha elegida de pérdida


def test_fechas_found_usa_elegida():
    rep, seen = fechas_publicar("found", date(2026, 9, 28), date(2026, 10, 5))
    assert rep == "2026-09-28T12:00:00+02:00"  # fecha elegida de avistamiento
    assert seen is None


def test_fechas_futura_o_vacia_a_hoy():
    hoy = date(2026, 10, 5)
    assert fechas_publicar("lost", date(2026, 10, 9), hoy)[1] == "2026-10-05T18:00:00+02:00"
    assert fechas_publicar("found", None, hoy)[0] == "2026-10-05T12:00:00+02:00"


def test_fmt_corta():
    from datetime import datetime
    from ui_home import fmt_corta
    assert fmt_corta(datetime(2026, 9, 25, 10, 0)) == "25/09/26"
    assert fmt_corta("2026-08-25T12:00:00+02:00") == "25/08/26"
    assert fmt_corta(None) == "—"


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


def test_pen_sin_contacto():
    out = build_pen_html()
    assert "huellas-penwrap" in out and "huellas-trazo" in out
    assert "huellas-boli" in out and "<svg" in out
    assert "contact" not in out.lower()
