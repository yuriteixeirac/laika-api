from fastapi import FastAPI
from .routers.session_router import session_router
from .routers.document_router import document_router

app = FastAPI()

app.include_router(session_router)
app.include_router(document_router)
