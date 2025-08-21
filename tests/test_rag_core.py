import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag_core import get_embedding

def test_embedding_length():
    embedding = get_embedding("adventure war drama")
    assert isinstance(embedding, list)
    assert len(embedding) > 0

def test_embedding_empty_input():
    embedding = get_embedding("")
    assert isinstance(embedding, list)
    assert len(embedding) > 0  # Some models still return embeddings
