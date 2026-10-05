"""Tests seed reencuentros + renombre siamesa a lost_006."""
import json
from pathlib import Path

from agents import db as dbmod
from agents.ingestor import normalize_aviso

SEED = Path("data/seed")

ESPERADOS = {
    "renc_006": (["lost_006"], "validada",
                 "data/seed/images/demo reencuentros/reencuentro_cerrado_006.png"),
    "renc_012": (["found_012"], "pendiente",
                 "data/seed/images/demo reencuentros/reencuentro_en_revision_012.jpg"),
    "renc_013": (["found_013"], "pendiente",
                 "data/seed/images/demo reencuentros/reencuentro_en_revision_013.jpg"),
}


def _avisos_ids():
    ids = set()
    for folder in ("lost", "found"):
        for fp in (SEED / folder).glob("*.json"):
            ids.add(json.loads(fp.read_text(encoding="utf-8"))["id"])
    return ids


def test_casos_esperados_con_forma_valida():
    fps = sorted((SEED / "reencuentros").glob("*.json"))
    assert {f.stem for f in fps} == set(ESPERADOS), [f.name for f in fps]
    validos = {aid for avisos, _, _ in ESPERADOS.values() for aid in avisos}
    for fp in fps:
        d = json.loads(fp.read_text(encoding="utf-8"))
        assert d["id"] == fp.stem
        assert d["estado"] == ESPERADOS[d["id"]][1], d["id"]
        assert d["aviso_ids"] and set(d["aviso_ids"]) <= validos, d["aviso_ids"]
        assert str(d.get("nota") or "").strip(), f"{d['id']} sin nota"
        assert str(d.get("created_at") or "").strip(), f"{d['id']} sin fecha"


def test_notas_en_revision_con_voz_del_dueno():
    # Las fotos de prueba las tomaron los dueños ya en casa: la nota lo
    # cuenta en primera persona (no como quien avistó en la calle).
    n12 = json.loads((SEED / "reencuentros" / "renc_012.json").read_text(encoding="utf-8"))["nota"]
    assert "ya está en casa" in n12 and "plantas" in n12
    n13 = json.loads((SEED / "reencuentros" / "renc_013.json").read_text(encoding="utf-8"))["nota"]
    assert "cinta roja" in n13 and "quien lo encontró" not in n13


def test_casos_enlazan_avisos_y_fotos_reales():
    ids = _avisos_ids()
    for rid, (aviso_ids, _, foto) in ESPERADOS.items():
        d = json.loads((SEED / "reencuentros" / f"{rid}.json").read_text(encoding="utf-8"))
        assert list(d["aviso_ids"]) == aviso_ids, rid
        for aid in d["aviso_ids"]:
            assert aid in ids, f"{rid} enlaza aviso inexistente {aid}"
        assert list(d["fotos"]) == [foto], rid
        assert Path(foto).exists(), f"{rid}: falta {foto}"


def test_upsert_seed_no_toca_casos_de_usuarios():
    con = dbmod.connect(":memory:")
    for fp in sorted((SEED / "reencuentros").glob("*.json")):
        dbmod.upsert_reencuentro_seed(con, json.loads(fp.read_text(encoding="utf-8")))
    rid = dbmod.save_reencuentro(con, ["lost_001"], ["f1.jpg"], "caso de usuario")
    for fp in sorted((SEED / "reencuentros").glob("*.json")):
        dbmod.upsert_reencuentro_seed(con, json.loads(fp.read_text(encoding="utf-8")))
    rows = {r["id"]: r for r in dbmod.list_reencuentros(con)}
    assert len(rows) == 4, sorted(rows)
    assert rows[rid]["nota"] == "caso de usuario"
    assert rows["renc_006"]["estado"] == "validada"
    assert rows["renc_012"]["estado"] == "pendiente"
    assert rows["renc_013"]["estado"] == "pendiente"


def _aviso_min(aid, tipo):
    return normalize_aviso({"id": aid, "type": tipo, "animal": "dog",
                            "color_primary": "marrón", "size": "medium",
                            "description_text": "prueba",
                            "location": {"lat": 36.6, "lng": -6.1, "address_text": "X"},
                            "date_reported": "2026-09-01T12:00:00+02:00",
                            "image_url": "data/seed/images/gato 3.jpg",
                            "contact_info": "600 000 000", "status": "active"})


def test_resolver_casos_validados_oculta_cerrados():
    # El cerrado se oculta de su pestaña; los en revisión siguen activos.
    con = dbmod.connect(":memory:")
    for aid, tipo in (("lost_006", "lost"), ("found_012", "found"), ("found_013", "found")):
        dbmod.upsert_aviso(con, _aviso_min(aid, tipo))
    for fp in sorted((SEED / "reencuentros").glob("*.json")):
        dbmod.upsert_reencuentro_seed(con, json.loads(fp.read_text(encoding="utf-8")))
    assert dbmod.resolver_casos_validados(con) == 1
    assert dbmod.get_aviso(con, "lost_006")["status"] == "resolved"
    assert dbmod.get_aviso(con, "found_012")["status"] == "active"
    assert dbmod.get_aviso(con, "found_013")["status"] == "active"
    assert {a["id"] for a in dbmod.get_active_opuestos(con, "lost")} == {"found_012", "found_013"}
    assert dbmod.get_active_opuestos(con, "found") == []


def test_siamesa_es_lost_006_y_no_existe_lost_007():
    assert not (SEED / "lost" / "lost_007.json").exists(), "lost_007 ha resucitado"
    assert not Path("data/seed/images/lost_007.jpg").exists(), "foto lost_007 ha resucitado"
    d = json.loads((SEED / "lost" / "lost_006.json").read_text(encoding="utf-8"))
    assert d["breed_guess"] == "siamés", d["breed_guess"]
    assert d["image_url"] == "data/seed/images/lost_006.jpg", d["image_url"]
    assert Path(d["image_url"]).exists()
    gen = Path("scripts/make_seed.py").read_text(encoding="utf-8")
    assert "lost_007" not in gen, "make_seed.py aún menciona lost_007"
    pre = json.load(open(SEED / "embeddings.json", encoding="utf-8"))
    assert "lost_006" in pre and "lost_007" not in pre
