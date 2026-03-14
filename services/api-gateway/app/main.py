"""API Gateway - FastAPI application."""

import hmac
import logging
import os
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "service": "api-gateway", "message": "%(message)s"}',
)
logger = logging.getLogger(__name__)

AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL", "http://agent-service:8004")
API_KEY = os.getenv("API_KEY", "dev-secret-key")

app = FastAPI(title="API Gateway", version="1.0.0")

GATEWAY_REQUESTS = Counter("gateway_requests_total", "Total gateway requests")
GATEWAY_LATENCY = Histogram("gateway_latency_seconds", "Gateway request latency")


class QueryRequest(BaseModel):
    question: str
    mode: str = "hybrid"


def verify_api_key(x_api_key: Optional[str] = None) -> bool:
    """Simple API key authentication placeholder using constant-time comparison."""
    if not x_api_key:
        return False
    return hmac.compare_digest(x_api_key, API_KEY)


@app.get("/health")
def health():
    return {"status": "ok", "service": "api-gateway"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/query")
def query(
    request: QueryRequest,
    x_api_key: Optional[str] = Header(default=None),
):
    if not verify_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    GATEWAY_REQUESTS.inc()
    with GATEWAY_LATENCY.time():
        logger.info("Gateway query: %s", request.question)
        try:
            response = httpx.post(
                f"{AGENT_SERVICE_URL}/qa",
                json={"question": request.question, "mode": request.mode},
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("Agent service error: %s", exc)
            raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
        except Exception as exc:
            logger.error("Gateway error: %s", exc)
            raise HTTPException(status_code=503, detail="Agent service unavailable")
