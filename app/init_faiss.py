
from .db import SessionLocal
from .models import Stay
from .faiss_index import get_faiss_index
import json, numpy as np

def rebuild_index():
    db = SessionLocal()
    try:
        stays = db.query(Stay).filter(Stay.embedding != None).all()
        vecs = []
        ids = []
        for s in stays:
            try:
                arr = json.loads(s.embedding)
                vecs.append(np.array(arr).astype('float32'))
                ids.append(s.stay_id)
            except Exception as e:
                print('bad embedding for', s.stay_id, e)
        if len(vecs) == 0:
            print('no embeddings to index')
            return
        vecs_np = np.vstack(vecs)
        idx = get_faiss_index()
        idx.add(vecs_np, ids)
        print('FAISS rebuild complete. total indexed:', idx.index.ntotal)
    finally:
        db.close()

if __name__ == '__main__':
    rebuild_index()
