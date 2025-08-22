import sys
import os
# Add parent directory to sys.path for module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

# Test GET request to home page returns 200 OK
def test_home_get():
    client = app.test_client()
    res = client.get("/")
    assert res.status_code == 200

# Test POST with empty query still returns 200 but no result shown
def test_home_post_empty():
    client = app.test_client()
    res = client.post("/", data={"query": ""})
    assert res.status_code == 200
    assert b"AI Answer" not in res.data

# Test POST with missing 'query' field returns 200 but no answer
def test_post_missing_query_field():
    client = app.test_client()
    res = client.post("/", data={})  # No "query" key in form
    assert res.status_code == 200
    assert b"AI Answer" not in res.data

# Test that PUT request is not allowed (only GET and POST are supported)
def test_home_put_method():
    client = app.test_client()
    res = client.put("/")
    assert res.status_code == 405  # Method Not Allowed
