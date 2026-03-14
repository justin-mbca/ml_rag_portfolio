"""Ingestion Service - FastAPI application."""

import logging
import os
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from pipeline import ingest_folder

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "service": "ingestion-service", "message": "%(message)s"}',
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Ingestion Service", version="1.0.0")

INGEST_REQUESTS = Counter("ingestion_requests_total", "Total ingest requests")
INGEST_LATENCY = Histogram("ingestion_latency_seconds", "Ingest latency")


class IngestRequest(BaseModel):
    folder_path: str


class IngestResponse(BaseModel):
    status: str
    files_ingested: int
    total_chunks: int


@app.get("/health")
def health():
    return {"status": "ok", "service": "ingestion-service"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest):
    INGEST_REQUESTS.inc()
    with INGEST_LATENCY.time():
        logger.info("Ingest request for folder: %s", request.folder_path)
        result = ingest_folder(request.folder_path)
    return IngestResponse(
        status="success",
        files_ingested=result["files_ingested"],
        total_chunks=result["total_chunks"],
    )
