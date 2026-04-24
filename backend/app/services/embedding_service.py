"""
Embedding service using sentence-transformers (all-MiniLM-L6-v2).

The model is loaded once at module level (singleton) so it is shared
across all Celery workers in the same process — avoids repeated 80MB loads.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

# Lazy-load to avoid import time cost outside Celery workers
_model = None

MODEL_NAME = "all-MiniLM-L6-v2"


def _get_model():
    """Return the globally cached SentenceTransformer model."""
    global _model
    if _model is None:
        # Import here so the FastAPI process doesn't load a 80 MB model on startup
        from sentence_transformers import SentenceTransformer  # type: ignore
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed(text: str) -> list[float]:
    """
    Embed a single string and return a 384-dimensional float list
    suitable for storing in a pgvector `Vector(384)` column.
    """
    model = _get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed a batch of strings — more efficient than calling embed() in a loop."""
    model = _get_model()
    vectors = model.encode(texts, normalize_embeddings=True, batch_size=32)
    return [v.tolist() for v in vectors]
