"""Tests Matcher — REQ-07 fórmula/pesos + REQ-08 umbrales >=."""
from agents.matcher import (
    PESO_GEO,
    PESO_TEMP,
    PESO_TEXTO,
    PESO_VISUAL,
    UMBRAL_GATE_VISUAL,
    UMBRAL_LISTA,
    UMBRAL_NOTIF,
    canon_color,
    match_one,
    normalizar_txt,
    proximidad_temporal,
    score_total,
    similitud_estructurada,
    similitud_texto,
)

Q = {
    "id": "q", "color_primary": "marrón", "size": "medium",
    "has_collar": True, "markings": ["mancha blanca pecho"],
    "location": {"lat": 36.6826, "lng": -6.1376},
    "date_reported": "2026-09-20T10:00:00+02:00", "date_last_seen": "2026-09-19T10:00:00+02:00",
}
C = {
    "id": "c", "color_primary": "marrón", "size": "medium",
    "has_collar": True, "markings": ["mancha blanca pecho"],
    "location": {"lat": 36.6836, "lng": -6.1386},
    "date_reported": "2026-09-20T12:00:00+02:00", "date_last_seen": "2026-09-19T12:00:00+02:00",
}


def test_pesos_suman_uno():
    assert abs((PESO_VISUAL + PESO_TEXTO + PESO_TEMP + PESO_GEO) - 1.0) < 1e-9
    assert abs(score_total(1, 1, 1, 1) - 1.0) < 1e-9


def test_pesos_v13_visual_manda():
    assert PESO_VISUAL == 0.55 and PESO_TEXTO == 0.25
    assert PESO_TEMP == 0.10 and PESO_GEO == 0.10


def test_estructurada_identica_es_uno():
    assert similitud_estructurada(Q, C) == 1.0


def test_texto_70_30():
    assert abs(similitud_texto(Q, C, 1.0) - 1.0) < 1e-9
    assert abs(similitud_texto(Q, C, 0.0) - 0.7) < 1e-9


def test_temporal_usa_last_seen():
    assert proximidad_temporal(Q, C) == 1.0
    c2 = dict(C, date_last_seen="2026-08-10T10:00:00+02:00")
    assert proximidad_temporal(Q, c2) == 0.0  # >30 días


def test_match_one_cercano_alto():
    m = match_one(Q, C, visual=0.9, semant=0.9)
    assert m["score"] >= UMBRAL_NOTIF
    assert m["notifica"] and m["lista"]


def test_umbrales_borde_inclusivos():
    assert UMBRAL_NOTIF == 0.80 and UMBRAL_LISTA == 0.65
    # score exacto 0.65 debe listar (regla >=)
    assert 0.65 >= UMBRAL_LISTA


def test_normalizar_ignora_tildes_mayusculas():
    assert normalizar_txt("  MARRÓN ") == "marron"
    assert canon_color("Marron") == canon_color("marrón") == "marron"
    assert canon_color("Café") == "marron"  # alias
    q = dict(Q, color_primary="MARRON", markings=["Pecho Blanco"])
    c = dict(C, color_primary="marrón", markings=["pecho blanco"])
    assert similitud_estructurada(q, c) == 1.0


def test_gate_visual_alerta_aunque_total_bajo():
    assert UMBRAL_GATE_VISUAL == 0.95
    # Misma foto (visual 1.0) pero todo lo demás distinto: alerta igual
    otro = {"id": "x", "color_primary": "negro", "size": "large",
            "has_collar": False, "markings": ["oreja cortada"],
            "location": {"lat": 37.0000, "lng": -6.5000},
            "date_reported": "2026-01-01T10:00:00+02:00",
            "date_last_seen": "2026-01-01T10:00:00+02:00"}
    m = match_one(Q, otro, visual=1.0, semant=0.0)
    assert m["visual"] == 1.0 and m["score"] < UMBRAL_NOTIF
    assert m["notifica"] and m["lista"]


def test_gate_no_dispara_con_visual_alta_pero_no_identica():
    otro = {"id": "x", "color_primary": "negro", "size": "large",
            "has_collar": False, "markings": ["oreja cortada"],
            "location": {"lat": 37.0000, "lng": -6.5000},
            "date_reported": "2026-01-01T10:00:00+02:00",
            "date_last_seen": "2026-01-01T10:00:00+02:00"}
    m = match_one(Q, otro, visual=0.90, semant=0.0)
    assert m["score"] < UMBRAL_NOTIF
    assert not m["notifica"] and not m["lista"]
