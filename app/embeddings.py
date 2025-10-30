import os
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def embed_text(text: str) -> np.ndarray:
    model = get_model()
    vec = model.encode([text], normalize_embeddings=True)
    return vec[0]

def to_list(vec):
    return vec.tolist()

def from_list(lst):
    return np.array(lst).astype(float)

def cosine_similarity(a, b):
    a = np.array(a).astype(float)
    b = np.array(b).astype(float)
    if a.size == 0 or b.size == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
