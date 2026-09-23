"""Agente Notifier — REQ-06.5 + REQ-08.

MVP: panel/tabla Streamlit + log + tabla notifications. Sin Telegram
(decisión 9). Umbral con >= 0.85 (decisión 6).
"""
from pathlib import Path

from .db import save_notification
from .matcher import UMBRAL_NOTIF


def notificar(con, query_id: str, matches: list, log_path: str = "data/notifications.log") -> list:
    """Filtra matches >=0.85, persiste y añade al log. Devuelve notificados."""
    hechos = [m for m in matches if m["score"] >= UMBRAL_NOTIF]
    if not hechos:
        return []
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        for m in hechos:
            save_notification(con, query_id, m["candidato_id"], m["score"])
            f.write(f"{query_id} -> {m['candidato_id']} {m['score']:.4f}\n")
    return hechos
