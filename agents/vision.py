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

_model = None
_processor = None


def _fallback_embedding(key: str, dim: int = DIM) -> list:
    h = hashlib.sha256(str(key).encode("utf-8")).digest()
    seed = int.from_bytes(h[:8], "big") % (2**32)
    rng = np.random.RandomState(seed)
    v = rng.randn(dim)
    v = v / np.linalg.norm(v)
    return v.tolist()


def get_image_embedding(image_path: str) -> list:
    """Devuelve vector 512 normalizado. Intenta CLIP real, si no fallback."""
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
            feat = _model.get_image_features(**inputs).cpu().numpy()[0]
        feat = feat / np.linalg.norm(feat)
        return feat.tolist()
    except Exception:
        return _fallback_embedding(f"img:{image_path}")
