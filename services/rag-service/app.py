"""
RAG Service – FastAPI application for hybrid VectorRAG and GraphRAG retrieval.

Accepts a user query and returns the most relevant document chunks
using a combination of vector similarity search (ChromaDB / FAISS)
and graph-based retrieval (Neo4j).
"""

import logging
import os
from enum import Enum
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(
    title="RAG Service",
    description="Hybrid VectorRAG + GraphRAG retrieval for financial documents",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8005"))
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


class RetrievalMethod(str, Enum):
    vector = "vector"
    graph = "graph"
    hybrid = "hybrid"


class QueryRequest(BaseModel):
    question: str = Field(..., description="The user's financial question")
    retrieval_method: RetrievalMethod = RetrievalMethod.hybrid
    top_k: int = Field(default=5, ge=1, le=20, description="Number of document chunks to retrieve")
    filter_category: Optional[str] = Field(None, description="Filter documents by category (e.g. 'AML', 'Basel')")


class DocumentChunk(BaseModel):
    filename: str
    page: Optional[int] = None
    content: str
    relevance_score: float


class QueryResponse(BaseModel):
    answer: str
    sources: List[DocumentChunk]
    retrieval_method: str
    latency_ms: int


def vector_search(query: str, top_k: int, category: Optional[str]) -> List[DocumentChunk]:
    """Perform vector similarity search using ChromaDB."""
    # In production: connect to ChromaDB and run similarity_search()
    # from langchain_community.vectorstores import Chroma
    # vectorstore = Chroma(host=CHROMA_HOST, port=CHROMA_PORT, ...)
    # results = vectorstore.similarity_search_with_score(query, k=top_k)
    return [
        DocumentChunk(
            filename="AML_Policy_2024.pdf",
            page=3,
            content=f"Placeholder vector result for: {query}",
            relevance_score=0.94,
        )
    ]


def graph_search(query: str, top_k: int) -> List[DocumentChunk]:
    """Perform graph traversal search using Neo4j."""
    # In production: query Neo4j with Cypher
    # from neo4j import GraphDatabase
    # driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    # results = driver.session().run("MATCH (n:Document)-[:RELATES_TO]->... RETURN n")
    return [
        DocumentChunk(
            filename="Regulatory_Knowledge_Graph",
            page=None,
            content=f"Placeholder graph result for: {query}",
            relevance_score=0.88,
        )
    ]


def generate_answer(query: str, chunks: List[DocumentChunk]) -> str:
    """Generate a final answer using an LLM over retrieved chunks."""
    # In production:
    # from langchain_openai import ChatOpenAI
    # from langchain.chains import RetrievalQA
    context = "\n".join(c.content for c in chunks)
    return f"Based on the retrieved documents: {context[:200]}..."


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "rag-service"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    """
    Perform hybrid RAG retrieval and answer generation.

    Combines vector similarity search with graph-based retrieval
    to produce a grounded, cited answer.
    """
    import time
    start = time.time()

    try:
        chunks: List[DocumentChunk] = []

        if request.retrieval_method in (RetrievalMethod.vector, RetrievalMethod.hybrid):
            chunks.extend(vector_search(request.question, request.top_k, request.filter_category))

        if request.retrieval_method in (RetrievalMethod.graph, RetrievalMethod.hybrid):
            chunks.extend(graph_search(request.question, request.top_k))

        if not chunks:
            raise HTTPException(status_code=404, detail="No relevant documents found.")

        answer = generate_answer(request.question, chunks)
        latency = int((time.time() - start) * 1000)

        return QueryResponse(
            answer=answer,
            sources=chunks,
            retrieval_method=request.retrieval_method.value,
            latency_ms=latency,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Query failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
