from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_sensors():
    response = client.get("/api/sensors")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 3

    assert data == [
        {
            "id": 1,
            "name": "Датчик 1",
            "metric": "vehicle_count_last_hour",
            "unit": "vehicles",
        },
        {
            "id": 2,
            "name": "Датчик 2",
            "metric": "vehicle_count_last_hour",
            "unit": "vehicles",
        },
        {
            "id": 3,
            "name": "Датчик 3",
            "metric": "vehicle_count_last_hour",
            "unit": "vehicles",
        },
    ]

