"""
ML Risk Classifier Training Script
====================================
Trains a TF-IDF + Logistic Regression pipeline to classify financial
transaction descriptions into risk categories (HIGH / LOW).

Usage:
    python train_risk_classifier.py [--data-path PATH] [--output-path PATH]
"""

import argparse
import logging
import os

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

DEFAULT_DATA_PATH = os.path.join(
    os.path.dirname(__file__), "../../data_pipeline/sample_data/training.csv"
)
DEFAULT_OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), "../saved_models/risk_model.joblib"
)


def train(data_path: str, output_path: str) -> None:
    logger.info("Loading training data from: %s", data_path)
    df = pd.read_csv(data_path)

    logger.info("Dataset shape: %s", df.shape)
    logger.info("Class distribution:\n%s", df["risk_category"].value_counts())

    X = df["text"].astype(str)
    y = df["risk_category"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words="english",
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight="balanced",
        )),
    ])

    logger.info("Training model...")
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    logger.info("Classification Report:\n%s", classification_report(y_test, y_pred))

    macro_f1 = report["macro avg"]["f1-score"]
    min_f1_threshold = 0.70
    if macro_f1 < min_f1_threshold:
        raise ValueError(
            f"Model macro F1 ({macro_f1:.3f}) is below the minimum threshold ({min_f1_threshold}). "
            "Training aborted — review data quality or model parameters."
        )
    logger.info("Model meets quality threshold: macro F1 = %.3f >= %.2f", macro_f1, min_f1_threshold)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    joblib.dump(pipeline, output_path)
    logger.info("Model saved to: %s", output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train risk classifier")
    parser.add_argument("--data-path", default=DEFAULT_DATA_PATH, help="Path to training CSV")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH, help="Output path for model")
    args = parser.parse_args()
    train(args.data_path, args.output_path)
