"""Carga seed Jerez → SQLite. Trazable a REQ-03.8 + REQ-05."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.db import (SEED_VERSION, connect, get_seed_version, set_seed_version, upsert_aviso,  # noqa: E402
                       upsert_reencuentro_seed, wipe_all)
from agents.ingestor import normalize_aviso  # noqa: E402
from agents.vision import backfill_embeddings  # noqa: E402


def seed_reencuentros(con) -> int:
    """Siembra los reencuentros demo versionados (ids fijos renc_*).

    Los casos cerrados ocultan sus avisos de Perdidos/Avistamientos
    (los pendientes siguen visibles hasta que se cierren).
    """
    from agents.db import resolver_casos_validados  # noqa: E402

    n = 0
    for fp in sorted((ROOT / "data" / "seed" / "reencuentros").glob("*.json")):
        upsert_reencuentro_seed(con, json.loads(fp.read_text(encoding="utf-8")))
        n += 1
    resolver_casos_validados(con)
    return n


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
    r = seed_reencuentros(con)
    print(f"seed v{SEED_VERSION} cargado: {n} avisos + {e} embeddings + {r} reencuentros en {db_path}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/huellas.db")
