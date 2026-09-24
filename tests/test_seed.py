"""Tests seed demo — v1.4: todo aviso seed trae dato de contacto (REQ-09.5, CU-01/02)."""
import json
from pathlib import Path

SEED = Path("data/seed")


def _seeds():
    return sorted(SEED.glob("lost/*.json")) + sorted(SEED.glob("found/*.json"))


def test_todo_seed_con_contacto():
    fps = _seeds()
    assert fps, "sin ficheros seed"
    sin = []
    for fp in fps:
        d = json.loads(fp.read_text(encoding="utf-8"))
        if not str(d.get("contact_info") or "").strip():
            sin.append(fp.name)
    assert not sin, f"seed sin contacto: {sin}"


def test_contactos_con_formato_valido():
    for fp in _seeds():
        d = json.loads(fp.read_text(encoding="utf-8"))
        c = str(d.get("contact_info") or "").strip()
        assert c, fp.name
        assert "@" in c or any(ch.isdigit() for ch in c), f"{fp.name}: {c!r}"
