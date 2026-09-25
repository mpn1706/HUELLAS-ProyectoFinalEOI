"""Agente Matcher — REQ-06.3 + REQ-07 + REQ-08.

score_total = 0.55*visual + 0.25*texto + 0.10*temporal + 0.10*geo
similitud_texto = 0.70*estructurado + 0.30*semántico
Umbrales con >= (decisión 6, v1.2 S51): >=0.80 notifica, >=0.65 lista.
Puerta visual (v1.40 S108): visual>=0.95 también notifica/lista aunque el
total no llegue (la misma foto siempre da visual 1.0; dos fotos distintas
rara vez pasan de ~0.65 con histograma).
v1.40 (25/09/2026, decisión del alumno S108): visual 0.40→0.55, texto
0.30→0.25, temporal 0.20→0.10, geo se queda en 0.10 — el visual manda más
y fecha/zona (ruido en Buscar) pesan menos. Descartado 0.60 de visual:
la demo E2E caía a 0.798 <0.80.
v1.2 (S51): geo 0.30→0.10, texto 0.20→0.30, temporal 0.10→0.20 —
decisión del alumno: la ubicación lejana penalizaba demasiado.
"""
import math
import unicodedata

import numpy as np

from .geo import haversine_km, proximidad_geografica, RADIO_MAX_KM
from .ingestor import effective_date

PESO_VISUAL = 0.55
PESO_TEXTO = 0.25
PESO_TEMP = 0.10
PESO_GEO = 0.10

PESO_ESTRUCT = 0.70
PESO_SEMANT = 0.30

UMBRAL_NOTIF = 0.80
UMBRAL_LISTA = 0.65
UMBRAL_GATE_VISUAL = 0.95

VENTANA_DIAS = 30

# Alias mínimos de color (ya normalizados): variantes habituales → canónico.
# Tabla corta y documentada; NO inventa colores nuevos.
COLOR_ALIAS = {
    "cafe": "marron", "canela": "marron", "chocolate": "marron",
    "grisaceo": "gris", "ceniza": "gris", "cenizo": "gris",
    "azabache": "negro",
}


def normalizar_txt(s: str) -> str:
    """Minúsculas, sin tildes, espacios colapsados.

    "Marrón" == "marron" == "  MARRÓN ". Se aplica al comparar
    color_primary y markings (el seed y los formularios mezclan
    tildes y mayúsculas y la igualdad exacta los penalizaba).
    """
    s = unicodedata.normalize("NFD", (s or "").lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return " ".join(s.split())


def canon_color(s: str) -> str:
    """Color normalizado y con alias resuelto."""
    n = normalizar_txt(s)
    return COLOR_ALIAS.get(n, n)


def cosine(a, b) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def similitud_estructurada(q: dict, c: dict) -> float:
    """Media de 4 señales: color_primary, size, has_collar, markings(Jaccard).

    Color y markings se comparan normalizados (sin tildes/mayúsculas,
    con alias de color) para no penalizar "Marrón" vs "marron".
    """
    parts = [
        1.0 if canon_color(q.get("color_primary")) == canon_color(c.get("color_primary")) else 0.0,
        1.0 if (q.get("size") or "") == (c.get("size") or "") else 0.0,
        1.0 if bool(q.get("has_collar")) == bool(c.get("has_collar")) else 0.0,
    ]
    mq = {normalizar_txt(m) for m in (q.get("markings") or [])} - {""}
    mc = {normalizar_txt(m) for m in (c.get("markings") or [])} - {""}
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
    return PESO_VISUAL * visual + PESO_TEXTO * texto + PESO_TEMP * temp + PESO_GEO * geo


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
    score = round(total, 4)
    visual_r = round(float(visual), 4)
    gate = visual_r >= UMBRAL_GATE_VISUAL
    return {
        "candidato_id": c["id"],
        "score": score,
        "visual": visual_r,
        "geo": round(geo, 4),
        "texto": round(texto, 4),
        "temporal": round(temp, 4),
        "dist_km": round(dist_km, 2),
        "notifica": (score >= UMBRAL_NOTIF) or gate,
        "lista": (score >= UMBRAL_LISTA) or gate,
    }


def explain(m: dict) -> str:
    return (
        f"Posible coincidencia {m['score']*100:.1f}% — "
        f"visual {m['visual']:.2f}, geo {m['geo']:.2f} ({m['dist_km']} km), "
        f"texto {m['texto']:.2f}, temporal {m['temporal']:.2f}."
    )
