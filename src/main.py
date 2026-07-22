from fastapi import FastAPI

from src.routers import session_router, document_router, agent_router

app = FastAPI()

app.include_router(session_router)
app.include_router(document_router)
app.include_router(agent_router)
