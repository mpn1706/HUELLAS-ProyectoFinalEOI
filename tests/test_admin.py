"""Tests Admin — REQ-11 (auth, borrado, listado)."""
import sqlite3

import pytest

from agents import admin as adm
from agents import db as dbmod


@pytest.fixture()
def con(tmp_path):
    c = dbmod.connect(str(tmp_path / "t.db"))
    for i in ("a1", "a2"):
        dbmod.upsert_aviso(c, {
            "id": i, "type": "lost", "animal": "dog", "breed_guess": "x",
            "color_primary": "marrón", "color_secondary": None, "markings": [],
            "size": "medium", "has_collar": False, "collar_description": None,
            "description_text": "perro marrón", "location": {"lat": 1.0, "lng": 2.0, "address_text": ""},
            "date_reported": "2026-09-20T10:00:00+02:00", "date_last_seen": None,
            "image_url": "data/seed/images/x.jpg", "image_embedding": None,
            "contact_info": "", "status": "active"})
    return c


def test_password():
    assert adm.check_password("huellas123", "huellas123")
    assert not adm.check_password("nope", "huellas123")
    assert not adm.check_password("", "huellas123")


def test_list_filtra(con):
    assert len(adm.list_avisos(con)) == 2
    assert len(adm.list_avisos(con, texto="marrón")) == 2
    assert len(adm.list_avisos(con, texto="verde")) == 0
    assert len(adm.list_avisos(con, tipo="found")) == 0


def test_delete_borra_y_registra(con, tmp_path):
    log = str(tmp_path / "admin.log")
    assert adm.delete_aviso(con, "a1", log_path=log)
    assert dbmod.get_aviso(con, "a1") is None
    assert len(adm.list_avisos(con)) == 1
    assert "DELETE a1" in open(log, encoding="utf-8").read()
    assert not adm.delete_aviso(con, "inexistente", log_path=log)


def test_resolve(con, tmp_path):
    adm.resolve_aviso(con, "a2", log_path=str(tmp_path / "admin.log"))
    assert dbmod.get_aviso(con, "a2")["status"] == "resolved"
    assert len(adm.list_avisos(con)) == 2  # sigue listado (filtro por defecto no excluye)
