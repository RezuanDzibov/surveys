from fastapi import FastAPI
from fastapi_pagination import add_pagination

from app.api.routes import router

app = FastAPI()
app.include_router(router)

add_pagination(app)
