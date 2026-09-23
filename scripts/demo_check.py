"""Demo E2E ÉXITO-01: lost_001 debe recuperar found_011 arriba con score de alerta."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents import db as dbmod
from agents.vision import get_image_embedding
from rag.embeddings import semantic_similarity
from rag.retrieval import retrieve

con = dbmod.connect("data/huellas.db")
q = dbmod.get_aviso(con, "lost_001")
cands = dbmod.get_active_opuestos(con, "lost")


def embed(a):
    return a["image_embedding"] or get_image_embedding(a["image_url"])


ms = retrieve(q, cands, embed, semantic_similarity)
print(f"query lost_001 vs {len(cands)} found activos")
for m in ms[:5]:
    print(f"  {m['candidato_id']}: {m['score']*100:.1f}% v={m['visual']:.2f} g={m['geo']:.2f} t={m['texto']:.2f} tmp={m['temporal']:.2f} {m['dist_km']}km")
top = ms[0]["candidato_id"] if ms else None
assert top == "found_011", f"ÉXITO-01 falla: top={top}"
assert ms[0]["score"] >= 0.85, f"ÉXITO-01 falla: {ms[0]['score']:.3f} bajo umbral de alerta"
resto = {m["candidato_id"]: m["score"] for m in ms}
assert resto.get("found_001", 0) >= 0.65, "found_001 debe seguir en lista ≥65%"
print("E2E OK: found_011 es top-1 con score >=85% (alerta real)")
