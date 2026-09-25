"""Administración básica — REQ-11 (un único admin con contraseña).

Capacidades: listar con filtros, eliminar duplicados/vandalismo,
marcar resueltos. Toda acción queda registrada en data/admin.log.
"""
import hmac
from datetime import datetime
from pathlib import Path

from .db import _from_row, set_resolved


def check_password(pw: str, expected: str) -> bool:
    """Comparación segura (hmac). Sin contraseña configurada, nunca pasa.

    La contraseña vive en Secrets `ADMIN_PASSWORD` (Cloud) o en la
    variable `HUELLAS_ADMIN_PASSWORD` (local); sin ninguna de las dos,
    la administración queda desactivada (expected vacío → acceso denegado).
    """
    return bool(pw) and bool(expected) and hmac.compare_digest(str(pw), str(expected))


def list_avisos(con, tipo: str = "todos", texto: str = "") -> list:
    q = "SELECT * FROM avisos WHERE 1=1"
    params: list = []
    if tipo in ("lost", "found"):
        q += " AND type=?"
        params.append(tipo)
    if texto:
        q += " AND (id LIKE ? OR description_text LIKE ? OR color_primary LIKE ?)"
        like = f"%{texto}%"
        params += [like, like, like]
    q += " ORDER BY date_reported DESC"
    return [_from_row(r) for r in con.execute(q, params).fetchall()]


def _log(log_path: str, msg: str):
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().astimezone().isoformat()} {msg}\n")


def log_action(msg: str, log_path: str = "data/admin.log"):
    _log(log_path, msg)


def delete_aviso(con, aviso_id: str, log_path: str = "data/admin.log") -> bool:
    """Borrado total: aviso + notificaciones ligadas + foto si es subida (no seed)."""
    row = con.execute("SELECT image_url FROM avisos WHERE id=?", (aviso_id,)).fetchone()
    if not row:
        return False
    n_not = con.execute(
        "DELETE FROM notifications WHERE aviso_id=? OR candidato_id=?",
        (aviso_id, aviso_id)).rowcount
    con.execute("DELETE FROM avisos WHERE id=?", (aviso_id,))
    con.commit()
    img = row["image_url"] or ""
    if img.startswith("data/uploads/"):
        try:
            Path(img).unlink(missing_ok=True)
        except OSError:
            pass
    _log(log_path, f"DELETE {aviso_id} (+{n_not} notif)")
    return True


def resolve_aviso(con, aviso_id: str, log_path: str = "data/admin.log") -> bool:
    set_resolved(con, aviso_id)
    _log(log_path, f"RESOLVE {aviso_id}")
    return True
