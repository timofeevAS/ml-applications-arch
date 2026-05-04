from fastapi import APIRouter

from app.schemas.sensors import SensorResponse

router = APIRouter()

@router.get("/sensors", response_model=list[SensorResponse])
def get_sensors() -> list[SensorResponse]:
    return [
        SensorResponse(
            id=1,
            name="Датчик 1",
            metric="vehicle_count_last_hour",
            unit="vehicles",
        ),
        SensorResponse(
            id=2,
            name="Датчик 2",
            metric="vehicle_count_last_hour",
            unit="vehicles",
        ),
        SensorResponse(
            id=3,
            name="Датчик 3",
            metric="vehicle_count_last_hour",
            unit="vehicles",
        )
    ]
