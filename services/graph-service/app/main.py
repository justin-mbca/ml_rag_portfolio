"""Graph Service - FastAPI application."""

import logging
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from graph_builder import Neo4jClient, build_graph_from_text

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "service": "graph-service", "message": "%(message)s"}',
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Graph Service", version="1.0.0")

GRAPH_INGEST_REQUESTS = Counter("graph_ingest_requests_total", "Total graph ingest requests")
GRAPH_INGEST_LATENCY = Histogram("graph_ingest_latency_seconds", "Graph ingest latency")

_neo4j_client: Neo4jClient = None


def get_neo4j_client() -> Neo4jClient:
    global _neo4j_client
    if _neo4j_client is None:
        _neo4j_client = Neo4jClient()
    return _neo4j_client


class GraphIngestRequest(BaseModel):
    text: str
    doc_id: str
    source: str = "unknown"


class GraphIngestResponse(BaseModel):
    status: str
    entities_extracted: int
    doc_id: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "graph-service"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/ingest", response_model=GraphIngestResponse)
def ingest(request: GraphIngestRequest):
    GRAPH_INGEST_REQUESTS.inc()
    with GRAPH_INGEST_LATENCY.time():
        logger.info("Graph ingest for doc_id: %s", request.doc_id)
        try:
            client = get_neo4j_client()
            result = build_graph_from_text(
                text=request.text,
                doc_id=request.doc_id,
                source=request.source,
                client=client,
            )
        except Exception as exc:
            logger.error("Graph ingest failed: %s", exc)
            raise HTTPException(status_code=500, detail=str(exc))
    return GraphIngestResponse(
        status="success",
        entities_extracted=result["entities_extracted"],
        doc_id=result["doc_id"],
    )
