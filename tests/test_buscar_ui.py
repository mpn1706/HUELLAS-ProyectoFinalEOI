"""Tests Buscar con vida + Perdidos/Avistamientos — REQ-UI-26..35 (solo UI)."""
from datetime import date, datetime, timedelta, timezone

from ui_home import (
    build_bars_html,
    build_foto_scan_html,
    build_radar_html,
    build_result_card_html,
    chip_dias_perdido,
    chip_visto,
    contacto_details_html,
    dias_perdido,
    es_nuevo,
    faltantes_buscar,
    nuevo_html,
)


def test_faltantes_buscar_vacio_y_completo():
    assert faltantes_buscar() == ["canal", "foto", "animal", "tamaño",
                                  "color principal", "descripción"]
    assert faltantes_buscar("found", True, "dog", "small", "marrón", "noble") == []


def test_dias_y_nuevo():
    hoy = date(2026, 9, 25)
    assert dias_perdido("2026-09-23T10:00:00+02:00", None, hoy) == 2
    assert dias_perdido(None, "2026-09-25T10:00:00+02:00", hoy) == 0
    assert dias_perdido(None, None, hoy) == 0
    ahora = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)
    assert es_nuevo((ahora - timedelta(hours=10)).isoformat(), None, ahora)
    assert not es_nuevo((ahora - timedelta(hours=60)).isoformat(), None, ahora)
    assert not es_nuevo(None, None, ahora)


def test_chips_urgencia_y_visto():
    assert 'verde' in chip_dias_perdido(1) and '1 día perdido' in chip_dias_perdido(1)
    assert 'ambar' in chip_dias_perdido(4)
    assert 'rojo' in chip_dias_perdido(9)
    assert 'Perdido hoy' in chip_dias_perdido(0)
    assert 'neutro' in chip_visto(5) and 'Visto hace 5 días' in chip_visto(5)
    assert 'Nuevo' in nuevo_html() and 'huellas-dot' in nuevo_html()


def test_result_card_cascada_top_y_badge():
    out = build_result_card_html("found_011", 0.843, 0.09,
                                 "POSIBLE COINCIDENCIA DESTACADA", 2, top=True)
    assert "animation-delay:0.16s" in out  # 2 × 80 ms
    assert "huellas-res-top" in out and "POSIBLE COINCIDENCIA" in out
    assert "found_011" in out and "0.09 km" in out
    assert "contact" not in out.lower()


def test_bars_cuatro_y_valores():
    out = build_bars_html("found_011", 0.71, 0.99, 0.89, 0.97)
    for et in ("Visual", "Zona", "Texto", "Fecha"):
        assert et in out
    assert "width:71%" in out and "width:99%" in out
    assert out.count("huellas-barfill") == 4


def test_contacto_details_escapado_y_alternancia():
    out = contacto_details_html("610 204 518")
    assert "610 204 518" in out and "<details" in out and "<summary>" in out
    assert "Ver contacto" in out and "Ocultar contacto" in out
    assert "&lt;b&gt;x&lt;/b&gt;" in contacto_details_html("<b>x</b>")
    assert "Sin contacto registrado" in contacto_details_html("")
    assert "610" not in contacto_details_html("")


def test_radar_y_scan():
    r = build_radar_html()
    assert "huellas-radar" in r and "huellas-ping" in r
    s = build_foto_scan_html("data:image/jpeg;base64,AAA", "mi foto",
                             "Foto lista", esquinas=True)
    assert "huellas-scanline" in s and "Foto lista" in s
    assert "huellas-flash" in s
    assert s.count('<i class="c') == 4
    s2 = build_foto_scan_html("data:image/jpeg;base64,AAA")
    assert '<i class="c' not in s2 and "huellas-analizada" not in s2
    assert "huellas-flash" in s2
