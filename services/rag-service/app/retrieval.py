"""RAG retrieval: vector search, graph hint search, and hybrid retrieval."""

import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

CHROMA_HOST = os.getenv("CHROMA_HOST", "chroma")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "financial_docs")
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "changeme")

TOP_K = int(os.getenv("TOP_K", "5"))

_model = None
_chroma_client = None
_neo4j_driver = None


def get_model() -> "SentenceTransformer":
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def get_chroma_collection():
    global _chroma_client
    if _chroma_client is None:
        import chromadb
        _chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    return _chroma_client.get_or_create_collection(COLLECTION_NAME)


def get_neo4j_driver():
    global _neo4j_driver
    if _neo4j_driver is None:
        from neo4j import GraphDatabase
        _neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return _neo4j_driver


def vector_search(query: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
    """Search ChromaDB by embedding similarity."""
    model = get_model()
    collection = get_chroma_collection()
    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    hits = []
    if results and results.get("documents"):
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            hits.append({"text": doc, "metadata": meta, "score": 1 - dist, "source": "vector"})
    return hits


def graph_hint_search(query: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
    """Search Neo4j for entities mentioned in the query."""
    try:
        driver = get_neo4j_driver()
        words = [w.strip(".,;:!?") for w in query.split() if len(w) > 3]
        hits = []
        with driver.session() as session:
            for word in words[:5]:
                result = session.run(
                    "MATCH (e:Entity) WHERE toLower(e.name) CONTAINS toLower($word) "
                    "MATCH (e)-[:MENTIONED_IN]->(d:Document) "
                    "RETURN d.text AS text, d.source AS source LIMIT $limit",
                    word=word,
                    limit=top_k,
                )
                for record in result:
                    hits.append({
                        "text": record["text"],
                        "metadata": {"source": record["source"]},
                        "score": 0.5 + (1.0 / (1 + len(hits))),
                        "source": "graph",
                    })
        return hits[:top_k]
    except Exception as exc:
        logger.warning("Graph search failed (Neo4j unavailable?): %s", exc)
        return []


def hybrid_retrieve(query: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
    """Combine vector and graph results, deduplicate, and return top_k."""
    vector_hits = vector_search(query, top_k)
    graph_hits = graph_hint_search(query, top_k)

    seen_texts = set()
    combined = []
    for hit in vector_hits + graph_hits:
        import hashlib
        key = hashlib.md5(hit["text"].encode("utf-8", errors="replace")).hexdigest()
        if key not in seen_texts:
            seen_texts.add(key)
            combined.append(hit)

    combined.sort(key=lambda x: x.get("score", 0), reverse=True)
    return combined[:top_k]
