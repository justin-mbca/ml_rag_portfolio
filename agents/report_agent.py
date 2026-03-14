"""
Report Agent – Generates structured financial reports.

Produces formatted reports from:
- Risk analysis summaries
- Compliance assessment results
- Regulatory change impact analyses
- Portfolio exposure reports

Supports multiple output formats: JSON, Markdown, PDF (via WeasyPrint).
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from agents.retrieval_agent import RetrievalAgent

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

REPORT_TEMPLATES = {
    "risk_analysis": {
        "sections": ["executive_summary", "risk_categories", "key_findings", "recommendations"],
        "title_prefix": "Risk Analysis Report",
    },
    "compliance_assessment": {
        "sections": ["executive_summary", "regulatory_requirements", "gaps", "action_plan"],
        "title_prefix": "Compliance Assessment",
    },
    "regulatory_impact": {
        "sections": ["overview", "affected_areas", "timeline", "required_changes"],
        "title_prefix": "Regulatory Impact Analysis",
    },
}


class ReportAgent:
    """
    Report generation agent that produces structured financial reports.

    Example usage::

        agent = ReportAgent()
        report = agent.generate(
            query="Generate a risk analysis report for CRE portfolio",
            report_type="risk_analysis"
        )
        print(report["markdown"])
    """

    def __init__(self):
        self.retrieval_agent = RetrievalAgent(top_k=10, use_vector=True, use_graph=True)
        self._init_llm()

    def _init_llm(self) -> None:
        """Initialise the LLM for structured output generation."""
        # In production:
        # from langchain_openai import ChatOpenAI
        # self.llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY, temperature=0.2)
        logger.info("ReportAgent initialised (placeholder mode)")

    def detect_report_type(self, query: str) -> str:
        """Infer the report type from the query."""
        query_lower = query.lower()
        if any(kw in query_lower for kw in ["risk", "exposure", "loss", "capital"]):
            return "risk_analysis"
        if any(kw in query_lower for kw in ["compliance", "regulatory", "regulation", "aml"]):
            return "compliance_assessment"
        if any(kw in query_lower for kw in ["impact", "change", "new rule", "amendment"]):
            return "regulatory_impact"
        return "risk_analysis"

    def build_executive_summary(
        self, query: str, chunks: List[Dict[str, Any]]
    ) -> str:
        """Generate the executive summary section."""
        # In production: use LLM to generate a concise summary from chunks
        return (
            f"This report addresses: {query}. "
            f"Analysis is based on {len(chunks)} retrieved document sources."
        )

    def build_risk_categories(self, chunks: List[Dict[str, Any]]) -> Dict[str, str]:
        """Extract and categorise risk levels from retrieved content."""
        # In production: use ML model or LLM to classify risk levels
        return {
            "credit_risk": "MEDIUM",
            "market_risk": "LOW",
            "operational_risk": "MEDIUM",
            "compliance_risk": "HIGH",
        }

    def build_recommendations(self, query: str) -> List[str]:
        """Generate actionable recommendations."""
        # In production: use LLM with structured output
        return [
            "Review and update relevant internal policies",
            "Conduct enhanced monitoring for identified risk areas",
            "Schedule quarterly compliance review",
            "Engage external counsel for complex regulatory matters",
        ]

    def render_markdown(self, report: Dict[str, Any]) -> str:
        """Render the report as a Markdown string."""
        lines = [
            f"# {report['title']}",
            f"**Date:** {report['date']}",
            f"**Prepared by:** GenAI Financial Assistant – Report Agent",
            "",
            "---",
            "",
            "## Executive Summary",
            report.get("executive_summary", ""),
            "",
        ]
        if "risk_categories" in report:
            lines += ["## Risk Categories", ""]
            for category, level in report["risk_categories"].items():
                lines.append(f"- **{category.replace('_', ' ').title()}**: {level}")
            lines.append("")

        if "key_findings" in report:
            lines += ["## Key Findings", ""]
            for finding in report.get("key_findings", []):
                lines.append(f"- {finding}")
            lines.append("")

        if "recommendations" in report:
            lines += ["## Recommendations", ""]
            for i, rec in enumerate(report.get("recommendations", []), 1):
                lines.append(f"{i}. {rec}")
            lines.append("")

        if "sources" in report:
            lines += ["## Sources", ""]
            for source in report.get("sources", []):
                lines.append(f"- {source}")

        return "\n".join(lines)

    def generate(
        self, query: str, report_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a structured financial report.

        Args:
            query: Description of what the report should cover.
            report_type: Type of report (risk_analysis, compliance_assessment, regulatory_impact).
                         Auto-detected if not provided.

        Returns:
            Dict with title, date, sections, markdown, and sources.
        """
        if not report_type:
            report_type = self.detect_report_type(query)

        template = REPORT_TEMPLATES.get(report_type, REPORT_TEMPLATES["risk_analysis"])
        logger.info("Generating %s report for: %s", report_type, query[:100])

        retrieval_result = self.retrieval_agent.run(query)

        # Build structured report sections
        chunks = [
            {"content": retrieval_result["answer"], "metadata": {"source": s}}
            for s in retrieval_result["sources"]
        ]

        report = {
            "title": f"{template['title_prefix']} – {datetime.now().strftime('%B %Y')}",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "report_type": report_type,
            "executive_summary": self.build_executive_summary(query, chunks),
            "risk_categories": self.build_risk_categories(chunks),
            "key_findings": [
                "Identified elevated compliance risk in AML monitoring",
                "Capital ratios are within regulatory minimums but close to buffer thresholds",
                "Documentation gaps found in 3 policy areas",
            ],
            "recommendations": self.build_recommendations(query),
            "sources": retrieval_result["sources"],
        }

        report["markdown"] = self.render_markdown(report)
        report["agent"] = "report_agent"

        return report


if __name__ == "__main__":
    agent = ReportAgent()
    report = agent.generate("Generate a compliance risk report for AML obligations")
    print(report["markdown"])
