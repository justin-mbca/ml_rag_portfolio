"""
Compliance Agent – Handles financial regulatory compliance workflows.

Specialised agent for answering compliance-specific questions about:
- AML / KYC regulations
- GDPR and data privacy
- Basel III / CRD IV capital requirements
- MiFID II / MiFIR
- Dodd-Frank Act
- FATF recommendations

Uses a compliance-tuned prompt and retrieves from compliance document collections.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from agents.retrieval_agent import RetrievalAgent

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

COMPLIANCE_SYSTEM_PROMPT = """
You are a senior compliance officer at a global financial institution with deep expertise
in international banking regulations, AML/KYC frameworks, and regulatory reporting.

When answering questions:
1. Always cite the specific regulation, article, or policy section
2. Highlight any regulatory deadlines or thresholds
3. Flag high-risk areas that require immediate attention
4. Recommend next steps for compliance teams
5. Use precise regulatory terminology

If information is insufficient, explicitly state what additional documents are needed.
"""


class ComplianceAgent:
    """
    Compliance-specialised agent for regulatory question answering.

    Example usage::

        agent = ComplianceAgent()
        result = agent.run("What are our SAR reporting obligations under BSA?")
        print(result["answer"])
    """

    COMPLIANCE_CATEGORIES = [
        "AML", "KYC", "GDPR", "Basel III", "CRD IV", "MiFID II",
        "Dodd-Frank", "FATF", "OFAC", "sanctions", "CDD", "EDD",
    ]

    def __init__(self):
        self.retrieval_agent = RetrievalAgent(top_k=8, use_vector=True, use_graph=True)
        self._init_llm()

    def _init_llm(self) -> None:
        """Initialise the LLM with compliance-specific system prompt."""
        # In production:
        # from langchain_openai import ChatOpenAI
        # from langchain.prompts import SystemMessagePromptTemplate, ChatPromptTemplate
        # self.llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY, temperature=0)
        # self.prompt = ChatPromptTemplate.from_messages([
        #     ("system", COMPLIANCE_SYSTEM_PROMPT),
        #     ("human", "{question}\n\nContext:\n{context}")
        # ])
        logger.info("ComplianceAgent initialised (placeholder mode)")

    def detect_regulation_type(self, question: str) -> Optional[str]:
        """Identify which regulation the question relates to."""
        question_lower = question.lower()
        for category in self.COMPLIANCE_CATEGORIES:
            if category.lower() in question_lower:
                return category
        return None

    def check_regulatory_thresholds(self, answer: str) -> List[Dict[str, Any]]:
        """
        Extract and validate any regulatory thresholds mentioned in the answer.

        Returns a list of threshold objects with value, unit, and regulation.
        """
        # In production: use NLP/regex to extract thresholds
        return []

    def run(self, question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the compliance agent workflow.

        Steps:
        1. Identify the regulatory domain
        2. Retrieve relevant compliance documents
        3. Generate a compliance-grounded answer
        4. Validate any thresholds or deadlines mentioned
        5. Add compliance flags and recommended actions

        Args:
            question: The compliance question.
            context: Optional extra context (e.g. portfolio data).

        Returns:
            Dict with answer, regulation_type, sources, flags, recommended_actions.
        """
        regulation_type = self.detect_regulation_type(question)
        logger.info("Compliance query - regulation type: %s", regulation_type)

        # Step 1: Retrieve compliance documents
        retrieval_result = self.retrieval_agent.run(question)

        # Step 2: Generate compliance-specific answer
        # In production: use self.llm with COMPLIANCE_SYSTEM_PROMPT
        answer = (
            f"[Compliance Analysis - {regulation_type or 'General'}]\n\n"
            f"{retrieval_result['answer']}\n\n"
            "**Recommended Actions:**\n"
            "1. Review the relevant policy documents cited above\n"
            "2. Consult with the Legal and Compliance team\n"
            "3. Update internal procedures if required"
        )

        thresholds = self.check_regulatory_thresholds(answer)

        return {
            "answer": answer,
            "regulation_type": regulation_type,
            "sources": retrieval_result["sources"],
            "retrieval_method": retrieval_result["retrieval_method"],
            "thresholds": thresholds,
            "recommended_actions": [
                "Review cited policy documents",
                "Consult Legal & Compliance team",
                "Update procedures as required",
            ],
            "agent": "compliance_agent",
        }


if __name__ == "__main__":
    agent = ComplianceAgent()
    result = agent.run("What are the suspicious activity reporting requirements under BSA/AML?")
    print(result)
