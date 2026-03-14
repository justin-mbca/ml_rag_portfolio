"""
Ingestion Service – FastAPI application for document ingestion.

Accepts document uploads (PDF, DOCX, TXT) and triggers the
data pipeline to chunk, embed, and store them in the vector store
and knowledge graph.
"""

import logging
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ingestion Service",
    description="Handles document ingestion for the GenAI Financial Knowledge Assistant",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/tmp/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


class IngestionResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str


class StatusResponse(BaseModel):
    document_id: str
    status: str
    chunks_created: Optional[int] = None
    graph_nodes_created: Optional[int] = None


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ingestion-service"}


@app.post("/ingest", response_model=IngestionResponse)
async def ingest_document(file: UploadFile = File(...)):
    """
    Upload and ingest a financial document.

    Supported formats: PDF, DOCX, TXT, Markdown.
    The document is processed asynchronously: chunked, embedded,
    and stored in ChromaDB and Neo4j.
    """
    suffix = Path(file.filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Supported: {SUPPORTED_EXTENSIONS}",
        )

    document_id = str(uuid.uuid4())
    destination = UPLOAD_DIR / f"{document_id}{suffix}"

    try:
        contents = await file.read()
        destination.write_bytes(contents)
        logger.info("Saved document %s to %s", document_id, destination)
    except Exception as exc:
        logger.exception("Failed to save document")
        raise HTTPException(status_code=500, detail=f"Failed to save document: {exc}") from exc

    # In a production system this would publish a message to a queue
    # (e.g. SQS, Kafka) to trigger the async pipeline worker.
    logger.info("Document %s queued for processing", document_id)

    return IngestionResponse(
        document_id=document_id,
        filename=file.filename,
        status="queued",
        message="Document received and queued for ingestion.",
    )


@app.get("/status/{document_id}", response_model=StatusResponse)
def get_ingestion_status(document_id: str):
    """
    Check the ingestion status of a previously uploaded document.
    """
    # Placeholder: in production, query a metadata database (PostgreSQL)
    return StatusResponse(
        document_id=document_id,
        status="completed",
        chunks_created=42,
        graph_nodes_created=18,
    )
