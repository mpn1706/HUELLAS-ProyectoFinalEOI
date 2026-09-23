"""Sincroniza make_seed.py con los JSON ya geocodificados (una sola dirección de verdad).

Lee cada data/seed/{lost,found}/<id>.json y reescribe la línea de
coords+dirección de su tupla en scripts/make_seed.py.
Uso: python scripts/sync_seed_gen.py ; después verificar con make_seed.py (debe ser no-op).
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "scripts" / "make_seed.py"


def main():
    src = GEN.read_text(encoding="utf-8")
    n = 0
    for folder in ("lost", "found"):
        for fp in sorted((ROOT / "data" / "seed" / folder).glob("*.json")):
            doc = json.loads(fp.read_text(encoding="utf-8"))
            aid = fp.stem
            loc = doc["location"]
            start = src.index(f'("{aid}.json"')
            end = src.index("),", start) + 2
            block = src[start:end]
            new_block, cnt = re.subn(
                r"-?\d+\.\d+, -?\d+\.\d+, \"((?:[^\"\\\\]|\\\\.)*)\"",
                f"{loc['lat']}, {loc['lng']}, \"{loc['address_text']}\"",
                block, count=1)
            assert cnt == 1, aid
            src = src[:start] + new_block + src[end:]
            n += 1
    GEN.write_text(src, encoding="utf-8")
    print(f"sincronizadas {n} tuplas en make_seed.py")


if __name__ == "__main__":
    main()
