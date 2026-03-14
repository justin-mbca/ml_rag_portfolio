"""
Tests for the data pipeline – ingestion module.
"""

import os
import tempfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from data_pipeline.ingestion import (  # noqa: E402
    Document,
    SUPPORTED_EXTENSIONS,
    load_from_filesystem,
    _read_file,
)


def test_document_creation():
    doc = Document(
        content="Test content about AML compliance.",
        filename="test.txt",
        source="/data/test.txt",
        metadata={"size_bytes": 35},
    )
    assert doc.filename == "test.txt"
    assert doc.source == "/data/test.txt"
    assert len(doc.content) > 0
    assert doc.metadata["size_bytes"] == 35


def test_document_repr():
    doc = Document(content="Hello", filename="hello.txt", source="/tmp/hello.txt")
    assert "hello.txt" in repr(doc)


def test_supported_extensions():
    assert ".pdf" in SUPPORTED_EXTENSIONS
    assert ".docx" in SUPPORTED_EXTENSIONS
    assert ".txt" in SUPPORTED_EXTENSIONS
    assert ".html" not in SUPPORTED_EXTENSIONS


def test_load_from_filesystem_empty_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        docs = load_from_filesystem(tmpdir)
    assert docs == []


def test_load_from_filesystem_txt_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        txt_file = Path(tmpdir) / "policy.txt"
        txt_file.write_text("This is a financial policy document.", encoding="utf-8")

        docs = load_from_filesystem(tmpdir)

    assert len(docs) == 1
    assert docs[0].filename == "policy.txt"
    assert "financial policy" in docs[0].content


def test_load_from_filesystem_filters_unsupported():
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "doc.txt").write_text("valid", encoding="utf-8")
        (Path(tmpdir) / "page.html").write_text("<html/>", encoding="utf-8")

        docs = load_from_filesystem(tmpdir)

    assert len(docs) == 1
    assert docs[0].filename == "doc.txt"


def test_load_from_filesystem_missing_dir():
    with pytest.raises(FileNotFoundError):
        load_from_filesystem("/nonexistent/path/to/dir")


def test_read_txt_file():
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False, encoding="utf-8") as f:
        f.write("Sample financial document content.")
        tmp_path = Path(f.name)

    try:
        content = _read_file(tmp_path)
        assert "Sample financial" in content
    finally:
        tmp_path.unlink()
