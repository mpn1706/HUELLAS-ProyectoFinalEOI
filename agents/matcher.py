"""Agente Matcher — REQ-06.3 + REQ-07 + REQ-08.

score_total = 0.40*visual + 0.30*geo + 0.20*texto + 0.10*temporal
similitud_texto = 0.70*estructurado + 0.30*semántico
Umbrales con >= (decisión 6): >=0.85 notifica, >=0.65 lista.
"""
import math

import numpy as np

from .geo import haversine_km, proximidad_geografica, RADIO_MAX_KM
from .ingestor import effective_date

PESO_VISUAL = 0.40
PESO_GEO = 0.30
PESO_TEXTO = 0.20
PESO_TEMP = 0.10

PESO_ESTRUCT = 0.70
PESO_SEMANT = 0.30

UMBRAL_NOTIF = 0.85
UMBRAL_LISTA = 0.65

VENTANA_DIAS = 30


def cosine(a, b) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def similitud_estructurada(q: dict, c: dict) -> float:
    """Media de 4 señales: color_primary, size, has_collar, markings(Jaccard)."""
    parts = [
        1.0 if (q.get("color_primary") or "") == (c.get("color_primary") or "") else 0.0,
        1.0 if (q.get("size") or "") == (c.get("size") or "") else 0.0,
        1.0 if bool(q.get("has_collar")) == bool(c.get("has_collar")) else 0.0,
    ]
    mq, mc = set(q.get("markings") or []), set(c.get("markings") or [])
    if not mq and not mc:
        parts.append(1.0)
    else:
        parts.append(len(mq & mc) / len(mq | mc) if (mq | mc) else 0.0)
    return sum(parts) / len(parts)


def proximidad_temporal(q: dict, c: dict, ventana: int = VENTANA_DIAS) -> float:
    """max(0, 1 - dias/30) con date_last_seen si existe si no date_reported.

    Compara fechas de calendario (evita el floor negativo de timedelta).
    """
    dq, dc = effective_date(q), effective_date(c)
    dias = abs((dq.date() - dc.date()).days)
    return max(0.0, 1.0 - dias / ventana)


def similitud_texto(q: dict, c: dict, semant: float) -> float:
    return PESO_ESTRUCT * similitud_estructurada(q, c) + PESO_SEMANT * float(semant)


def score_total(visual: float, geo: float, texto: float, temp: float) -> float:
    return PESO_VISUAL * visual + PESO_GEO * geo + PESO_TEXTO * texto + PESO_TEMP * temp


def match_one(q: dict, c: dict, visual: float, semant: float) -> dict:
    """Puntúa un par lost↔found y devuelve desglose explicable."""
    dist_km = haversine_km(
        q["location"]["lat"], q["location"]["lng"],
        c["location"]["lat"], c["location"]["lng"],
    )
    geo = proximidad_geografica(dist_km, RADIO_MAX_KM)
    texto = similitud_texto(q, c, semant)
    temp = proximidad_temporal(q, c)
    total = score_total(visual, geo, texto, temp)
    return {
        "candidato_id": c["id"],
        "score": round(total, 4),
        "visual": round(visual, 4),
        "geo": round(geo, 4),
        "texto": round(texto, 4),
        "temporal": round(temp, 4),
        "dist_km": round(dist_km, 2),
        "notifica": total >= UMBRAL_NOTIF,
        "lista": total >= UMBRAL_LISTA,
    }


def explain(m: dict) -> str:
    return (
        f"Posible coincidencia {m['score']*100:.1f}% — "
        f"visual {m['visual']:.2f}, geo {m['geo']:.2f} ({m['dist_km']} km), "
        f"texto {m['texto']:.2f}, temporal {m['temporal']:.2f}."
    )
