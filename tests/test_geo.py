"""Tests Geo — REQ-07 (radio 15 km)."""
from agents.geo import RADIO_MAX_KM, haversine_km, proximidad_geografica


def test_radio_fijo_15():
    assert RADIO_MAX_KM == 15.0


def test_haversine_jerez_centro_chapin():
    # Plaza del Arenal (36.6826,-6.1376) → Chapín (36.6905,-6.1479): ~1.2-1.4 km
    d = haversine_km(36.6826, -6.1376, 36.6905, -6.1479)
    assert 0.8 < d < 2.0


def test_proximidad_bordes():
    assert proximidad_geografica(0) == 1.0
    assert proximidad_geografica(7.5) == 0.5
    assert proximidad_geografica(15) == 0.0
    assert proximidad_geografica(30) == 0.0
