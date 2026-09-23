"""Carga seed Jerez → SQLite. Trazable a REQ-03.8 + REQ-05."""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.db import SEED_VERSION, connect, get_seed_version, set_seed_version, upsert_aviso, wipe_all  # noqa: E402
from agents.ingestor import normalize_aviso  # noqa: E402
from agents.vision import backfill_embeddings  # noqa: E402


def main(db_path: str = "data/huellas.db"):
    con = connect(db_path)
    if get_seed_version(con) != SEED_VERSION:
        wipe_all(con)
    n = 0
    for folder in ("lost", "found"):
        for fp in sorted((ROOT / "data" / "seed" / folder).glob("*.json")):
            raw = json.loads(fp.read_text(encoding="utf-8"))
            upsert_aviso(con, normalize_aviso(raw))
            n += 1
    set_seed_version(con)
    e = backfill_embeddings(con)
    print(f"seed v{SEED_VERSION} cargado: {n} avisos + {e} embeddings en {db_path}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/huellas.db")
