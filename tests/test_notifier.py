"""Tests Notifier — REQ-08 sin duplicados."""
from agents import db as dbmod
from agents.notifier import notificar


def _con(tmp_path):
    return dbmod.connect(str(tmp_path / "t.db"))


def _m(cid, score):
    return {"candidato_id": cid, "score": score}


def test_primera_vez_registra(tmp_path):
    con = _con(tmp_path)
    log = str(tmp_path / "n.log")
    assert len(notificar(con, "q", [_m("c1", 0.9)], log_path=log)) == 1
    assert len(open(log, encoding="utf-8").readlines()) == 1


def test_duplicado_identico_se_ignora(tmp_path):
    con = _con(tmp_path)
    log = str(tmp_path / "n.log")
    notificar(con, "q", [_m("c1", 0.9)], log_path=log)
    assert notificar(con, "q", [_m("c1", 0.9)], log_path=log) == []
    assert con.execute("SELECT COUNT(*) FROM notifications").fetchone()[0] == 1
    assert len(open(log, encoding="utf-8").readlines()) == 1


def test_score_distinto_actualiza(tmp_path):
    con = _con(tmp_path)
    log = str(tmp_path / "n.log")
    notificar(con, "q", [_m("c1", 0.9)], log_path=log)
    assert len(notificar(con, "q", [_m("c1", 0.95)], log_path=log)) == 1
    row = con.execute("SELECT score FROM notifications").fetchone()
    assert abs(row["score"] - 0.95) < 1e-9


def test_bajo_umbral_no_registra(tmp_path):
    con = _con(tmp_path)
    assert notificar(con, "q", [_m("c1", 0.5)], log_path=str(tmp_path / "n.log")) == []
