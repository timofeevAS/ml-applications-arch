from fastapi import FastAPI

from app.api.router import router as api_router

# NOTE: to run this application in basic way use:
#  uvicorn app.main:app --reload 
#
#  pwd: /ml-applications-arch/backend/...
app = FastAPI(
    title="Backend Service",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api")