import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    from taskmanager.main import app
    return TestClient(app)
