"""Precomputa vectores CLIP reales para las fotos del seed.

Requiere torch+transformers (SOLO en local, NO van a requirements.txt
para no engordar Cloud). Genera data/seed/embeddings.json {id: vector},
que sí viaja en git y la app usa sin necesidad de torch.

Flujo fotos reales:
  1. Coloca JPG (<=800px, <500KB, propias o licencia libre) en data/seed/images/
     nombrados por aviso (p.ej. found_001.jpg) y apunta image_url en su JSON.
  2. pip install torch --index-url https://download.pytorch.org/whl/cpu
     pip install transformers pillow
  3. python scripts/compute_embeddings.py
  4. commit de data/seed/images + data/seed/*.json + data/seed/embeddings.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.vision import DIM, get_image_embedding  # noqa: E402


def main():
    try:
        import torch  # noqa: F401
        import transformers  # noqa: F401
    except ImportError:
        print("Falta torch/transformers (solo local). Ver docstring para instalar.")
        sys.exit(2)
    out = {}
    for folder in ("lost", "found"):
        for fp in sorted((ROOT / "data" / "seed" / folder).glob("*.json")):
            doc = json.loads(fp.read_text(encoding="utf-8"))
            if doc.get("image_embedding"):
                out[doc["id"]] = doc["image_embedding"]
                print(f"{doc['id']}: ya fijado, se conserva")
                continue
            img = ROOT / doc["image_url"]
            if not img.exists():
                print(f"{doc['id']}: falta {doc['image_url']}, se omite")
                continue
            vec = get_image_embedding(str(img))
            assert len(vec) == DIM, doc["id"]
            out[doc["id"]] = vec
            print(f"{doc['id']}: CLIP real ({DIM}-dim)")
    with open(ROOT / "data" / "seed" / "embeddings.json", "w", encoding="utf-8") as f:
        json.dump(out, f)
    print(f"embeddings.json: {len(out)} vectores")


if __name__ == "__main__":
    main()
