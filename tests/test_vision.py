"""Tests Vision — embeddings deterministas 512-dim."""
import pytest

from agents.matcher import cosine
from agents.vision import DIM, _fallback_embedding, _histogram_embedding

IMG_A = "data/seed/images/gato 1.jpg"
IMG_B = "data/seed/images/gato 5.jpg"


def test_histograma_dim_y_normalizado():
    v = _histogram_embedding(IMG_A)
    assert len(v) == DIM
    assert abs(sum(v) - 1.0) < 1e-9


def test_histograma_determinista():
    assert _histogram_embedding(IMG_A) == _histogram_embedding(IMG_A)


def test_histograma_simismo_es_uno():
    v = _histogram_embedding(IMG_A)
    assert abs(cosine(v, v) - 1.0) < 1e-9


def test_histograma_distinto_no_identico():
    assert cosine(_histogram_embedding(IMG_A), _histogram_embedding(IMG_B)) < 0.99


def test_fallback_dim():
    assert len(_fallback_embedding("x")) == DIM


@pytest.mark.skipif(__import__("importlib").util.find_spec("torch") is None,
                    reason="CLIP solo con torch")
def test_clip_real_si_hay_torch():
    from agents.vision import get_image_embedding

    v = get_image_embedding(IMG_A)
    assert len(v) == DIM


def test_mismo_espacio_misma_foto_da_uno():
    """S49: query y candidato en hist → misma foto da 1.0 (caso Cloud)."""
    from agents.vision import _histogram_embedding, embed_candidato

    a = {"id": "t", "type": "found", "image_url": IMG_A, "image_embedding": None}
    assert abs(cosine(_histogram_embedding(IMG_A), embed_candidato(a, "hist")) - 1.0) < 1e-9


@pytest.mark.skipif(__import__("importlib").util.find_spec("torch") is None,
                    reason="CLIP solo con torch")
def test_mezclar_espacios_no_vale():
    """S49: hist contra CLIP da ~0.09 → por eso se exige mismo espacio."""
    import json

    from agents.vision import _histogram_embedding, embedida_con_espacio

    vec, espacio = embedida_con_espacio(IMG_A)
    assert espacio == "clip"
    pre = json.load(open("data/seed/embeddings.json", encoding="utf-8"))
    assert cosine(_histogram_embedding(IMG_A), pre["lost_001"]) < 0.5
