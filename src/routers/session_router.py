from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from src.models import Session

from src.models.schemas import SessionInput
from src.repositories.session_repository import SessionRepository
from src import utils


session_router = APIRouter()


@session_router.get("/sessions/")
async def list_sessions(
    session_repository: SessionRepository = Depends(
        utils.get_session_repository
    )
) -> list[Session]:
    sessions = await session_repository.list()
    return sessions


@session_router.get("/sessions/{session_id}/")
async def get_session(
    session_id: int,
    repo: SessionRepository = Depends(
        utils.get_session_repository
    )
) -> Optional[Session]:
    session = await repo.get(session_id)
    if not session:
        raise HTTPException(status_code=404)
    return session


@session_router.post("/sessions/")
async def add_session(
    session_input: SessionInput,
    repo: SessionRepository = Depends(
        utils.get_session_repository
    )
) -> Session:
    session = Session(
        title=session_input.title,
        created_at=datetime.utcnow()
    )
    await repo.add(session)
    return session


@session_router.delete("/sessions/{session_id}/", status_code=200)
async def remove_session(
    session_id: int,
    repo: SessionRepository = Depends(
        utils.get_session_repository
    )
):
    if not await repo.exists(session_id=session_id):
        raise HTTPException(status_code=404)

    await repo.remove(session_id)
    return JSONResponse(content={
        "detail": "deleted succesfully."
    })


@session_router.patch("/sessions/")
async def update_session(
    session: Session,
    repo: SessionRepository = Depends(
        utils.get_session_repository
    )
) -> Session:
    if not session.id:
        raise HTTPException(status_code=403)

    if not await repo.exists(session.id):
        raise HTTPException(status_code=404)

    return await repo.update(session)
