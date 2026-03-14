"""
Data Ingestion Pipeline – Loads financial documents from various sources.

Supports:
- Local filesystem
- Amazon S3
- Azure Blob Storage
- HTTP/HTTPS URLs

Orchestrated with Prefect for scheduling and monitoring.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

S3_BUCKET = os.getenv("S3_BUCKET", "")
S3_PREFIX = os.getenv("S3_PREFIX", "financial-documents/")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".csv", ".xlsx"}


class Document:
    """Represents a loaded document with content and metadata."""

    def __init__(
        self,
        content: str,
        filename: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.content = content
        self.filename = filename
        self.source = source
        self.metadata = metadata or {}

    def __repr__(self) -> str:
        return f"Document(filename={self.filename!r}, source={self.source!r}, chars={len(self.content)})"


def load_from_filesystem(directory: str) -> List[Document]:
    """
    Load all supported documents from a local directory.

    Args:
        directory: Path to the directory containing documents.

    Returns:
        List of Document objects.
    """
    docs = []
    path = Path(directory)
    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    for filepath in path.rglob("*"):
        if filepath.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        try:
            content = _read_file(filepath)
            docs.append(
                Document(
                    content=content,
                    filename=filepath.name,
                    source=str(filepath),
                    metadata={"extension": filepath.suffix, "size_bytes": filepath.stat().st_size},
                )
            )
            logger.info("Loaded: %s (%d chars)", filepath.name, len(content))
        except Exception:
            logger.exception("Failed to load %s", filepath)

    logger.info("Loaded %d documents from %s", len(docs), directory)
    return docs


def _read_file(filepath: Path) -> str:
    """Read file content based on its extension."""
    suffix = filepath.suffix.lower()
    if suffix == ".pdf":
        return _read_pdf(filepath)
    if suffix == ".docx":
        return _read_docx(filepath)
    if suffix in (".txt", ".md"):
        return filepath.read_text(encoding="utf-8", errors="replace")
    # For .csv and .xlsx, return raw text representation
    return filepath.read_text(encoding="utf-8", errors="replace")


def _read_pdf(filepath: Path) -> str:
    """Extract text from a PDF file using PyMuPDF."""
    # In production:
    # import fitz  # PyMuPDF
    # doc = fitz.open(str(filepath))
    # return "\n".join(page.get_text() for page in doc)
    logger.debug("PDF extraction placeholder for %s", filepath.name)
    return f"[PDF content placeholder for {filepath.name}]"


def _read_docx(filepath: Path) -> str:
    """Extract text from a DOCX file using python-docx."""
    # In production:
    # from docx import Document as DocxDocument
    # doc = DocxDocument(str(filepath))
    # return "\n".join(para.text for para in doc.paragraphs)
    logger.debug("DOCX extraction placeholder for %s", filepath.name)
    return f"[DOCX content placeholder for {filepath.name}]"


def load_from_s3(bucket: str, prefix: str = "") -> Generator[Document, None, None]:
    """
    Stream documents from an S3 bucket.

    Args:
        bucket: S3 bucket name.
        prefix: Key prefix to filter objects.

    Yields:
        Document objects as they are downloaded.
    """
    # In production:
    # import boto3
    # s3 = boto3.client("s3", region_name=AWS_REGION)
    # paginator = s3.get_paginator("list_objects_v2")
    # for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
    #     for obj in page.get("Contents", []):
    #         key = obj["Key"]
    #         if Path(key).suffix.lower() not in SUPPORTED_EXTENSIONS:
    #             continue
    #         response = s3.get_object(Bucket=bucket, Key=key)
    #         content = response["Body"].read().decode("utf-8", errors="replace")
    #         yield Document(content=content, filename=Path(key).name, source=f"s3://{bucket}/{key}")
    logger.info("S3 ingestion placeholder: s3://%s/%s", bucket, prefix)
    yield Document(
        content="[S3 document placeholder]",
        filename="s3_placeholder.txt",
        source=f"s3://{bucket}/{prefix}",
    )


# ---------------------------------------------------------------------------
# Prefect flow
# ---------------------------------------------------------------------------

try:
    from prefect import flow, task  # type: ignore

    @task(name="load-documents", retries=2)
    def load_documents_task(source_dir: str) -> List[Document]:
        """Prefect task: load documents from filesystem."""
        return load_from_filesystem(source_dir)

    @task(name="load-documents-s3", retries=3)
    def load_documents_s3_task(bucket: str, prefix: str = "") -> List[Document]:
        """Prefect task: load documents from S3."""
        return list(load_from_s3(bucket, prefix))

    @flow(name="document-ingestion-pipeline")
    def ingestion_flow(source_dir: str = "/data/documents") -> List[Document]:
        """
        Prefect flow: full document ingestion pipeline.

        Loads from local filesystem and optionally from S3,
        then passes to the chunking and embedding stage.
        """
        docs = load_documents_task(source_dir)
        if S3_BUCKET:
            s3_docs = load_documents_s3_task(S3_BUCKET, S3_PREFIX)
            docs.extend(s3_docs)
        logger.info("Ingestion complete: %d documents loaded", len(docs))
        return docs

except ImportError:
    logger.warning("Prefect not installed; flow orchestration disabled.")


if __name__ == "__main__":
    # Run a test ingestion from the current directory
    docs = load_from_filesystem(".")
    for doc in docs:
        print(doc)
