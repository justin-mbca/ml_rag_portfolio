"""Ingestion pipeline: chunking, embedding, and indexing documents."""

import os
import logging
from typing import List

logger = logging.getLogger(__name__)

CHROMA_HOST = os.getenv("CHROMA_HOST", "chroma")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "financial_docs")
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

_model = None
_client = None


def get_model() -> "SentenceTransformer":
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading embedding model: %s", EMBED_MODEL)
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def get_chroma_client() -> "chromadb.HttpClient":
    global _client
    if _client is None:
        import chromadb
        logger.info("Connecting to ChromaDB at %s:%s", CHROMA_HOST, CHROMA_PORT)
        _client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    return _client


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == len(words):
            break
        start += chunk_size - overlap
    return chunks


def ingest_folder(folder_path: str) -> dict:
    """Walk a folder and ingest .txt and .md files into ChromaDB."""
    model = get_model()
    client = get_chroma_client()
    collection = client.get_or_create_collection(COLLECTION_NAME)

    ingested = 0
    total_chunks = 0

    for root, _dirs, files in os.walk(folder_path):
        for fname in files:
            if not fname.endswith((".txt", ".md")):
                continue
            fpath = os.path.join(root, fname)
            logger.info("Ingesting file: %s", fpath)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            chunks = chunk_text(text)
            if not chunks:
                continue

            embeddings = model.encode(chunks).tolist()
            ids = [f"{fname}::{i}" for i in range(len(chunks))]
            metadatas = [{"source": fpath, "chunk_index": i} for i in range(len(chunks))]

            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
            )
            ingested += 1
            total_chunks += len(chunks)
            logger.info("Indexed %d chunks from %s", len(chunks), fname)

    return {"files_ingested": ingested, "total_chunks": total_chunks}
