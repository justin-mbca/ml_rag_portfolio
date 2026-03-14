"""
Document Classification – Classifies financial documents into categories.

Supported categories:
- policy
- regulation
- risk_report
- audit_report
- product_documentation
- correspondence
- financial_statement

Uses a fine-tuned HuggingFace transformer or a scikit-learn TF-IDF classifier.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

MODEL_DIR = os.getenv("MODEL_DIR", "/models/document_classifier")
HUGGINGFACE_MODEL = os.getenv("HF_CLASSIFIER_MODEL", "ProsusAI/finbert")

DOCUMENT_CATEGORIES = [
    "policy",
    "regulation",
    "risk_report",
    "audit_report",
    "product_documentation",
    "correspondence",
    "financial_statement",
]

# Keyword hints for rule-based fallback classification
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "policy": ["policy", "procedure", "guideline", "framework", "standard"],
    "regulation": ["regulation", "directive", "act", "rule", "requirement", "compliance"],
    "risk_report": ["risk", "exposure", "var", "stress test", "capital", "loss"],
    "audit_report": ["audit", "internal audit", "finding", "control", "assurance"],
    "product_documentation": ["product", "term sheet", "prospectus", "offering"],
    "correspondence": ["letter", "memo", "correspondence", "notice", "communication"],
    "financial_statement": ["balance sheet", "income statement", "p&l", "cash flow", "revenue"],
}


class DocumentClassifier:
    """
    Financial document classifier with ML and rule-based fallback.

    Example usage::

        classifier = DocumentClassifier()
        category, confidence = classifier.classify("This document outlines the AML policy...")
        print(category, confidence)
    """

    def __init__(self, use_ml: bool = True):
        self.use_ml = use_ml
        self.model = None
        self.vectorizer = None
        if use_ml:
            self._load_model()

    def _load_model(self) -> None:
        """Load the trained classification model."""
        model_path = Path(MODEL_DIR)
        if model_path.exists():
            logger.info("Loading classifier model from %s", MODEL_DIR)
            try:
                # In production (scikit-learn):
                # import joblib
                # self.model = joblib.load(model_path / "classifier.pkl")
                # self.vectorizer = joblib.load(model_path / "vectorizer.pkl")

                # Or HuggingFace transformer:
                # from transformers import pipeline
                # self.model = pipeline(
                #     "text-classification",
                #     model=HUGGINGFACE_MODEL,
                #     device=-1
                # )
                pass
            except Exception:
                logger.exception("Failed to load model; falling back to rule-based classification")
                self.use_ml = False
        else:
            logger.warning("Model not found at %s; using rule-based classification", MODEL_DIR)
            self.use_ml = False

    def classify_rule_based(self, text: str) -> Tuple[str, float]:
        """
        Classify a document using keyword heuristics.

        Args:
            text: Document text.

        Returns:
            Tuple of (category, confidence_score).
        """
        text_lower = text.lower()
        scores: Dict[str, int] = {cat: 0 for cat in DOCUMENT_CATEGORIES}

        for category, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    scores[category] += 1

        best_category = max(scores, key=lambda k: scores[k])
        total_matches = sum(scores.values())
        confidence = scores[best_category] / total_matches if total_matches > 0 else 0.5

        return best_category, min(confidence, 1.0)

    def classify_ml(self, text: str) -> Tuple[str, float]:
        """
        Classify using the trained ML model.

        Args:
            text: Document text.

        Returns:
            Tuple of (category, confidence_score).
        """
        if self.model is None:
            return self.classify_rule_based(text)

        # In production (scikit-learn):
        # features = self.vectorizer.transform([text])
        # probabilities = self.model.predict_proba(features)[0]
        # category_idx = np.argmax(probabilities)
        # return self.model.classes_[category_idx], float(probabilities[category_idx])

        # In production (HuggingFace):
        # result = self.model(text[:512])[0]
        # return result["label"], result["score"]

        return self.classify_rule_based(text)

    def classify(self, text: str) -> Tuple[str, float]:
        """
        Classify a document into a financial document category.

        Args:
            text: Document text to classify.

        Returns:
            Tuple of (category, confidence_score).
        """
        if self.use_ml and self.model is not None:
            return self.classify_ml(text)
        return self.classify_rule_based(text)

    def classify_batch(self, texts: List[str]) -> List[Tuple[str, float]]:
        """
        Classify multiple documents efficiently.

        Args:
            texts: List of document texts.

        Returns:
            List of (category, confidence) tuples.
        """
        return [self.classify(text) for text in texts]

    def train(
        self,
        training_texts: List[str],
        labels: List[str],
        save_path: Optional[str] = None,
    ) -> Dict[str, float]:
        """
        Train a scikit-learn TF-IDF + Logistic Regression classifier.

        Args:
            training_texts: List of document texts for training.
            labels: Corresponding category labels.
            save_path: Directory to save the trained model.

        Returns:
            Training metrics dict.
        """
        logger.info("Training document classifier on %d samples", len(training_texts))

        # In production:
        # from sklearn.pipeline import Pipeline
        # from sklearn.feature_extraction.text import TfidfVectorizer
        # from sklearn.linear_model import LogisticRegression
        # from sklearn.model_selection import cross_val_score
        #
        # pipeline = Pipeline([
        #     ("tfidf", TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),
        #     ("clf", LogisticRegression(max_iter=500, C=1.0)),
        # ])
        # scores = cross_val_score(pipeline, training_texts, labels, cv=5, scoring="accuracy")
        # pipeline.fit(training_texts, labels)
        #
        # if save_path:
        #     import joblib
        #     Path(save_path).mkdir(parents=True, exist_ok=True)
        #     joblib.dump(pipeline.named_steps["clf"], f"{save_path}/classifier.pkl")
        #     joblib.dump(pipeline.named_steps["tfidf"], f"{save_path}/vectorizer.pkl")
        #
        # self.model = pipeline.named_steps["clf"]
        # self.vectorizer = pipeline.named_steps["tfidf"]
        #
        # return {"accuracy_mean": scores.mean(), "accuracy_std": scores.std()}

        return {"accuracy_mean": 0.0, "accuracy_std": 0.0}


if __name__ == "__main__":
    classifier = DocumentClassifier(use_ml=False)
    test_docs = [
        "This policy outlines the procedures for AML compliance monitoring.",
        "Q3 2024 Risk Report: VaR exposure increased by 12% in the CRE portfolio.",
        "Basel III regulation requires banks to maintain a CET1 ratio of 4.5%.",
    ]
    for doc in test_docs:
        category, confidence = classifier.classify(doc)
        print(f"Category: {category:25s} Confidence: {confidence:.2f}  | {doc[:60]}")
