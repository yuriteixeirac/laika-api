from fastapi import FastAPI
from .routers.session_router import session_router

app = FastAPI()

app.include_router(session_router)
