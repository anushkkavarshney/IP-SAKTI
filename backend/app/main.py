"""
FastAPI entrypoint for Member 2's backend.

Run from the REPO ROOT (not from inside /backend), e.g.:
    uvicorn backend.app.main:app --reload --port 8000

This matters because Member 4's LegalSearchEngine defaults to the
relative path "rag_engine/processed_data/corpus.json" -- if you run
uvicorn from inside /backend, that relative path won't resolve.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import analyze, clarify, report

app = FastAPI(
    title="IP-SAKTI Navigator Backend",
    description="Member 2 (Backend + Integration) -- orchestrates clarification, classification, RAG, and verification.",
    version="0.1.0",
)

# Frontend runs on localhost:3000 by default (Next.js).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clarify.router)
app.include_router(analyze.router)
app.include_router(report.router)


@app.get("/")
def read_root():
    return {"status": "online", "message": "IP-SAKTI Navigator backend is running."}
