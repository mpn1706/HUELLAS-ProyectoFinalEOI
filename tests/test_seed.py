"""Tests seed demo — v1.4: todo aviso seed trae dato de contacto (REQ-09.5, CU-01/02)."""
import json
from pathlib import Path

SEED = Path("data/seed")


def _seeds():
    return sorted(SEED.glob("lost/*.json")) + sorted(SEED.glob("found/*.json"))


def test_todo_seed_con_contacto():
    fps = _seeds()
    assert fps, "sin ficheros seed"
    sin = []
    for fp in fps:
        d = json.loads(fp.read_text(encoding="utf-8"))
        if not str(d.get("contact_info") or "").strip():
            sin.append(fp.name)
    assert not sin, f"seed sin contacto: {sin}"


def test_contactos_con_formato_valido():
    for fp in _seeds():
        d = json.loads(fp.read_text(encoding="utf-8"))
        c = str(d.get("contact_info") or "").strip()
        assert c, fp.name
        assert "@" in c or any(ch.isdigit() for ch in c), f"{fp.name}: {c!r}"


CANONICOS_LOST = {
    "lost_001": "data/seed/images/lost_001.jpg",
    "lost_002": "data/seed/images/lost_002.png",
    "lost_003": "data/seed/images/lost_003.jpg",
    "lost_004": "data/seed/images/lost_004.jpg",
    "lost_005": "data/seed/images/lost_005.jpg",
}


def test_lost_usan_fotos_canonicas():
    """Los lost_001..005 apuntan a las fotos de 'losts changes'.

    Regresión: make_seed.py es la única fuente de verdad; si alguien
    regenera el seed, estas 5 fotos deben sobrevivir (Cloud incluido).
    """
    for aid, img in CANONICOS_LOST.items():
        d = json.loads((SEED / "lost" / f"{aid}.json").read_text(encoding="utf-8"))
        assert d["image_url"] == img, f"{aid}: {d['image_url']!r} != {img!r}"
        assert (Path(img).exists()), f"{aid}: falta {img}"
    gen = Path("scripts/make_seed.py").read_text(encoding="utf-8")
    for img in CANONICOS_LOST.values():
        nombre = img.rsplit("/", 1)[-1]
        assert nombre in gen, f"make_seed.py ya no referencia {nombre}"
    for vieja in ("gato 1.jpg", "perrete 4.jpg", "perrete 3.jpg",
                  "gato 4.jpg", "perrete 12.jpg"):
        assert vieja not in gen, f"make_seed.py reintroduce foto antigua {vieja}"


def test_gatito_gris_es_avistamiento():
    """El gatito gris (volvió a casa) no es un perdido activo: es found_014.

    Regresión: si alguien regenera el seed, el gris no debe volver a perdidos
    (el lost_006 actual es la siamesa renombrada desde lost_007).
    """
    grises = [fp.name for fp in (SEED / "lost").glob("*.json")
              if json.loads(fp.read_text(encoding="utf-8"))["image_url"]
              == "data/seed/images/gato 3.jpg"]
    assert not grises, f"el gris volvió a perdidos: {grises}"
    d = json.loads((SEED / "found" / "found_014.json").read_text(encoding="utf-8"))
    assert d["type"] == "found", d["type"]
    assert d["image_url"] == "data/seed/images/gato 3.jpg", d["image_url"]
    assert d["date_last_seen"] is None
    assert str(d.get("contact_info") or "").strip(), "found_014 sin contacto"
    gen = Path("scripts/make_seed.py").read_text(encoding="utf-8")
    assert "Apareció al día siguiente en casa" not in gen
