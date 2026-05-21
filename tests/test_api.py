import pytest

def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_resource(client):
    data = {"name": "test", "value": 42}
    response = client.post("/api/resources", json=data)
    assert response.status_code == 201
    assert response.json()["name"] == "test"

def test_list_resources(client):
    response = client.get("/api/resources")
    assert response.status_code == 200
    # Assuming at least one resource exists
    assert isinstance(response.json(), list)

def test_invalid_input(client):
    response = client.post("/api/resources", json={})
    assert response.status_code >= 400
