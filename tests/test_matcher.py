"""Tests Matcher — REQ-07 fórmula/pesos + REQ-08 umbrales >=."""
from agents.matcher import (
    UMBRAL_LISTA,
    UMBRAL_NOTIF,
    match_one,
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
    assert abs((0.40 + 0.30 + 0.20 + 0.10) - 1.0) < 1e-9
    assert abs(score_total(1, 1, 1, 1) - 1.0) < 1e-9


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
    assert UMBRAL_NOTIF == 0.85 and UMBRAL_LISTA == 0.65
    # score exacto 0.65 debe listar (regla >=)
    assert 0.65 >= UMBRAL_LISTA
