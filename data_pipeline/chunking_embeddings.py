"""
Chunking and Embeddings Pipeline – Splits documents into chunks and generates embeddings.

Responsible for:
1. Splitting raw document text into overlapping chunks
2. Generating embeddings for each chunk
3. Storing chunks and embeddings in ChromaDB / FAISS
4. Persisting chunk metadata in PostgreSQL
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8005"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

DEFAULT_CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
DEFAULT_CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "64"))


@dataclass
class DocumentChunk:
    """A single chunk of a document with its embedding and metadata."""

    content: str
    filename: str
    source: str
    chunk_index: int
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


def split_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """
    Split text into overlapping chunks using a recursive character splitter.

    Args:
        text: Raw document text.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Number of overlapping characters between adjacent chunks.

    Returns:
        List of text chunk strings.
    """
    # In production: use LangChain's RecursiveCharacterTextSplitter
    # from langchain.text_splitter import RecursiveCharacterTextSplitter
    # splitter = RecursiveCharacterTextSplitter(
    #     chunk_size=chunk_size,
    #     chunk_overlap=chunk_overlap,
    #     separators=["\n\n", "\n", ".", " "]
    # )
    # return splitter.split_text(text)

    # Placeholder: simple fixed-size chunking
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of text strings.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors (list of floats).
    """
    if not texts:
        return []

    logger.info("Generating embeddings for %d chunks", len(texts))

    # In production:
    # from langchain_openai import OpenAIEmbeddings
    # embeddings_model = OpenAIEmbeddings(
    #     model=EMBEDDING_MODEL,
    #     api_key=OPENAI_API_KEY
    # )
    # return embeddings_model.embed_documents(texts)

    # Placeholder: return zero vectors
    return [[0.0] * 1536 for _ in texts]


def store_in_vectorstore(chunks: List[DocumentChunk], collection_name: str = "financial_docs") -> int:
    """
    Store document chunks and their embeddings in ChromaDB.

    Args:
        chunks: List of DocumentChunk objects with embeddings.
        collection_name: ChromaDB collection to store chunks in.

    Returns:
        Number of chunks stored.
    """
    if not chunks:
        return 0

    logger.info("Storing %d chunks in ChromaDB collection '%s'", len(chunks), collection_name)

    # In production:
    # import chromadb
    # client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    # collection = client.get_or_create_collection(collection_name)
    # collection.add(
    #     ids=[f"{c.filename}_{c.chunk_index}" for c in chunks],
    #     documents=[c.content for c in chunks],
    #     embeddings=[c.embedding for c in chunks],
    #     metadatas=[{**c.metadata, "source": c.source, "filename": c.filename} for c in chunks],
    # )

    return len(chunks)


def process_document(
    content: str,
    filename: str,
    source: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[DocumentChunk]:
    """
    Full pipeline: split a document into chunks and generate embeddings.

    Args:
        content: Raw document text.
        filename: Document filename.
        source: Document source path or URL.
        chunk_size: Target chunk size in characters.
        chunk_overlap: Overlap between adjacent chunks.

    Returns:
        List of DocumentChunk objects with embeddings.
    """
    logger.info("Processing document: %s (%d chars)", filename, len(content))

    # Step 1: Split text into chunks
    text_chunks = split_text(content, chunk_size, chunk_overlap)
    logger.info("Created %d chunks from %s", len(text_chunks), filename)

    # Step 2: Generate embeddings in batch
    embeddings = generate_embeddings(text_chunks)

    # Step 3: Build DocumentChunk objects
    chunks = [
        DocumentChunk(
            content=text,
            filename=filename,
            source=source,
            chunk_index=i,
            embedding=emb,
            metadata={"chunk_size": len(text)},
        )
        for i, (text, emb) in enumerate(zip(text_chunks, embeddings))
    ]

    return chunks


# ---------------------------------------------------------------------------
# Prefect tasks
# ---------------------------------------------------------------------------

try:
    from prefect import task  # type: ignore
    from data_pipeline.ingestion import Document  # type: ignore

    @task(name="chunk-and-embed")
    def chunk_and_embed_task(documents: List[Any]) -> List[DocumentChunk]:
        """Prefect task: chunk and embed a list of Document objects."""
        all_chunks: List[DocumentChunk] = []
        for doc in documents:
            chunks = process_document(doc.content, doc.filename, doc.source)
            all_chunks.extend(chunks)
        return all_chunks

    @task(name="store-embeddings")
    def store_embeddings_task(chunks: List[DocumentChunk]) -> int:
        """Prefect task: store chunks in ChromaDB."""
        return store_in_vectorstore(chunks)

except ImportError:
    logger.warning("Prefect not installed; task wrappers disabled.")


if __name__ == "__main__":
    sample_text = "This is a sample financial document about AML compliance. " * 20
    chunks = process_document(sample_text, "sample.txt", "/data/sample.txt")
    stored = store_in_vectorstore(chunks)
    print(f"Processed {len(chunks)} chunks, stored {stored}")
