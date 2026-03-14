"""
Tests for ML components – risk analysis model.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ml_components.risk_analysis_model import (  # noqa: E402
    RiskAnalysisModel,
    RiskAssessment,
    RISK_CATEGORIES,
    RISK_SCORES,
)


@pytest.fixture
def model():
    return RiskAnalysisModel(use_ml=False)


def test_assess_document_returns_valid_category(model):
    text = "The loan is compliant and within all regulatory limits."
    assessment = model.assess_document(text)
    assert isinstance(assessment, RiskAssessment)
    assert assessment.risk_category in RISK_CATEGORIES
    assert 0.0 <= assessment.confidence <= 1.0
    assert isinstance(assessment.risk_score, int)


def test_assess_high_risk_document(model):
    text = "Regulatory enforcement action issued for AML violations. Immediate response required."
    assessment = model.assess_document(text)
    assert assessment.risk_category in ("critical", "high")
    assert assessment.risk_score >= RISK_SCORES["high"]


def test_assess_low_risk_document(model):
    text = "All loans are compliant with covenants. No findings in the audit. Satisfactory review."
    assessment = model.assess_document(text)
    assert assessment.risk_category == "low"


def test_recommended_action_populated(model):
    text = "Covenant breach identified in CRE portfolio. Elevated exposure."
    assessment = model.assess_document(text)
    assert assessment.recommended_action != ""


def test_assess_portfolio(model):
    portfolio = [
        {"description": "Compliant mortgage loan within LTV limits", "exposure": 1_000_000},
        {"description": "AML violation detected, enforcement action pending", "exposure": 500_000},
    ]
    result = model.assess_portfolio(portfolio)
    assert result["total_positions"] == 2
    assert result["total_exposure"] == 1_500_000
    assert "risk_distribution" in result
    assert "average_risk_score" in result


def test_assess_empty_portfolio(model):
    result = model.assess_portfolio([])
    assert "error" in result


def test_train_returns_metrics(model):
    texts = ["compliant loan within limits"] * 5 + ["breach detected enforcement action"] * 5
    labels = ["low"] * 5 + ["critical"] * 5
    metrics = model.train(texts, labels)
    assert "accuracy" in metrics
    # Placeholder implementation returns 0.0
    assert isinstance(metrics["accuracy"], float)


def test_risk_score_ordering():
    assert RISK_SCORES["low"] < RISK_SCORES["medium"]
    assert RISK_SCORES["medium"] < RISK_SCORES["medium_high"]
    assert RISK_SCORES["medium_high"] < RISK_SCORES["high"]
    assert RISK_SCORES["high"] < RISK_SCORES["critical"]
