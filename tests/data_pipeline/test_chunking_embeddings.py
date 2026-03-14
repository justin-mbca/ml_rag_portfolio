"""
Tests for the data pipeline – chunking and embeddings module.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from data_pipeline.chunking_embeddings import (  # noqa: E402
    DocumentChunk,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    generate_embeddings,
    process_document,
    split_text,
)


def test_split_text_basic():
    text = "A" * 1000
    chunks = split_text(text, chunk_size=200, chunk_overlap=20)
    assert len(chunks) > 1
    assert all(len(c) <= 200 for c in chunks)


def test_split_text_overlap():
    text = "word " * 200  # 1000 chars
    chunks = split_text(text, chunk_size=100, chunk_overlap=20)
    # Verify overlap: end of chunk n should appear at start of chunk n+1
    assert len(chunks) >= 2
    overlap_text = chunks[0][80:]  # last 20 chars of first chunk
    assert overlap_text in chunks[1]


def test_split_text_shorter_than_chunk():
    text = "Short text"
    chunks = split_text(text, chunk_size=500, chunk_overlap=50)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_split_text_empty():
    chunks = split_text("", chunk_size=100, chunk_overlap=10)
    assert chunks == []


def test_generate_embeddings_returns_correct_shape():
    texts = ["financial policy text", "AML compliance document", "Basel III requirements"]
    embeddings = generate_embeddings(texts)
    assert len(embeddings) == 3
    assert all(len(e) == 1536 for e in embeddings)


def test_generate_embeddings_empty_input():
    embeddings = generate_embeddings([])
    assert embeddings == []


def test_process_document_creates_chunks():
    content = "This is a financial compliance document. " * 50
    chunks = process_document(content, "test.txt", "/data/test.txt", chunk_size=100, chunk_overlap=10)
    assert len(chunks) > 0
    assert all(isinstance(c, DocumentChunk) for c in chunks)


def test_process_document_chunk_metadata():
    content = "Test document content. " * 20
    chunks = process_document(content, "policy.pdf", "s3://bucket/policy.pdf")
    for chunk in chunks:
        assert chunk.filename == "policy.pdf"
        assert chunk.source == "s3://bucket/policy.pdf"
        assert chunk.embedding is not None
        assert len(chunk.embedding) == 1536


def test_process_document_chunk_indices():
    content = "X" * 2000
    chunks = process_document(content, "doc.txt", "/tmp/doc.txt", chunk_size=200, chunk_overlap=20)
    indices = [c.chunk_index for c in chunks]
    assert indices == list(range(len(chunks)))
