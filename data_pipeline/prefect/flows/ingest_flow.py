"""Prefect flow for ingesting financial documents."""

import logging
import os
import sys

from prefect import flow, task, get_run_logger

# Allow importing from ingestion-service pipeline module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../services/ingestion-service/app"))


@task(name="ingest_folder_task", retries=2, retry_delay_seconds=10)
def ingest_folder_task(folder_path: str) -> dict:
    """Task to ingest all documents from a folder."""
    logger = get_run_logger()
    logger.info("Starting ingestion for folder: %s", folder_path)

    try:
        from pipeline import ingest_folder
        result = ingest_folder(folder_path)
        logger.info("Ingestion complete: %s", result)
        return result
    except Exception as exc:
        logger.error("Ingestion failed: %s", exc)
        raise


@flow(name="financial-document-ingest-flow", log_prints=True)
def financial_document_ingest_flow(
    folder_path: str = "/data/financial_docs",
) -> dict:
    """
    Prefect flow to ingest financial documents into the vector store.

    Args:
        folder_path: Path to the folder containing .txt and .md documents.

    Returns:
        dict with files_ingested and total_chunks counts.
    """
    logger = get_run_logger()
    logger.info("=== Financial Document Ingest Flow Starting ===")
    logger.info("Target folder: %s", folder_path)

    result = ingest_folder_task(folder_path)

    logger.info("=== Flow Complete: %s files ingested, %s chunks indexed ===",
                result.get("files_ingested", 0),
                result.get("total_chunks", 0))
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the financial document ingest flow")
    parser.add_argument("--folder", default="/data/financial_docs", help="Folder to ingest")
    args = parser.parse_args()
    financial_document_ingest_flow(folder_path=args.folder)
