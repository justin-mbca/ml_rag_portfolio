"""Unit tests for the chunking functionality in the ingestion pipeline."""

import sys
import os

# Add ingestion-service app to path for direct import
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "../../services/ingestion-service/app"),
)

from pipeline import chunk_text


def test_chunk_text_basic():
    text = " ".join([f"word{i}" for i in range(100)])
    chunks = chunk_text(text, chunk_size=10, overlap=2)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.split()) <= 10


def test_chunk_text_single_chunk():
    text = "This is a short text"
    chunks = chunk_text(text, chunk_size=512, overlap=50)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_overlap():
    words = [f"w{i}" for i in range(20)]
    text = " ".join(words)
    chunks = chunk_text(text, chunk_size=10, overlap=5)
    # With overlap, words at the boundary should appear in consecutive chunks
    assert len(chunks) >= 2
    # Last words of chunk[0] should appear in first words of chunk[1]
    chunk0_words = set(chunks[0].split())
    chunk1_words = set(chunks[1].split())
    assert len(chunk0_words & chunk1_words) > 0


def test_chunk_text_empty():
    chunks = chunk_text("", chunk_size=10, overlap=2)
    assert chunks == []


def test_chunk_text_exact_size():
    words = [f"w{i}" for i in range(10)]
    text = " ".join(words)
    chunks = chunk_text(text, chunk_size=10, overlap=0)
    assert len(chunks) == 1


def test_chunk_text_preserves_content():
    text = "The AML compliance framework requires customer due diligence."
    chunks = chunk_text(text, chunk_size=3, overlap=0)
    reconstructed_words = []
    for chunk in chunks:
        reconstructed_words.extend(chunk.split())
    original_words = text.split()
    assert reconstructed_words == original_words
