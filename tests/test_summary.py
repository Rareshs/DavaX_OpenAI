import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from summary import get_summary_by_title

def test_valid_title():
    summary = get_summary_by_title("The Great Gatsby")
    assert "Jay Gatsby" in summary
def test_valid_title_case_insensitive():
    summary = get_summary_by_title("the great gatsby")
    assert "Jay Gatsby" in summary

def test_valid_title_with_spaces():
    summary = get_summary_by_title("  The Hobbit  ")
    assert "Bilbo Baggins" in summary

def test_invalid_title():
    summary = get_summary_by_title("Nonexistent Book")
    assert summary.startswith("Summary not found")

def test_empty_title():
    summary = get_summary_by_title("")
    assert "Invalid book title" in summary

def test_non_string_title():
    summary = get_summary_by_title(None)
    assert "Invalid book title" in summary
    summary = get_summary_by_title(123)
    assert "Invalid book title" in summary

def test_exception_handling(monkeypatch):
    monkeypatch.setattr("summary.book_summaries_dict", None)
    summary = get_summary_by_title("1984")
    assert "error occurred" in summary.lower()

def test_partial_match_title():
    summary = get_summary_by_title("Gatsby")
    assert "Summary not found" in summary
    
def test_title_with_special_characters():
    summary = get_summary_by_title("The Great Gatsby!!!")
    assert "Summary not found" in summary


