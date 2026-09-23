"""Eval mínima ÉXITO-01/03 con vectores fijos (sin modelos)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.matcher import match_one  # noqa: E402

q = {"id": "q", "color_primary": "marrón", "size": "medium", "has_collar": True,
     "markings": ["mancha blanca pecho"],
     "location": {"lat": 36.6826, "lng": -6.1376},
     "date_reported": "2026-09-20T10:00:00+02:00", "date_last_seen": "2026-09-19T10:00:00+02:00"}
c = {"id": "c", "color_primary": "marrón", "size": "medium", "has_collar": True,
     "markings": ["mancha blanca pecho"],
     "location": {"lat": 36.6836, "lng": -6.1386},
     "date_reported": "2026-09-20T12:00:00+02:00", "date_last_seen": "2026-09-19T12:00:00+02:00"}

m = match_one(q, c, visual=0.9, semant=0.9)
print(m)
assert m["score"] >= 0.85, "ÉXITO-01/03: el par idéntico debe notificar"
print("EVAL OK: fórmula y umbrales verificados con vectores fijos")
