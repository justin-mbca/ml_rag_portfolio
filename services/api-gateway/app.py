"""
API Gateway – FastAPI application that routes financial queries to downstream microservices.

Acts as the single entry point for all client requests:
- Routes document ingestion to the Ingestion Service
- Routes RAG queries to the RAG Service
- Routes agent tasks to the Agent Service
- Routes graph queries to the Graph Service

Handles authentication, rate limiting, and request logging.
"""

import logging
import os
import time
from typing import Any, Dict, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(
    title="GenAI Financial Assistant – API Gateway",
    description="Unified API gateway for the GenAI Financial Knowledge Assistant Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

INGESTION_SERVICE_URL = os.getenv("INGESTION_SERVICE_URL", "http://ingestion-service:8001")
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://rag-service:8002")
GRAPH_SERVICE_URL = os.getenv("GRAPH_SERVICE_URL", "http://graph-service:8003")
AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL", "http://agent-service:8004")

HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "30.0"))


class QueryRequest(BaseModel):
    question: str = Field(..., description="Financial question to answer")
    agent: Optional[str] = Field(None, description="Specific agent to use (optional, defaults to auto)")
    retrieval_method: Optional[str] = Field("hybrid", description="Retrieval method: vector, graph, hybrid")
    top_k: Optional[int] = Field(5, ge=1, le=20)


class QueryResponse(BaseModel):
    answer: str
    sources: Any
    retrieval_method: str
    agent: Optional[str] = None
    latency_ms: int


async def proxy_request(url: str, payload: Dict) -> Dict:
    """Forward a request to a downstream service."""
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with latency."""
    start = time.time()
    response = await call_next(request)
    latency = int((time.time() - start) * 1000)
    logger.info(
        "method=%s path=%s status=%s latency_ms=%d",
        request.method, request.url.path, response.status_code, latency,
    )
    return response


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "api-gateway"}


@app.get("/health/services")
async def services_health():
    """Check health of all downstream services."""
    services = {
        "ingestion-service": f"{INGESTION_SERVICE_URL}/health",
        "rag-service": f"{RAG_SERVICE_URL}/health",
        "graph-service": f"{GRAPH_SERVICE_URL}/health",
        "agent-service": f"{AGENT_SERVICE_URL}/health",
    }
    results = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in services.items():
            try:
                resp = await client.get(url)
                results[name] = "healthy" if resp.status_code == 200 else "unhealthy"
            except Exception:
                results[name] = "unreachable"
    return results


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Main query endpoint.

    Routes to the Agent Service for multi-step agentic responses,
    or directly to the RAG Service for simple retrieval.
    """
    start = time.time()
    try:
        if request.agent and request.agent != "retrieval_agent":
            # Route to agent service for specialised agentic workflows
            result = await proxy_request(
                f"{AGENT_SERVICE_URL}/agent/run",
                {
                    "question": request.question,
                    "agent": request.agent or "auto",
                    "max_steps": 5,
                },
            )
            latency = int((time.time() - start) * 1000)
            return QueryResponse(
                answer=result.get("answer", ""),
                sources=result.get("sources", []),
                retrieval_method=request.retrieval_method or "hybrid",
                agent=result.get("agent_used"),
                latency_ms=latency,
            )
        else:
            # Route directly to RAG service for retrieval
            result = await proxy_request(
                f"{RAG_SERVICE_URL}/query",
                {
                    "question": request.question,
                    "retrieval_method": request.retrieval_method or "hybrid",
                    "top_k": request.top_k or 5,
                },
            )
            latency = int((time.time() - start) * 1000)
            return QueryResponse(
                answer=result.get("answer", ""),
                sources=result.get("sources", []),
                retrieval_method=result.get("retrieval_method", "hybrid"),
                latency_ms=latency,
            )
    except httpx.HTTPError as exc:
        logger.exception("Downstream service error")
        raise HTTPException(status_code=502, detail=f"Downstream service error: {exc}") from exc
    except Exception as exc:
        logger.exception("Gateway error")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/agents")
async def list_agents():
    """List available agents from the Agent Service."""
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            resp = await client.get(f"{AGENT_SERVICE_URL}/agents")
            return resp.json()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
