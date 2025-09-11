from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_scan_returns_files():
    resp = client.post("/api/scan", json={"path": "app"})
    assert resp.status_code == 200
    data = resp.json()
    assert "files" in data
    # ensure at least one known file is listed
    assert any(f.endswith("main.py") for f in data["files"])
