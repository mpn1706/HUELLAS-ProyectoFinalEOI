"""Retrieval — filtra active + tipo opuesto y ordena por score_total.

embed_fn(aviso) -> vector 512; la similitud visual se calcula aquí
con coseno para que Matcher siempre reciba floats (REQ-07).
"""
from agents.matcher import UMBRAL_LISTA, cosine, match_one


def retrieve(query: dict, candidatos: list, embed_fn, semant_fn) -> list:
    q_emb = embed_fn(query)
    out = []
    for c in candidatos:
        if c["id"] == query["id"]:
            continue
        visual = cosine(q_emb, embed_fn(c))
        m = match_one(query, c, visual, semant_fn(query.get("description_text", ""), c.get("description_text", "")))
        if m["lista"]:
            m["candidato"] = c
            out.append(m)
    return sorted(out, key=lambda m: m["score"], reverse=True)
