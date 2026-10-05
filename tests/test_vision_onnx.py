"""Visión Cloud: MobileNetV3-Small en ONNX (576-d) — espacio "onnx"."""
from pathlib import Path

import numpy as np

from agents.matcher import cosine
from agents.vision import ONNX_DIM, ONNX_MODEL, _onnx_embedding

IMG_A = "data/seed/images/lost_001.jpg"
IMG_B = "data/seed/images/gato alert coincidencia con lost_001.jpg"
IMG_C = "data/seed/images/lost_002.png"


def test_modelo_onnx_presente():
    assert Path(ONNX_MODEL).exists(), "falta el modelo ONNX en data/models/"
    assert Path(ONNX_MODEL + ".data").exists(), "faltan los pesos externos del ONNX"


def test_dim_y_determinista():
    v = _onnx_embedding(IMG_A)
    assert len(v) == ONNX_DIM == 576
    assert v == _onnx_embedding(IMG_A)


def test_normalizado():
    v = np.asarray(_onnx_embedding(IMG_A))
    assert abs(float(np.linalg.norm(v)) - 1.0) < 1e-3


def test_par_insignia_por_encima_de_gato_vs_perro():
    # El par demo (gatos naranjas) debe superar al cruce gato↔perro
    # (medido en Fase 0: 0.77 vs 0.52). Regresión si se sustituye el modelo.
    par = cosine(_onnx_embedding(IMG_A), _onnx_embedding(IMG_B))
    cruz = cosine(_onnx_embedding(IMG_A), _onnx_embedding(IMG_C))
    assert par > 0.7, par
    assert par > cruz + 0.1, (par, cruz)


def test_misma_foto_da_uno():
    v = _onnx_embedding(IMG_A)
    assert abs(cosine(v, v) - 1.0) < 1e-9
