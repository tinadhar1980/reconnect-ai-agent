import os, json
import numpy as np
import faiss

INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "/app/faiss_index.bin")
MAPPING_PATH = os.getenv("FAISS_MAPPING_PATH", "/app/faiss_mapping.json")
_dim = int(os.getenv("EMBED_DIM", "384"))

class FaissIndex:
    def __init__(self, dim=_dim):
        self.dim = dim
        self.index = faiss.IndexFlatIP(self.dim)
        self.mapping = []

    def add(self, vecs, stay_ids):
        if vecs is None or len(vecs) == 0:
            return
        if vecs.ndim == 1:
            vecs = vecs.reshape(1, -1)
        faiss.normalize_L2(vecs)
        self.index.add(vecs.astype('float32'))
        self.mapping.extend(stay_ids)
        self._save()

    def search(self, query_vec, k=5):
        if self.index.ntotal == 0:
            return []
        q = np.array(query_vec).astype('float32').reshape(1, -1)
        faiss.normalize_L2(q)
        D, I = self.index.search(q, k)
        results = []
        for dist, idx in zip(D[0], I[0]):
            if idx < 0 or idx >= len(self.mapping):
                continue
            results.append({"stay_id": self.mapping[idx], "score": float(dist)})
        return results

    def _save(self):
        try:
            faiss.write_index(self.index, INDEX_PATH)
            with open(MAPPING_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.mapping, f)
        except Exception as e:
            print("Failed to save FAISS index:", e)

    def load(self):
        try:
            if os.path.exists(INDEX_PATH) and os.path.exists(MAPPING_PATH):
                self.index = faiss.read_index(INDEX_PATH)
                with open(MAPPING_PATH, 'r', encoding='utf-8') as f:
                    self.mapping = json.load(f)
        except Exception as e:
            print("Failed to load FAISS index:", e)

_global_index = None
def get_faiss_index():
    global _global_index
    if _global_index is None:
        _global_index = FaissIndex()
        _global_index.load()
    return _global_index
