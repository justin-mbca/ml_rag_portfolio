"""RAG Service - FastAPI application."""

import logging

from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from typing import List, Dict, Any

from retrieval import hybrid_retrieve, vector_search, graph_hint_search

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "service": "rag-service", "message": "%(message)s"}',
)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Service", version="1.0.0")

RETRIEVE_REQUESTS = Counter("rag_retrieve_requests_total", "Total retrieve requests")
RETRIEVE_LATENCY = Histogram("rag_retrieve_latency_seconds", "Retrieve latency")


class RetrieveRequest(BaseModel):
    query: str
    mode: str = "hybrid"
    top_k: int = 5


class RetrieveResponse(BaseModel):
    results: List[Dict[str, Any]]
    mode: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "rag-service"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/retrieve", response_model=RetrieveResponse)
def retrieve(request: RetrieveRequest):
    RETRIEVE_REQUESTS.inc()
    with RETRIEVE_LATENCY.time():
        logger.info("Retrieve request: mode=%s query=%s", request.mode, request.query)
        if request.mode == "vector":
            results = vector_search(request.query, request.top_k)
        elif request.mode == "graph":
            results = graph_hint_search(request.query, request.top_k)
        else:
            results = hybrid_retrieve(request.query, request.top_k)
    return RetrieveResponse(results=results, mode=request.mode)
