import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag_core import get_embedding, generate_id, parse_books, setup_chroma

def test_embedding_length():
    embedding = get_embedding("adventure war drama")
    assert isinstance(embedding, list)
    assert len(embedding) > 0

def test_embedding_empty_input():
    embedding = get_embedding("")
    assert isinstance(embedding, list)
    assert len(embedding) > 0  # Some models still return embeddings

def test_generate_id_consistency():
    assert generate_id("Test Title") == generate_id("Test Title")

def test_generate_id_empty():
    assert generate_id("") == ""

def test_parse_books_nonexistent_file():
    books = parse_books("nonexistent_file.txt")
    assert books == []

def test_parse_books_empty_file(tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("")
    books = parse_books(str(file_path))
    assert books == []

def test_parse_books_malformed(tmp_path):
    file_path = tmp_path / "malformed.txt"
    file_path.write_text("Just some text without proper format")
    books = parse_books(str(file_path))
    assert books == []

def test_setup_chroma_invalid_path(monkeypatch):
    monkeypatch.setattr("chromadb.PersistentClient", lambda path: (_ for _ in ()).throw(Exception("fail")))
    collection = setup_chroma()
    assert collection is None
