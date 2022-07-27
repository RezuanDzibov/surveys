from fastapi import FastAPI

from app.api.api_v1.routes import router

app = FastAPI()
app.include_router(router)
