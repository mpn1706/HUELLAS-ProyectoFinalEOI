"""Carga seed Jerez → SQLite. Trazable a REQ-03.8 + REQ-05."""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.db import connect, upsert_aviso  # noqa: E402
from agents.ingestor import normalize_aviso  # noqa: E402


def main(db_path: str = "data/huellas.db"):
    con = connect(db_path)
    n = 0
    for folder in ("lost", "found"):
        for fp in sorted((ROOT / "data" / "seed" / folder).glob("*.json")):
            raw = json.loads(fp.read_text(encoding="utf-8"))
            upsert_aviso(con, normalize_aviso(raw))
            n += 1
    print(f"seed cargado: {n} avisos en {db_path}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/huellas.db")
