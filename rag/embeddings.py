"""RAG textual — similitud semántica del description_text.

Modelo canónico: paraphrase-multilingual-MiniLM-L12-v2 (decisión 3).
Carga perezosa con fallback TF-IDF/sklearn y último recurso Jaccard,
para ejecución local sin descargar modelos. En los fallbacks, los
tokens se reducen a raíz (raiz_es): "gatito" == "gato", "manchitas" ==
"mancha" — los sinónimos finos los aporta MiniLM cuando está disponible.
"""
import re

from agents.matcher import raiz_es

_model = None

MODEL_ID = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def _tokens(s: str) -> set:
    return {raiz_es(t) for t in re.findall(r"\w+", (s or "").lower())}


def _norm_es(s: str) -> str:
    """Texto con tokens reducidos a raíz (para TF-IDF)."""
    return " ".join(raiz_es(t) for t in re.findall(r"\w+", (s or "").lower()))


def _jaccard(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta and not tb:
        return 1.0
    return len(ta & tb) / len(ta | tb) if (ta | tb) else 0.0


def semantic_similarity(a: str, b: str) -> float:
    """Coseno semántico 0-1. Intenta MiniLM, si no TF-IDF, si no Jaccard."""
    global _model
    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity

        if _model is None:
            _model = SentenceTransformer(MODEL_ID)
        emb = _model.encode([a or "", b or ""])
        return float(cosine_similarity([emb[0]], [emb[1]])[0][0])
    except Exception:
        pass
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vec = TfidfVectorizer().fit_transform([_norm_es(a or ""), _norm_es(b or "")])
        return float(cosine_similarity(vec[0], vec[1])[0][0])
    except Exception:
        return _jaccard(a, b)
