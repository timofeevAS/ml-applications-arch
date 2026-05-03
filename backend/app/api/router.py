from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.sensors import router as sensors_router

router = APIRouter()
router.include_router(health_router, tags=["Health"])
router.include_router(sensors_router, tags=["Sensors"])
