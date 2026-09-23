"""Retrieval — filtra active + tipo opuesto y ordena por score_total."""
from agents.matcher import UMBRAL_LISTA, match_one


def retrieve(query: dict, candidatos: list, visual_fn, semant_fn) -> list:
    """visual_fn(c) y semant_fn(q_text, c_text) inyectables (test/real)."""
    out = []
    for c in candidatos:
        if c["id"] == query["id"]:
            continue
        m = match_one(query, c, visual_fn(c), semant_fn(query.get("description_text", ""), c.get("description_text", "")))
        if m["lista"]:
            m["candidato"] = c
            out.append(m)
    return sorted(out, key=lambda m: m["score"], reverse=True)
