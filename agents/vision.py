"""Agente Vision Analyst — REQ-06.2.

Modelo canónico: CLIP openai/clip-vit-base-patch32, 512-dim (decisión 2).
Carga perezosa: si torch/transformers no están instalados o falla la
descarga, usa fallback determinista (hash → vector 512 normalizado)
para que el MVP siga ejecutable en local sin claves ni GPU.
"""
import hashlib

import numpy as np

MODEL_ID = "openai/clip-vit-base-patch32"
DIM = 512
EMBEDDINGS_JSON = "data/seed/embeddings.json"

_model = None
_processor = None


def _fallback_embedding(key: str, dim: int = DIM) -> list:
    h = hashlib.sha256(str(key).encode("utf-8")).digest()
    seed = int.from_bytes(h[:8], "big") % (2**32)
    rng = np.random.RandomState(seed)
    v = rng.randn(dim)
    v = v / np.linalg.norm(v)
    return v.tolist()


def _histogram_embedding(image_path: str, dim: int = DIM) -> list:
    """Paleta de color 8x8x8 (=512-dim) sobre recorte central.

    Fallback honesto sin torch: animales del mismo color dan similitud
    alta aunque sean fotos distintas. Determinista y normalizado.
    """
    from PIL import Image

    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    img = img.crop((int(w * 0.2), int(h * 0.2), int(w * 0.8), int(h * 0.8))).resize((64, 64))
    px = np.asarray(img).reshape(-1, 3) // 32
    hist = np.zeros(512)
    for idx in (px[:, 0] * 64 + px[:, 1] * 8 + px[:, 2]):
        hist[int(idx)] += 1.0
    hist = hist / hist.sum()
    return hist.tolist()


def _hash_bytes_embedding(key) -> list:
    """Hash determinista → vector 512 normalizado (bytes o ruta)."""
    if isinstance(key, bytes):
        h = hashlib.sha256(key).digest()
        seed = int.from_bytes(h[:8], "big") % (2**32)
        rng = np.random.RandomState(seed)
        v = rng.randn(DIM)
        return (v / np.linalg.norm(v)).tolist()
    return _fallback_embedding(key)


def embedida_con_espacio(image_path: str) -> tuple:
    """Incrusta una imagen y dice en qué espacio: clip | hist | hash.

    Regla de oro (S49): query y candidatos DEBEN compararse en el mismo
    espacio. Mezclarlos (p.ej. query en hist contra CLIP almacenado) da
    similitud ~0.09 y vacía el ranking en Cloud, donde no hay torch.
    """
    global _model, _processor
    try:
        from PIL import Image
        from transformers import CLIPModel, CLIPProcessor

        if _model is None:
            _processor = CLIPProcessor.from_pretrained(MODEL_ID)
            _model = CLIPModel.from_pretrained(MODEL_ID)
            _model.eval()
        import torch

        img = Image.open(image_path).convert("RGB")
        inputs = _processor(images=img, return_tensors="pt")
        with torch.no_grad():
            out = _model.get_image_features(**inputs)
            # transformers>=4.4x devuelve BaseModelOutputWithPooling; antes Tensor
            feat = out.pooler_output if hasattr(out, "pooler_output") else out
            feat = feat.cpu().numpy()[0]
        feat = feat / np.linalg.norm(feat)
        return feat.tolist(), "clip"
    except Exception:
        pass
    try:
        return _histogram_embedding(image_path), "hist"
    except Exception:
        pass
    try:
        with open(image_path, "rb") as f:
            key = f.read()
    except OSError:
        key = f"img:{image_path}"
    return _hash_bytes_embedding(key), "hash"


def get_image_embedding(image_path: str) -> list:
    """Devuelve vector 512 normalizado. Intenta CLIP real, si no fallback.

    Fallback: hash de los bytes del fichero (dos fotos placeholder del
    mismo color sólido dan el mismo vector → similitud alta, coherente).
    Si el fichero no existe, hash de la ruta.
    """
    vec, _ = embedida_con_espacio(image_path)
    return vec


def embed_candidato(a: dict, espacio: str):
    """Vector del candidato EN EL MISMO espacio que la query (ver S49).

    clip → vector almacenado; hist/hash → recalculado del fichero
    (las fotos del seed viajan en git, también en Cloud). Si el fichero
    falta, último recurso: lo almacenado aunque mezcle espacios.
    """
    if espacio == "clip" and a.get("image_embedding"):
        return a["image_embedding"]
    if espacio == "hist":
        try:
            return _histogram_embedding(a["image_url"])
        except Exception:
            pass
    if espacio == "hash":
        try:
            with open(a["image_url"], "rb") as f:
                key = f.read()
        except OSError:
            key = f"img:{a.get('image_url')}"
        return _hash_bytes_embedding(key)
    if a.get("image_embedding"):
        return a["image_embedding"]
    return _fallback_embedding(f"img:{a['id']}")


def sync_seed_embeddings(con) -> int:
    """Actualiza image_embedding si embeddings.json trae otro vector.

    Caso: se sustituye la foto de un aviso (misma descripción e id).
    Evita subir SEED_VERSION (y el wipe) cuando solo cambia una imagen.
    Devuelve nº de avisos actualizados.
    """
    import json as _json

    try:
        with open(EMBEDDINGS_JSON, encoding="utf-8") as f:
            pre = _json.load(f)
    except OSError:
        return 0
    n = 0
    for _id, vec in pre.items():
        r = con.execute("SELECT image_embedding FROM avisos WHERE id=?", (_id,)).fetchone()
        if not r:
            continue
        want = _json.dumps(vec)
        if r["image_embedding"] != want:
            con.execute("UPDATE avisos SET image_embedding=? WHERE id=?", (want, _id))
            n += 1
    con.commit()
    return n


def backfill_embeddings(con) -> int:
    """Rellena image_embedding NULL sin tocar los ya fijados.

    Orden: (1) data/seed/embeddings.json (vectores CLIP precomputados,
    generan Cloud sin torch); (2) get_image_embedding (CLIP si hay torch,
    si no fallback determinista). Devuelve nº rellenados.
    """
    import json as _json

    pre = {}
    try:
        with open(EMBEDDINGS_JSON, encoding="utf-8") as f:
            pre = _json.load(f)
    except OSError:
        pass
    n = 0
    for r in con.execute("SELECT id, image_url FROM avisos WHERE image_embedding IS NULL").fetchall():
        vec = pre.get(r["id"])
        if vec is None:
            try:
                vec = get_image_embedding(r["image_url"])
            except Exception:
                continue
        con.execute("UPDATE avisos SET image_embedding=? WHERE id=?",
                    (_json.dumps(vec), r["id"]))
        n += 1
    con.commit()
    return n
