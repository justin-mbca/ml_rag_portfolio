"""
Risk Analysis Model – Predicts risk categories for financial documents and portfolios.

Supported risk categories:
- low
- medium
- medium_high
- high
- critical

Uses a scikit-learn ensemble model or a fine-tuned transformer for risk scoring.
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

MODEL_DIR = os.getenv("MODEL_DIR", "/models/risk_model")

RISK_CATEGORIES = ["low", "medium", "medium_high", "high", "critical"]
RISK_SCORES = {"low": 1, "medium": 2, "medium_high": 3, "high": 4, "critical": 5}

RISK_INDICATOR_KEYWORDS: Dict[str, List[str]] = {
    "critical": ["breach", "violation", "fraud", "sanction", "enforcement action", "regulatory penalty"],
    "high": ["non-compliant", "overdue", "escalated", "material risk", "significant exposure"],
    "medium_high": ["elevated", "watchlist", "concentration risk", "covenant breach"],
    "medium": ["monitoring", "review required", "moderate exposure", "flag"],
    "low": ["compliant", "within limits", "no findings", "satisfactory"],
}


@dataclass
class RiskAssessment:
    """The result of a risk analysis prediction."""

    risk_category: str
    risk_score: int
    confidence: float
    indicators: List[str] = field(default_factory=list)
    recommended_action: str = ""


class RiskAnalysisModel:
    """
    Financial risk analysis model for documents and portfolio data.

    Supports:
    - Document-level risk scoring (text input)
    - Portfolio-level risk aggregation (structured data input)
    - Trend analysis across multiple risk assessments

    Example usage::

        model = RiskAnalysisModel()
        assessment = model.assess_document("Credit exposure to CRE exceeds concentration limits...")
        print(assessment.risk_category, assessment.confidence)
    """

    RECOMMENDED_ACTIONS = {
        "critical": "Immediate escalation to Risk Committee and Regulator notification required",
        "high": "Escalate to Senior Risk Manager within 24 hours; prepare remediation plan",
        "medium_high": "Schedule risk review within 5 business days; update risk register",
        "medium": "Add to monitoring watch list; quarterly review recommended",
        "low": "No immediate action required; continue standard monitoring",
    }

    def __init__(self, use_ml: bool = True):
        self.use_ml = use_ml
        self.model = None
        if use_ml:
            self._load_model()

    def _load_model(self) -> None:
        """Load the trained risk prediction model."""
        model_path = Path(MODEL_DIR)
        if model_path.exists():
            logger.info("Loading risk model from %s", MODEL_DIR)
            try:
                # In production:
                # import joblib
                # self.model = joblib.load(model_path / "risk_model.pkl")
                pass
            except Exception:
                logger.exception("Failed to load risk model; falling back to rule-based scoring")
                self.use_ml = False
        else:
            logger.warning("Risk model not found at %s; using rule-based scoring", MODEL_DIR)
            self.use_ml = False

    def score_text_rule_based(self, text: str) -> Tuple[str, float, List[str]]:
        """
        Score document risk using keyword heuristics.

        Returns:
            Tuple of (risk_category, confidence, matched_indicators).
        """
        text_lower = text.lower()
        category_matches: Dict[str, List[str]] = {cat: [] for cat in RISK_CATEGORIES}

        for category, keywords in RISK_INDICATOR_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    category_matches[category].append(kw)

        # Select highest risk category with any matches
        for category in ["critical", "high", "medium_high", "medium", "low"]:
            if category_matches[category]:
                indicators = category_matches[category]
                confidence = min(0.5 + len(indicators) * 0.1, 0.95)
                return category, confidence, indicators

        return "medium", 0.5, []

    def assess_document(self, text: str) -> RiskAssessment:
        """
        Assess the risk level of a financial document.

        Args:
            text: Document text to analyse.

        Returns:
            RiskAssessment with category, score, confidence, and recommendations.
        """
        if self.use_ml and self.model is not None:
            # In production:
            # features = self._extract_features(text)
            # proba = self.model.predict_proba([features])[0]
            # category_idx = np.argmax(proba)
            # category = RISK_CATEGORIES[category_idx]
            # confidence = float(proba[category_idx])
            # indicators = self._extract_indicators(text, category)
            pass

        category, confidence, indicators = self.score_text_rule_based(text)
        return RiskAssessment(
            risk_category=category,
            risk_score=RISK_SCORES.get(category, 2),
            confidence=confidence,
            indicators=indicators,
            recommended_action=self.RECOMMENDED_ACTIONS.get(category, "Review required"),
        )

    def assess_portfolio(self, portfolio_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate risk across a portfolio of positions or loans.

        Args:
            portfolio_data: List of dicts, each with keys:
                - description (str): Loan/position description
                - exposure (float): Exposure amount
                - category (str, optional): Asset category

        Returns:
            Aggregated risk summary.
        """
        assessments = []
        total_exposure = 0.0
        high_risk_exposure = 0.0

        for item in portfolio_data:
            description = item.get("description", "")
            exposure = float(item.get("exposure", 0))
            assessment = self.assess_document(description)

            assessments.append({
                "description": description[:100],
                "exposure": exposure,
                "risk_category": assessment.risk_category,
                "risk_score": assessment.risk_score,
            })

            total_exposure += exposure
            if assessment.risk_score >= RISK_SCORES["high"]:
                high_risk_exposure += exposure

        if not assessments:
            return {"error": "No portfolio items provided"}

        avg_risk_score = np.mean([a["risk_score"] for a in assessments])
        risk_distribution = {
            cat: sum(1 for a in assessments if a["risk_category"] == cat)
            for cat in RISK_CATEGORIES
        }

        return {
            "total_positions": len(assessments),
            "total_exposure": total_exposure,
            "high_risk_exposure": high_risk_exposure,
            "high_risk_exposure_pct": high_risk_exposure / total_exposure if total_exposure > 0 else 0,
            "average_risk_score": round(float(avg_risk_score), 2),
            "risk_distribution": risk_distribution,
            "positions": assessments,
        }

    def train(
        self,
        texts: List[str],
        labels: List[str],
        save_path: Optional[str] = None,
    ) -> Dict[str, float]:
        """
        Train a gradient boosted risk classification model.

        Args:
            texts: Training document texts.
            labels: Risk category labels.
            save_path: Directory to save trained model.

        Returns:
            Training metrics.
        """
        logger.info("Training risk model on %d samples", len(texts))

        # In production:
        # from sklearn.pipeline import Pipeline
        # from sklearn.feature_extraction.text import TfidfVectorizer
        # from sklearn.ensemble import GradientBoostingClassifier
        # from sklearn.model_selection import cross_val_score
        #
        # pipeline = Pipeline([
        #     ("tfidf", TfidfVectorizer(max_features=5000)),
        #     ("clf", GradientBoostingClassifier(n_estimators=100)),
        # ])
        # scores = cross_val_score(pipeline, texts, labels, cv=5)
        # pipeline.fit(texts, labels)
        # if save_path:
        #     import joblib
        #     Path(save_path).mkdir(parents=True, exist_ok=True)
        #     joblib.dump(pipeline, f"{save_path}/risk_model.pkl")
        # return {"accuracy": scores.mean()}

        return {"accuracy": 0.0}


if __name__ == "__main__":
    model = RiskAnalysisModel(use_ml=False)

    test_cases = [
        "This loan is compliant with all covenants and within regulatory limits.",
        "The CRE portfolio shows elevated concentration risk with 3 covenant breaches.",
        "Regulatory enforcement action issued for AML violations. Immediate response required.",
    ]

    for text in test_cases:
        assessment = model.assess_document(text)
        print(
            f"Risk: {assessment.risk_category:12s} | Score: {assessment.risk_score} | "
            f"Confidence: {assessment.confidence:.2f} | {text[:60]}"
        )
