from fastapi import FastAPI

# NOTE: to run this application in basic way use:
#  uvicorn app.main:app --reload --app-dir src
#  
#  pwd: /ml-applications-arch/backend/...
app = FastAPI(
    title="Backend Service",
    version="0.1.0",
)
