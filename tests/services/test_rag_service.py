"""
Tests for the RAG Service.
"""

import importlib.util
import os
import sys

import pytest
from fastapi.testclient import TestClient

# Load the rag-service app module directly to avoid sys.path conflicts
_rag_service_dir = os.path.join(os.path.dirname(__file__), "..", "..", "services", "rag-service")
_spec = importlib.util.spec_from_file_location("rag_service_app", os.path.join(_rag_service_dir, "app.py"))
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

app = _module.app
QueryRequest = _module.QueryRequest
RetrievalMethod = _module.RetrievalMethod

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "rag-service"


def test_query_vector_retrieval():
    response = client.post(
        "/query",
        json={
            "question": "What are the AML compliance requirements?",
            "retrieval_method": "vector",
            "top_k": 3,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert data["retrieval_method"] == "vector"
    assert isinstance(data["latency_ms"], int)


def test_query_graph_retrieval():
    response = client.post(
        "/query",
        json={
            "question": "What regulations relate to Basel III?",
            "retrieval_method": "graph",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["retrieval_method"] == "graph"


def test_query_hybrid_retrieval():
    response = client.post(
        "/query",
        json={
            "question": "Explain the capital conservation buffer requirements.",
            "retrieval_method": "hybrid",
            "top_k": 5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["retrieval_method"] == "hybrid"
    assert len(data["sources"]) > 0


def test_query_invalid_retrieval_method():
    response = client.post(
        "/query",
        json={
            "question": "Test question",
            "retrieval_method": "invalid_method",
        },
    )
    assert response.status_code == 422


def test_query_top_k_bounds():
    # top_k must be between 1 and 20
    response = client.post(
        "/query",
        json={"question": "Test", "top_k": 0},
    )
    assert response.status_code == 422

    response = client.post(
        "/query",
        json={"question": "Test", "top_k": 21},
    )
    assert response.status_code == 422


def test_query_missing_question():
    response = client.post("/query", json={"retrieval_method": "vector"})
    assert response.status_code == 422
