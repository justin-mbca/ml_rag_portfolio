"""
Tests for the Agent Service.
"""

import importlib.util
import os

import pytest
from fastapi.testclient import TestClient

# Load the agent-service app module directly to avoid sys.path conflicts
_svc_dir = os.path.join(os.path.dirname(__file__), "..", "..", "services", "agent-service")
_spec = importlib.util.spec_from_file_location("agent_service_app", os.path.join(_svc_dir, "app.py"))
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

app = _module.app
select_agent = _module.select_agent
AgentType = _module.AgentType

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "agent-service"


def test_list_agents():
    response = client.get("/agents")
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert len(data["agents"]) >= 4
    agent_names = [a["name"] for a in data["agents"]]
    assert "retrieval_agent" in agent_names
    assert "compliance_agent" in agent_names


def test_run_compliance_agent():
    response = client.post(
        "/agent/run",
        json={
            "question": "What are our AML reporting obligations?",
            "agent": "compliance_agent",
            "max_steps": 3,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["agent_used"] == "compliance_agent"
    assert "answer" in data
    assert "steps" in data
    assert len(data["steps"]) > 0


def test_run_auto_selects_compliance_agent():
    response = client.post(
        "/agent/run",
        json={
            "question": "Explain GDPR compliance requirements for customer data",
            "agent": "auto",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["agent_used"] == "compliance_agent"


def test_run_auto_selects_risk_agent():
    response = client.post(
        "/agent/run",
        json={"question": "Analyse capital risk exposure for Q4", "agent": "auto"},
    )
    assert response.status_code == 200
    assert response.json()["agent_used"] == "risk_agent"


def test_run_auto_selects_report_agent():
    response = client.post(
        "/agent/run",
        json={"question": "Generate a risk analysis report for the CRE portfolio", "agent": "auto"},
    )
    assert response.status_code == 200
    assert response.json()["agent_used"] == "report_agent"


def test_select_agent_logic():
    assert select_agent("What are the AML compliance risks?") == AgentType.compliance
    assert select_agent("Analyse capital risk") == AgentType.risk
    assert select_agent("Generate a summary report") == AgentType.report
    assert select_agent("Find documents about Basel III") == AgentType.retrieval


def test_run_agent_missing_question():
    response = client.post("/agent/run", json={"agent": "compliance_agent"})
    assert response.status_code == 422
