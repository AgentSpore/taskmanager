import pytest
from fastapi.testclient import TestClient
from foundercrisishub.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db():
    # Ensure fresh DB for each test
    import os, shutil
    db_path = "test.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    yield

def test_create_and_get_crisis():
    payload = {"title": "Funding loss", "description": "Lost investor", "severity": "high"}
    resp = client.post("/api/crises", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    crisis_id = data["id"]
    get_resp = client.get(f"/api/crises/{crisis_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "Funding loss"

def test_list_crises():
    # create two
    client.post("/api/crises", json={"title": "A", "description": "B", "severity": "low"})
    client.post("/api/crises", json={"title": "C", "description": "D", "severity": "medium"})
    resp = client.get("/api/crises")
    assert resp.status_code == 200
    assert len(resp.json()) >= 2
