"""
FastAPI Server Entrypoint for IP-SAKTI.
Serves legal reasoning payloads over REST API endpoints.
"""

import sys
import os
from fastapi import FastAPI, HTTPException

# Ensure root directory is accessible in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.schemas import AnalysisRequest, AnalysisResponse
from llm_pipeline.generator import LegalReasoningPipeline
from llm_pipeline.guardrails import validate_prompt_input, verify_grounding

app = FastAPI(
    title="IP-SAKTI API",
    description="AI Legal Reasoning Engine for Indian IP Law and ABS Compliance",
    version="1.0.0"
)

# Initialize legal reasoning pipeline
pipeline = LegalReasoningPipeline()


@app.get("/")
def read_root():
    return {"status": "online", "message": "IP-SAKTI API Backend is operational."}


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
def analyze_claim(request: AnalysisRequest):
    # Validate input query
    validation = validate_prompt_input(request.query, [])
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["reason"])

    # Generate prompt payload from RAG pipeline
    payload = pipeline.generate_prompt_payload(request.query, top_k=request.top_k)
    raw_evidence = payload.get("raw_evidence", [])

    # Run guardrail verification
    guardrail_result = verify_grounding(payload["user_prompt"], raw_evidence)

    return AnalysisResponse(
        status="success",
        query=request.query,
        matched_entities=payload["rag_metadata"]["matched_entities"],
        system_prompt=payload["system_prompt"],
        user_prompt=payload["user_prompt"],
        evidence=raw_evidence,
        guardrail_check=guardrail_result
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=False)