"""RAG textual — fallback TF-IDF/Jaccard con raíces (diminutivos, género)."""
from rag.embeddings import _jaccard, _norm_es, _tokens


def test_tokens_reducen_diminutivos():
    assert _tokens("Gatito ATIGRADO") == {"gat", "atigrad"}


def test_norm_es_une_raices():
    assert _norm_es("Gatitos atigraditos blancos") == "gat atigrad blanc"


def test_jaccard_diminutivo_es_uno():
    assert _jaccard("gatito atigrado", "gato atigrado") == 1.0
    assert _jaccard("perrito blanco", "perra blanca") == 1.0


def test_jaccard_distinto_no_identico():
    assert _jaccard("gato negro", "perro blanco") == 0.0
