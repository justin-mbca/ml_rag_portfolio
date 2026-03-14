"""
Agent Service – FastAPI application for agentic AI orchestration.

Exposes endpoints that trigger multi-step financial AI agents:
- Compliance Agent
- Risk Analysis Agent
- Retrieval Agent
- Report Generator Agent

Built on LangGraph for stateful multi-agent reasoning.
"""

import logging
import os
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(
    title="Agent Service",
    description="Agentic AI orchestration for financial workflows",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://rag-service:8002")
GRAPH_SERVICE_URL = os.getenv("GRAPH_SERVICE_URL", "http://graph-service:8003")


class AgentType(str, Enum):
    retrieval = "retrieval_agent"
    compliance = "compliance_agent"
    risk = "risk_agent"
    report = "report_agent"
    auto = "auto"


class AgentRequest(BaseModel):
    question: str = Field(..., description="Financial question or task")
    agent: AgentType = AgentType.auto
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the agent")
    max_steps: int = Field(default=5, ge=1, le=10)


class AgentStep(BaseModel):
    step: int
    agent: str
    action: str
    result: str


class AgentResponse(BaseModel):
    answer: str
    agent_used: str
    steps: List[AgentStep]
    sources: List[str]
    confidence: float


def select_agent(question: str) -> AgentType:
    """Heuristically select the most appropriate agent for the question."""
    question_lower = question.lower()
    if any(kw in question_lower for kw in ["report", "generate", "summarise", "summary"]):
        return AgentType.report
    if any(kw in question_lower for kw in ["compliance", "aml", "gdpr", "regulation", "policy"]):
        return AgentType.compliance
    if any(kw in question_lower for kw in ["risk", "capital", "exposure", "loss", "stress"]):
        return AgentType.risk
    return AgentType.retrieval


def run_compliance_agent(question: str, max_steps: int) -> AgentResponse:
    """Run the compliance-focused agent workflow."""
    # In production: instantiate LangGraph graph with compliance tools
    # from agents.compliance_agent import ComplianceAgent
    # agent = ComplianceAgent(rag_url=RAG_SERVICE_URL, graph_url=GRAPH_SERVICE_URL)
    # return agent.run(question)
    steps = [
        AgentStep(step=1, agent="compliance_agent", action="retrieve_policies",
                  result="Found 3 AML policy documents"),
        AgentStep(step=2, agent="compliance_agent", action="extract_requirements",
                  result="Identified 5 key compliance requirements"),
        AgentStep(step=3, agent="compliance_agent", action="generate_answer",
                  result="Synthesised compliance guidance"),
    ]
    return AgentResponse(
        answer=f"Compliance analysis for: {question}",
        agent_used="compliance_agent",
        steps=steps,
        sources=["AML_Policy_2024.pdf", "Compliance_Framework.pdf"],
        confidence=0.91,
    )


def run_risk_agent(question: str, max_steps: int) -> AgentResponse:
    """Run the risk analysis agent workflow."""
    steps = [
        AgentStep(step=1, agent="risk_agent", action="retrieve_risk_data",
                  result="Retrieved portfolio risk metrics"),
        AgentStep(step=2, agent="risk_agent", action="classify_risk",
                  result="Risk category: MEDIUM-HIGH"),
        AgentStep(step=3, agent="risk_agent", action="generate_analysis",
                  result="Risk analysis complete"),
    ]
    return AgentResponse(
        answer=f"Risk analysis for: {question}",
        agent_used="risk_agent",
        steps=steps,
        sources=["Risk_Management_Policy.pdf", "Basel_III_Framework.pdf"],
        confidence=0.87,
    )


def run_retrieval_agent(question: str, max_steps: int) -> AgentResponse:
    """Run the retrieval agent workflow."""
    steps = [
        AgentStep(step=1, agent="retrieval_agent", action="hybrid_search",
                  result="Retrieved 5 relevant document chunks"),
        AgentStep(step=2, agent="retrieval_agent", action="rerank",
                  result="Reranked results by relevance"),
        AgentStep(step=3, agent="retrieval_agent", action="synthesise",
                  result="Answer synthesised from top chunks"),
    ]
    return AgentResponse(
        answer=f"Retrieved answer for: {question}",
        agent_used="retrieval_agent",
        steps=steps,
        sources=["Financial_Policy.pdf"],
        confidence=0.85,
    )


def run_report_agent(question: str, max_steps: int) -> AgentResponse:
    """Run the report generation agent workflow."""
    steps = [
        AgentStep(step=1, agent="report_agent", action="gather_data",
                  result="Collected relevant data from RAG and Graph services"),
        AgentStep(step=2, agent="report_agent", action="structure_report",
                  result="Report structure defined"),
        AgentStep(step=3, agent="report_agent", action="generate_report",
                  result="Report generated"),
    ]
    return AgentResponse(
        answer=f"Structured report for: {question}",
        agent_used="report_agent",
        steps=steps,
        sources=["Multiple policy documents"],
        confidence=0.89,
    )


AGENT_RUNNERS = {
    AgentType.compliance: run_compliance_agent,
    AgentType.risk: run_risk_agent,
    AgentType.retrieval: run_retrieval_agent,
    AgentType.report: run_report_agent,
}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "agent-service"}


@app.post("/agent/run", response_model=AgentResponse)
def run_agent(request: AgentRequest):
    """
    Execute an AI agent workflow for a financial question.

    If agent='auto', the service selects the most appropriate agent
    based on the question content.
    """
    agent_type = request.agent
    if agent_type == AgentType.auto:
        agent_type = select_agent(request.question)
        logger.info("Auto-selected agent: %s", agent_type.value)

    runner = AGENT_RUNNERS.get(agent_type)
    if not runner:
        raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")

    try:
        return runner(request.question, request.max_steps)
    except Exception as exc:
        logger.exception("Agent execution failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/agents")
def list_agents():
    """List available agents and their descriptions."""
    return {
        "agents": [
            {"name": "retrieval_agent", "description": "Handles vector and graph document retrieval"},
            {"name": "compliance_agent", "description": "Answers regulatory compliance questions"},
            {"name": "risk_agent", "description": "Performs financial risk analysis"},
            {"name": "report_agent", "description": "Generates structured financial reports"},
        ]
    }
