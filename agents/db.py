"""Persistencia SQLite — espejo 1:1 del esquema REQ-05."""
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# Versión del seed: al subir, la app recarga sola (Cloud conserva la DB entre despliegues).
SEED_VERSION = 4

SCHEMA = """
CREATE TABLE IF NOT EXISTS avisos (
  id TEXT PRIMARY KEY,
  type TEXT CHECK(type IN ('lost','found')),
  animal TEXT,
  breed_guess TEXT,
  color_primary TEXT,
  color_secondary TEXT,
  markings JSON,
  size TEXT,
  has_collar INTEGER,
  collar_description TEXT,
  description_text TEXT,
  lat REAL, lng REAL, address_text TEXT,
  date_reported TEXT, date_last_seen TEXT,
  image_url TEXT, image_embedding JSON,
  contact_info TEXT, status TEXT
);
CREATE INDEX IF NOT EXISTS idx_avisos_status_type ON avisos(status, type);
CREATE TABLE IF NOT EXISTS notifications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  aviso_id TEXT, candidato_id TEXT, score REAL, created_at TEXT
);
"""

COLS = ["id", "type", "animal", "breed_guess", "color_primary", "color_secondary",
        "markings", "size", "has_collar", "collar_description", "description_text",
        "lat", "lng", "address_text", "date_reported", "date_last_seen",
        "image_url", "image_embedding", "contact_info", "status"]


def get_seed_version(con: sqlite3.Connection) -> int:
    return con.execute("PRAGMA user_version").fetchone()[0]


def set_seed_version(con: sqlite3.Connection, v: int = SEED_VERSION):
    con.execute(f"PRAGMA user_version={int(v)}")
    con.commit()


def wipe_all(con: sqlite3.Connection):
    con.execute("DELETE FROM notifications")
    con.execute("DELETE FROM avisos")
    con.commit()


def connect(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def _to_row(d: dict) -> tuple:
    loc = d.get("location") or {}
    return (
        d["id"], d["type"], d.get("animal"), d.get("breed_guess"),
        d.get("color_primary"), d.get("color_secondary"),
        json.dumps(d.get("markings") or []), d.get("size"),
        1 if d.get("has_collar") else 0, d.get("collar_description"),
        d.get("description_text"), float(loc.get("lat")), float(loc.get("lng")),
        loc.get("address_text"), d.get("date_reported"), d.get("date_last_seen"),
        d.get("image_url"),
        json.dumps(d["image_embedding"]) if d.get("image_embedding") else None,
        d.get("contact_info"), d.get("status", "active"),
    )


def _from_row(r: sqlite3.Row) -> dict:
    d = dict(r)
    return {
        "id": d["id"], "type": d["type"], "animal": d["animal"],
        "breed_guess": d["breed_guess"], "color_primary": d["color_primary"],
        "color_secondary": d["color_secondary"],
        "markings": json.loads(d["markings"] or "[]"), "size": d["size"],
        "has_collar": bool(d["has_collar"]), "collar_description": d["collar_description"],
        "description_text": d["description_text"],
        "location": {"lat": d["lat"], "lng": d["lng"], "address_text": d["address_text"]},
        "date_reported": d["date_reported"], "date_last_seen": d["date_last_seen"],
        "image_url": d["image_url"],
        "image_embedding": json.loads(d["image_embedding"]) if d["image_embedding"] else None,
        "contact_info": d["contact_info"], "status": d["status"],
    }


def upsert_aviso(con: sqlite3.Connection, d: dict):
    con.execute(
        f"INSERT OR REPLACE INTO avisos ({','.join(COLS)}) VALUES ({','.join('?'*len(COLS))})",
        _to_row(d),
    )
    con.commit()


def get_aviso(con: sqlite3.Connection, aviso_id: str):
    r = con.execute("SELECT * FROM avisos WHERE id=?", (aviso_id,)).fetchone()
    return _from_row(r) if r else None


def get_active_opuestos(con: sqlite3.Connection, tipo: str) -> list:
    op = "found" if tipo == "lost" else "lost"
    rows = con.execute(
        "SELECT * FROM avisos WHERE status='active' AND type=?", (op,)
    ).fetchall()
    return [_from_row(r) for r in rows]


def set_resolved(con: sqlite3.Connection, aviso_id: str):
    con.execute("UPDATE avisos SET status='resolved' WHERE id=?", (aviso_id,))
    con.commit()


def expire_old(con: sqlite3.Connection, dias: int = 30) -> int:
    """Marca expired si date_reported < hoy-dias. Retorna nº afectados."""
    corte = (datetime.now().astimezone() - timedelta(days=dias)).isoformat()
    cur = con.execute(
        "UPDATE avisos SET status='expired' WHERE status='active' AND date_reported < ?",
        (corte,),
    )
    con.commit()
    return cur.rowcount


def save_notification(con: sqlite3.Connection, aviso_id: str, cand_id: str, score: float):
    con.execute(
        "INSERT INTO notifications (aviso_id, candidato_id, score, created_at) VALUES (?,?,?,?)",
        (aviso_id, cand_id, score, datetime.now().astimezone().isoformat()),
    )
    con.commit()
