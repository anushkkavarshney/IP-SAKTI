"""
FastAPI entrypoint for Member 2's backend.

Run from the REPO ROOT (not from inside /backend), e.g.:
    uvicorn backend.app.main:app --reload --port 8000

This matters because Member 4's LegalSearchEngine defaults to the
relative path "rag_engine/processed_data/corpus.json" -- if you run
uvicorn from inside /backend, that relative path won't resolve.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import analyze, clarify, report

app = FastAPI(
    title="IP-SAKTI Navigator Backend",
    description="Member 2 (Backend + Integration) -- orchestrates clarification, classification, RAG, and verification.",
    version="0.1.0",
)

# Parse environment-driven CORS origins, defaulting to http://localhost:3000.
cors_origins_raw = os.environ.get("CORS_ORIGINS", "")
allow_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]
if not allow_origins:
    allow_origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clarify.router)
app.include_router(analyze.router)
app.include_router(report.router)


@app.get("/")
def read_root():
    return {"status": "online", "message": "IP-SAKTI Navigator backend is running."}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
