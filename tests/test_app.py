import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_home_get():
    client = app.test_client()
    res = client.get("/")
    assert res.status_code == 200

def test_home_post_empty():
    client = app.test_client()
    res = client.post("/", data={"query": ""})
    assert res.status_code == 200
    assert b"AI Answer" not in res.data

def test_post_missing_query_field():
    client = app.test_client()
    res = client.post("/", data={})  # no "query"
    assert res.status_code == 200
    assert b"AI Answer" not in res.data


def test_home_put_method():
    client = app.test_client()
    res = client.put("/")
    assert res.status_code == 405  # Method Not Allowed

