"""Tests Reencuentros — CU-05 cierre de caso con validación del admin."""
from agents import db as dbmod


def _con(tmp_path):
    return dbmod.connect(str(tmp_path / "t.db"))


def test_guardar_queda_pendiente(tmp_path):
    con = _con(tmp_path)
    rid = dbmod.save_reencuentro(con, ["lost_001", "found_011"], ["f1.jpg"], "Volvió solo")
    rows = dbmod.list_reencuentros(con)
    assert len(rows) == 1
    assert rows[0]["id"] == rid
    assert rows[0]["estado"] == "pendiente"
    assert rows[0]["aviso_ids"] == ["lost_001", "found_011"]
    assert rows[0]["fotos"] == ["f1.jpg"]


def test_validar_y_resolver(tmp_path):
    con = _con(tmp_path)
    rid = dbmod.save_reencuentro(con, ["lost_001"], [], "")
    dbmod.set_reencuentro(con, rid, "validada")
    assert dbmod.list_reencuentros(con, "validada")[0]["id"] == rid
    assert dbmod.list_reencuentros(con, "pendiente") == []


def test_rechazar_no_toca_avisos(tmp_path):
    con = _con(tmp_path)
    rid = dbmod.save_reencuentro(con, ["lost_001"], [], "")
    dbmod.set_reencuentro(con, rid, "rechazada")
    assert dbmod.list_reencuentros(con, "rechazada")[0]["id"] == rid
