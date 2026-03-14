"""Agent Service - FastAPI application."""

import logging
from typing import Dict, Any

from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from agents import RetrievalAgent, ComplianceAgent, RiskAnalysisAgent

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "service": "agent-service", "message": "%(message)s"}',
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Agent Service", version="1.0.0")

QA_REQUESTS = Counter("agent_qa_requests_total", "Total QA requests")
QA_LATENCY = Histogram("agent_qa_latency_seconds", "QA latency")

retrieval_agent = RetrievalAgent()
compliance_agent = ComplianceAgent()
risk_agent = RiskAnalysisAgent()


class QARequest(BaseModel):
    question: str
    mode: str = "hybrid"


class QAResponse(BaseModel):
    question: str
    answer: str
    risk_analysis: Dict[str, Any]
    sources: list


@app.get("/health")
def health():
    return {"status": "ok", "service": "agent-service"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/qa", response_model=QAResponse)
def qa(request: QARequest):
    QA_REQUESTS.inc()
    with QA_LATENCY.time():
        logger.info("QA request: %s", request.question)

        context = retrieval_agent.run(request.question, mode=request.mode)
        answer = compliance_agent.run(request.question, context)
        risk = risk_agent.run(context)

        sources = [
            c.get("metadata", {}).get("source", "unknown")
            for c in context
            if c.get("metadata")
        ]

    return QAResponse(
        question=request.question,
        answer=answer,
        risk_analysis=risk,
        sources=list(set(sources)),
    )
