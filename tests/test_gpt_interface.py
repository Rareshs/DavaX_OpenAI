import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gpt_interface import extract_themes, format_recommendations

def test_extract_themes_keywords():
    # Test that extract_themes returns a comma-separated string for a multi-topic query
    themes = extract_themes("Can you recommend a book about war and brotherhood?")
    assert isinstance(themes, str)
    assert "," in themes

def test_extract_themes_empty_prompt():
    # Test that extract_themes handles an empty prompt gracefully
    themes = extract_themes("")
    assert isinstance(themes, str)
    # Should be empty or not contain generic words like "book"
    assert len(themes) == 0 or "book" not in themes.lower()
    
def test_extract_themes_single_topic():
    # Test that extract_themes identifies a single topic correctly
    themes = extract_themes("Recommend a romance")
    assert "romance" in themes.lower()

def test_format_recommendations_structure():
    # Test that format_recommendations returns the expected markdown structure
    titles = ["1984", "The Hobbit"]
    output = format_recommendations(titles)
    assert output.startswith("## 📚 Recommended Books")
    assert "### 1." in output
