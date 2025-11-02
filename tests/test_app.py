import os
import sys

# Ensure project root is on sys.path for test discovery/imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Also ensure backend/app is on sys.path so imports like `from config import settings` resolve
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app")))

from fastapi.testclient import TestClient
from backend.app.main import app


client = TestClient(app)


def test_read_root():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    # Root returns API metadata
    assert "name" in data and "version" in data


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    # Health endpoint returns status/version/timestamp
    j = resp.json()
    assert j.get("status") == "healthy"
    assert "version" in j and "timestamp" in j
