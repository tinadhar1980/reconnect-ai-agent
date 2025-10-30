# Reconnect AI — FAISS-enabled 

This repository contains the FAISS-enabled Reconnect AI system.
It stores embeddings in Postgres (as JSON) and maintains a local FAISS index for similarity search.

## Quick start (Docker)

1. Build & run:
   
   docker-compose up --build
   

2. FastAPI: http://localhost:8000

3. Test flow:
   - POST /events/guest-checkout with header `X-API-KEY: our-secret-key`
   - GET /guest-profile/{guest_id} with `Authorization: Bearer <token>` after retrieving token at /token

## Notes
- Embeddings: sentence-transformers (all-MiniLM-L6-v2)
- Vector store: FAISS index saved/loaded from disk (faiss_index.bin) and a mapping file faiss_mapping.json
- Both embeddings are persisted in Postgres (Stay.embedding as JSON) and indexed in FAISS for retrieval.
