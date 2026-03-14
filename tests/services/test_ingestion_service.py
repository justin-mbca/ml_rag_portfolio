"""
Tests for the Ingestion Service.
"""

import importlib.util
import io
import os

import pytest
from fastapi.testclient import TestClient

# Load the ingestion-service app module directly to avoid sys.path conflicts
_svc_dir = os.path.join(os.path.dirname(__file__), "..", "..", "services", "ingestion-service")
_spec = importlib.util.spec_from_file_location("ingestion_service_app", os.path.join(_svc_dir, "app.py"))
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

app = _module.app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ingestion-service"


def test_ingest_txt_file():
    file_content = b"This is a test financial document about AML compliance."
    response = client.post(
        "/ingest",
        files={"file": ("test_doc.txt", io.BytesIO(file_content), "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test_doc.txt"
    assert data["status"] == "queued"
    assert "document_id" in data
    assert len(data["document_id"]) == 36  # UUID format


def test_ingest_pdf_file():
    file_content = b"%PDF-1.4 placeholder content"
    response = client.post(
        "/ingest",
        files={"file": ("policy.pdf", io.BytesIO(file_content), "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "policy.pdf"


def test_ingest_unsupported_format():
    file_content = b"<html><body>test</body></html>"
    response = client.post(
        "/ingest",
        files={"file": ("page.html", io.BytesIO(file_content), "text/html")},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_get_ingestion_status():
    doc_id = "123e4567-e89b-12d3-a456-426614174000"
    response = client.get(f"/status/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == doc_id
    assert "status" in data
