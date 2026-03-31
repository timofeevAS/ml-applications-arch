from fastapi.testclient import TestClient
import pytest

from app.main import app

client = TestClient(app)

@pytest.mark.xfail(reason="TODO: Health endpoint not implemented yet")
def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200
    
    assert response.json() == {
        "status": "ok"
    }
