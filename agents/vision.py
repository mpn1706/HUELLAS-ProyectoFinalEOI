"""Agente Vision Analyst — REQ-06.2.

Modelo canónico: CLIP openai/clip-vit-base-patch32, 512-dim (decisión 2).
Carga perezosa con tres niveles:
  1. CLIP (torch/transformers, local) → espacio "clip", 512-dim.
  2. MobileNetV3-Small en ONNX (sin torch, Cloud) → espacio "onnx", 576-dim.
     Pesos torchvision IMAGENET1K_V1 exportados con torch 2.9; ~4 MB en
     data/models/ (ONNX + datos externos) y ~10 MB de RAM en ejecución:
     cabe en el free tier sin OOM.
  3. Histograma de color 8³ → "hist" y hash determinista → "hash"
     (último recurso si faltan runtime o ficheros).
Regla de oro (S49): query y candidatos se comparan SIEMPRE en el mismo
espacio (nunca mezclar CLIP con onnx/hist).
"""
import hashlib
from functools import lru_cache
from pathlib import Path

import numpy as np

MODEL_ID = "openai/clip-vit-base-patch32"
DIM = 512
EMBEDDINGS_JSON = "data/seed/embeddings.json"
ONNX_MODEL = "data/models/mobilenetv3_small_feat.onnx"
ONNX_DIM = 576

_model = None
_processor = None
_onnx_sess = None


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


def _prep_onnx(path: str):
    """Imagen → NCHW float32 (1,3,224,224) con el preproceso ImageNet de torchvision.

    Resize del lado corto a 256 + recorte central 224 + normalización.
    Solo PIL+numpy (sin torchvision: corre en Cloud).
    """
    from PIL import Image

    img = Image.open(path).convert("RGB")
    w, h = img.size
    if w <= h:
        nw, nh = 256, max(1, round(h * 256 / w))
    else:
        nw, nh = max(1, round(w * 256 / h)), 256
    img = img.resize((nw, nh))
    left, top = (nw - 224) // 2, (nh - 224) // 2
    img = img.crop((left, top, left + 224, top + 224))
    arr = np.asarray(img, dtype=np.float32) / 255.0
    arr = (arr - np.array([0.485, 0.456, 0.406], dtype=np.float32)) / \
          np.array([0.229, 0.224, 0.225], dtype=np.float32)
    return arr.transpose(2, 0, 1)[np.newaxis, :, :, :]


@lru_cache(maxsize=128)
def _onnx_emb_cached(path: str, stamp: tuple) -> list:
    """Vector 576-d normalizado del fichero (cache por ruta+mtime+tamaño).

    `stamp` evita servir un vector viejo si la foto cambia bajo el mismo
    path (p. ej. data/uploads/_busqueda.jpg se reescribe en cada búsqueda).
    """
    global _onnx_sess
    import onnxruntime

    if _onnx_sess is None:
        _onnx_sess = onnxruntime.InferenceSession(ONNX_MODEL, providers=["CPUExecutionProvider"])
    out = _onnx_sess.run(None, {"input": _prep_onnx(path)})[0]
    return out[0].tolist()


def _onnx_embedding(path: str) -> list:
    """Vector MobileNetV3-ONNX si el modelo existe; si no, FileNotFoundError."""
    if not Path(ONNX_MODEL).exists():
        raise FileNotFoundError(ONNX_MODEL)
    st = Path(path).stat()
    return _onnx_emb_cached(str(path), (st.st_mtime_ns, st.st_size))


def embedida_con_espacio(image_path: str) -> tuple:
    """Incrusta una imagen y dice en qué espacio: clip | onnx | hist | hash.

    Regla de oro (S49): query y candidatos DEBEN compararse en el mismo
    espacio. Mezclarlos (p.ej. query en hist contra CLIP almacenado) da
    similitud ~0.09 y vacía el ranking en Cloud, donde no hay torch.
    Orden: CLIP si hay torch (local); si no, MobileNetV3-ONNX (Cloud);
    si no, histograma; y como último recurso hash de los bytes.
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
        return _onnx_embedding(image_path), "onnx"
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
    """Vector normalizado de la imagen (CLIP 512 · ONNX 576 · hist 512).

    Intenta CLIP real (local), si no MobileNetV3-ONNX (Cloud), si no
    fallbacks deterministas. Si el fichero no existe, hash de la ruta.
    """
    vec, _ = embedida_con_espacio(image_path)
    return vec


def embed_candidato(a: dict, espacio: str):
    """Vector del candidato EN EL MISMO espacio que la query (ver S49).

    clip → vector almacenado; onnx/hist → recalculado del fichero
    (las fotos del seed viajan en git, también en Cloud); hash →
    bytes. Si el fichero falta, último recurso: lo almacenado aunque
    mezcle espacios.
    """
    if espacio == "clip" and a.get("image_embedding"):
        return a["image_embedding"]
    if espacio == "onnx":
        try:
            return _onnx_embedding(a["image_url"])
        except Exception:
            pass
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
