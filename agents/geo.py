"""Agente Geo — REQ-06.4 + REQ-07.

Radio máximo fijo: 15 km (decisión 5, 23/09/2026).
proximidad = max(0, 1 - distancia_km / 15)
"""
import math

RADIO_MAX_KM = 15.0
EARTH_R_KM = 6371.0


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distancia haversine en km entre dos puntos."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * EARTH_R_KM * math.asin(math.sqrt(a))


def proximidad_geografica(distancia_km: float, radio_max: float = RADIO_MAX_KM) -> float:
    """Convierte distancia a proximidad 0-1. Fuera de radio → 0."""
    if distancia_km < 0:
        raise ValueError("distancia_km no puede ser negativa")
    return max(0.0, 1.0 - distancia_km / radio_max)
