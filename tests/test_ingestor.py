"""Tests Ingestor — REQ-05 (other, fechas, UUID, texto intacto)."""
import pytest

from agents.ingestor import effective_date, normalize_aviso


def base():
    return {
        "type": "lost", "animal": "dog", "color_primary": " Negro ",
        "size": "medium", "has_collar": False,
        "description_text": "  PERRO Negro con Mancha Blanca  ",
        "location": {"lat": 36.6826, "lng": -6.1376},
        "date_reported": "2026-09-20T10:00:00+02:00",
        "image_url": "data/seed/images/x.jpg",
    }


def test_normaliza_y_genera_uuid():
    d = normalize_aviso(base())
    assert d["id"] and d["status"] == "active"
    assert d["color_primary"] == "negro"  # estructurado normalizado
    assert d["description_text"] == "PERRO Negro con Mancha Blanca"  # intacto salvo strip


def test_other_exige_campos_y_anula_breed():
    d = base()
    d.update({"animal": "other", "breed_guess": "pastor", "color_primary": "verde", "size": "small"})
    n = normalize_aviso(d)
    assert n["breed_guess"] is None


def test_other_sin_descripcion_falla():
    d = base()
    d.update({"animal": "other", "description_text": ""})
    with pytest.raises(ValueError):
        normalize_aviso(d)


def test_effective_date_prioriza_last_seen():
    d = base()
    d["date_last_seen"] = "2026-09-19T10:00:00+02:00"
    assert effective_date(d).day == 19
    del d["date_last_seen"]
    assert effective_date(d).day == 20
