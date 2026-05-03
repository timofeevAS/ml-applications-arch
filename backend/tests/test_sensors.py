from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_sensors():
    response = client.get("/api/sensors")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 3

    sensor = data[0]

    assert sensor["id"] == 1
    assert sensor["name"] == "Датчик 1"
    assert sensor["metric"] == "vehicle_count_last_hour"
    assert sensor["unit"] == "vehicles"
