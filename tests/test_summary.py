import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from summary import get_summary_by_title

def test_valid_title():
    summary = get_summary_by_title("The Great Gatsby")
    assert "Jay Gatsby" in summary

def test_invalid_title():
    summary = get_summary_by_title("Nonexistent Book")
    assert summary == "Summary not available for this title."
