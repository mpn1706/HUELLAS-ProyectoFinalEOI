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
