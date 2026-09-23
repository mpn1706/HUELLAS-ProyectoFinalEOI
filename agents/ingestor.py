"""Agente Ingestor — REQ-06.1 + REQ-05.

Normaliza avisos al esquema. Preserva description_text intacto.
Manda Vision en atributos visuales (decisión 10): aquí NO se inventan
atributos visuales, solo se validan/normalizan los declarados.
"""
import uuid
from datetime import datetime

ANIMALS = {"dog", "cat", "other"}
SIZES = {"small", "medium", "large"}
TYPES = {"lost", "found"}
STATUS = {"active", "resolved", "expired"}


def _norm_str(v, lower=True):
    if v is None:
        return None
    v = str(v).strip()
    if not v:
        return None
    return v.lower() if lower else v


def effective_date(aviso: dict) -> datetime:
    """Fecha usada en proximidad temporal (decisión 4).

    date_last_seen si existe, si no date_reported.
    """
    raw = aviso.get("date_last_seen") or aviso.get("date_reported")
    if not raw:
        raise ValueError("aviso sin fecha comparable")
    return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))


def validate_aviso(d: dict) -> list:
    """Devuelve lista de errores (vacía si válido). No lanza."""
    errs = []
    if d.get("type") not in TYPES:
        errs.append("type debe ser lost|found")
    if d.get("animal") not in ANIMALS:
        errs.append("animal debe ser dog|cat|other")
    if not d.get("color_primary"):
        errs.append("color_primary obligatorio")
    if not d.get("size") in SIZES:
        errs.append("size debe ser small|medium|large")
    if not d.get("description_text"):
        errs.append("description_text obligatorio")
    if d.get("animal") == "other" and d.get("breed_guess"):
        errs.append("breed_guess debe omitirse si animal=other")
    loc = d.get("location") or {}
    try:
        lat, lng = float(loc.get("lat")), float(loc.get("lng"))
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            errs.append("lat/lng fuera de rango")
    except (TypeError, ValueError):
        errs.append("location.lat/lng numéricos obligatorios")
    for k in ("date_reported",):
        try:
            datetime.fromisoformat(str(d.get(k, "")).replace("Z", "+00:00"))
        except ValueError:
            errs.append(f"{k} debe ser ISO 8601")
    if d.get("date_last_seen"):
        try:
            datetime.fromisoformat(str(d["date_last_seen"]).replace("Z", "+00:00"))
        except ValueError:
            errs.append("date_last_seen debe ser ISO 8601")
    if not d.get("image_url"):
        errs.append("image_url obligatorio (ruta local data/seed/images/)")
    if d.get("status", "active") not in STATUS:
        errs.append("status inválido")
    return errs


def normalize_aviso(raw: dict) -> dict:
    """Normaliza un aviso nuevo. Genera UUID, fija status=active si ausente.

    Lanza ValueError si inválido.
    """
    d = dict(raw)
    d["id"] = d.get("id") or str(uuid.uuid4())
    d["type"] = _norm_str(d.get("type"))
    d["animal"] = _norm_str(d.get("animal"))
    d["color_primary"] = _norm_str(d.get("color_primary"))
    d["color_secondary"] = _norm_str(d.get("color_secondary"))
    d["size"] = _norm_str(d.get("size"))
    if isinstance(d.get("markings"), str):
        d["markings"] = [m.strip().lower() for m in d["markings"].split(",") if m.strip()]
    d["markings"] = list(d.get("markings") or [])
    # description_text INTACTO (decisión 10): no lower, solo strip
    if d.get("description_text") is not None:
        d["description_text"] = str(d["description_text"]).strip()
    d["status"] = d.get("status") or "active"
    # breed_guess solo lo escribe Vision; si viene de usuario y es other, se anula
    if d.get("animal") == "other":
        d["breed_guess"] = None
    errs = validate_aviso(d)
    if errs:
        raise ValueError("Aviso inválido: " + "; ".join(errs))
    return d
