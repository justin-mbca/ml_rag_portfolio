"""Agent definitions: RetrievalAgent, ComplianceAgent, RiskAnalysisAgent."""

import os
import logging
from typing import List, Dict, Any, Optional

import httpx
import joblib

logger = logging.getLogger(__name__)

RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://rag-service:8002")
RISK_MODEL_PATH = os.getenv("RISK_MODEL_PATH", "/models/risk_model.joblib")


class RetrievalAgent:
    """Calls RAG Service to retrieve relevant document chunks."""

    def run(self, question: str, mode: str = "hybrid", top_k: int = 5) -> List[Dict[str, Any]]:
        logger.info("RetrievalAgent: querying RAG service for '%s'", question)
        try:
            response = httpx.post(
                f"{RAG_SERVICE_URL}/retrieve",
                json={"query": question, "mode": mode, "top_k": top_k},
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json().get("results", [])
        except Exception as exc:
            logger.warning("RetrievalAgent failed: %s", exc)
            return []


class ComplianceAgent:
    """Summarizes compliance-relevant context from retrieved documents."""

    def run(self, question: str, context: List[Dict[str, Any]]) -> str:
        logger.info("ComplianceAgent: analyzing %d context chunks", len(context))
        if not context:
            return "No relevant compliance documents found."

        context_text = "\n\n".join(
            f"[Source: {c.get('metadata', {}).get('source', 'unknown')}]\n{c.get('text', '')}"
            for c in context[:3]
        )
        summary = (
            f"Based on retrieved financial documents, here is a compliance summary "
            f"for the query '{question}':\n\n{context_text}\n\n"
            "[Note: This is an AI-generated summary. Always verify with official compliance officers.]"
        )
        return summary


class RiskAnalysisAgent:
    """Loads a joblib risk classifier model and scores the query context."""

    def __init__(self):
        self._model = None

    def _load_model(self):
        if self._model is None:
            if os.path.exists(RISK_MODEL_PATH):
                logger.info("Loading risk model from %s", RISK_MODEL_PATH)
                self._model = joblib.load(RISK_MODEL_PATH)
            else:
                logger.warning("Risk model not found at %s, using placeholder", RISK_MODEL_PATH)
        return self._model

    def run(self, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        logger.info("RiskAnalysisAgent: analyzing risk for %d chunks", len(context))
        model = self._load_model()

        if model is None or not context:
            return {"risk_level": "UNKNOWN", "score": 0.0, "reason": "Model or context unavailable"}

        texts = [c.get("text", "") for c in context[:5]]
        combined_text = " ".join(texts)

        try:
            prediction = model.predict([combined_text])[0]
            proba = model.predict_proba([combined_text])[0]
            score = float(max(proba))
            return {
                "risk_level": str(prediction),
                "score": round(score, 4),
                "reason": "ML classifier risk assessment",
            }
        except Exception as exc:
            logger.error("Risk model prediction failed: %s", exc)
            return {"risk_level": "ERROR", "score": 0.0, "reason": str(exc)}
