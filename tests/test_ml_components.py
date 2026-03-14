"""
Tests for ML components – document classification.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ml_components.document_classification import (  # noqa: E402
    DocumentClassifier,
    DOCUMENT_CATEGORIES,
)


@pytest.fixture
def classifier():
    return DocumentClassifier(use_ml=False)


def test_classifier_returns_valid_category(classifier):
    text = "This AML policy outlines the procedures for monitoring suspicious transactions."
    category, confidence = classifier.classify(text)
    assert category in DOCUMENT_CATEGORIES
    assert 0.0 <= confidence <= 1.0


def test_classify_policy_document(classifier):
    text = "This policy document outlines the guidelines and procedures for compliance."
    category, _ = classifier.classify(text)
    assert category == "policy"


def test_classify_regulation_document(classifier):
    text = "This regulation sets out the requirements and compliance rules for financial institutions."
    category, _ = classifier.classify(text)
    assert category == "regulation"


def test_classify_risk_report(classifier):
    text = "Q4 Risk Report: VaR exposure and capital risk analysis with stress test results."
    category, _ = classifier.classify(text)
    assert category == "risk_report"


def test_classify_batch(classifier):
    texts = [
        "Internal audit findings and control assessment report.",
        "Basel III capital requirements regulation framework.",
    ]
    results = classifier.classify_batch(texts)
    assert len(results) == 2
    assert all(cat in DOCUMENT_CATEGORIES for cat, _ in results)
    assert all(0.0 <= conf <= 1.0 for _, conf in results)


def test_train_returns_metrics(classifier):
    texts = ["policy document text"] * 10 + ["regulation compliance text"] * 10
    labels = ["policy"] * 10 + ["regulation"] * 10
    metrics = classifier.train(texts, labels)
    assert "accuracy_mean" in metrics
    assert "accuracy_std" in metrics
    # Placeholder implementation returns 0.0 values
    assert isinstance(metrics["accuracy_mean"], float)
    assert isinstance(metrics["accuracy_std"], float)
