"""Unit tests for RAG retrieval logic (mocked dependencies)."""

import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "../../services/rag-service/app"),
)


def test_hybrid_retrieve_combines_results():
    """Test that hybrid_retrieve combines vector and graph results."""
    import retrieval

    mock_vector_results = [
        {"text": "AML compliance requires KYC procedures.", "metadata": {"source": "aml.txt"}, "score": 0.9, "source": "vector"},
        {"text": "Risk assessment must be documented.", "metadata": {"source": "risk.txt"}, "score": 0.8, "source": "vector"},
    ]
    mock_graph_results = [
        {"text": "FinCEN regulations apply to all banks.", "metadata": {"source": "fincen.txt"}, "score": 0.7, "source": "graph"},
    ]

    with patch.object(retrieval, "vector_search", return_value=mock_vector_results), \
         patch.object(retrieval, "graph_hint_search", return_value=mock_graph_results):
        results = retrieval.hybrid_retrieve("AML compliance", top_k=5)

    assert len(results) == 3
    sources = [r["source"] for r in results]
    assert "vector" in sources
    assert "graph" in sources


def test_hybrid_retrieve_deduplicates():
    """Test that hybrid_retrieve removes duplicate text entries."""
    import retrieval

    duplicate_result = {"text": "Same text content here.", "metadata": {}, "score": 0.8, "source": "vector"}
    mock_vector = [duplicate_result]
    mock_graph = [{"text": "Same text content here.", "metadata": {}, "score": 0.7, "source": "graph"}]

    with patch.object(retrieval, "vector_search", return_value=mock_vector), \
         patch.object(retrieval, "graph_hint_search", return_value=mock_graph):
        results = retrieval.hybrid_retrieve("test query", top_k=5)

    assert len(results) == 1


def test_hybrid_retrieve_sorted_by_score():
    """Test that results are sorted by score descending."""
    import retrieval

    mock_results = [
        {"text": "Low score doc.", "metadata": {}, "score": 0.3, "source": "vector"},
        {"text": "High score doc.", "metadata": {}, "score": 0.95, "source": "vector"},
        {"text": "Mid score doc.", "metadata": {}, "score": 0.6, "source": "graph"},
    ]

    with patch.object(retrieval, "vector_search", return_value=mock_results[:2]), \
         patch.object(retrieval, "graph_hint_search", return_value=mock_results[2:]):
        results = retrieval.hybrid_retrieve("query", top_k=5)

    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_graph_hint_search_handles_neo4j_failure():
    """Test that graph_hint_search returns empty list if Neo4j is unavailable."""
    import retrieval

    with patch.object(retrieval, "get_neo4j_driver", side_effect=Exception("Neo4j unavailable")):
        results = retrieval.graph_hint_search("AML regulations")

    assert results == []
