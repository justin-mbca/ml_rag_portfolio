"""
Integration tests for the GenAI Financial Knowledge Assistant Platform.

These tests require all services to be running (via docker compose).
Run with: pytest tests/integration/ -v

Set INTEGRATION_TEST=true to enable these tests.
"""

import os
import pytest
import httpx

INTEGRATION_TEST = os.getenv("INTEGRATION_TEST", "false").lower() == "true"
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
INGESTION_URL = os.getenv("INGESTION_URL", "http://localhost:8001")
RAG_URL = os.getenv("RAG_URL", "http://localhost:8002")
AGENT_URL = os.getenv("AGENT_URL", "http://localhost:8004")
API_KEY = os.getenv("API_KEY", "dev-secret-key")


@pytest.mark.skipif(not INTEGRATION_TEST, reason="Integration tests disabled (set INTEGRATION_TEST=true)")
class TestHealthEndpoints:
    def test_api_gateway_health(self):
        response = httpx.get(f"{API_GATEWAY_URL}/health", timeout=10)
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_ingestion_service_health(self):
        response = httpx.get(f"{INGESTION_URL}/health", timeout=10)
        assert response.status_code == 200

    def test_rag_service_health(self):
        response = httpx.get(f"{RAG_URL}/health", timeout=10)
        assert response.status_code == 200

    def test_agent_service_health(self):
        response = httpx.get(f"{AGENT_URL}/health", timeout=10)
        assert response.status_code == 200


@pytest.mark.skipif(not INTEGRATION_TEST, reason="Integration tests disabled (set INTEGRATION_TEST=true)")
class TestAPIGateway:
    def test_query_requires_auth(self):
        response = httpx.post(
            f"{API_GATEWAY_URL}/query",
            json={"question": "What are AML requirements?"},
            timeout=30,
        )
        assert response.status_code == 401

    def test_query_with_valid_key(self):
        response = httpx.post(
            f"{API_GATEWAY_URL}/query",
            json={"question": "What are AML compliance requirements?"},
            headers={"X-API-Key": API_KEY},
            timeout=60,
        )
        assert response.status_code == 200
        data = response.json()
        assert "question" in data
        assert "answer" in data
        assert len(data["answer"]) > 0
        assert "risk_analysis" in data
        risk = data["risk_analysis"]
        assert "risk_level" in risk
        assert "score" in risk


@pytest.mark.skipif(not INTEGRATION_TEST, reason="Integration tests disabled (set INTEGRATION_TEST=true)")
class TestRAGService:
    def test_vector_retrieve(self):
        response = httpx.post(
            f"{RAG_URL}/retrieve",
            json={"query": "AML compliance", "mode": "vector", "top_k": 3},
            timeout=30,
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
