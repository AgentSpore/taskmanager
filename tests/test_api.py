def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200

def test_create_resource(client):
    response = client.post("/api/tasks/", json={"title": "Learn Python", "description": "Study for exam"})
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert "id" in data

def test_list_resources(client):
    response = client.get("/api/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_invalid_input(client):
    response = client.post("/api/tasks/", json={})
    assert response.status_code >= 400

def test_analytics(client):
    response = client.get("/api/analytics")
    assert response.status_code == 200

