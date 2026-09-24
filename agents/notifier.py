"""Agente Notifier — REQ-06.5 + REQ-08.

MVP: panel/tabla Streamlit + log + tabla notifications. Sin Telegram
(decisión 9). Umbral con >= 0.80 (decisión 6, v1.2 S51).
Sin duplicados: un par (aviso, candidato) genera UNA fila; si el score
cambia se actualiza, si es idéntico se ignora.
"""
from datetime import datetime
from pathlib import Path

from .db import save_notification
from .matcher import UMBRAL_NOTIF


def notificar(con, query_id: str, matches: list, log_path: str = "data/notifications.log") -> list:
    """Registra solo novedades y devuelve las nuevas/actualizadas."""
    nuevos = []
    for m in matches:
        if m["score"] < UMBRAL_NOTIF:
            continue
        row = con.execute(
            "SELECT score FROM notifications WHERE aviso_id=? AND candidato_id=?",
            (query_id, m["candidato_id"])).fetchone()
        if row and abs(row["score"] - m["score"]) < 1e-9:
            continue
        if row:
            con.execute(
                "UPDATE notifications SET score=?, created_at=? WHERE aviso_id=? AND candidato_id=?",
                (m["score"], datetime.now().astimezone().isoformat(), query_id, m["candidato_id"]))
            con.commit()
        else:
            save_notification(con, query_id, m["candidato_id"], m["score"])
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{query_id} -> {m['candidato_id']} {m['score']:.4f}\n")
        nuevos.append(m)
    return nuevos
