from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from src.models import Session

from src.models.schemas import SessionInput
from src.repositories.chromadb_singleton import get_document_repository
from src.repositories.document_repository import DocumentRepository
from src.repositories.session_repository import SessionRepository
from src import utils


session_router = APIRouter(prefix="/sessions")


@session_router.get("/")
async def list_sessions(
    session_repository: SessionRepository = Depends(
        utils.get_session_repository
    )
) -> list[Session]:
    sessions = await session_repository.list()
    return sessions


@session_router.get("/{session_id}")
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


@session_router.post("/")
async def add_session(
    request: SessionInput,
    repo: SessionRepository = Depends(
        utils.get_session_repository
    )
) -> Session:
    session = Session(title=request.title)
    session.id = await repo.add(session)
    return session


@session_router.delete("/{session_id}", status_code=204)
async def remove_session(
    session_id: int,
    ses_repo: SessionRepository = Depends(utils.get_session_repository),
    doc_repo: DocumentRepository = Depends(get_document_repository)
):
    if not await ses_repo.exists(session_id=session_id):
        raise HTTPException(status_code=404)

    await ses_repo.remove(session_id)
    await doc_repo.delete_from_session(session_id)


@session_router.patch("/{session_id}")
async def update_session(
    session_id: int,
    request: SessionInput,
    repo: SessionRepository = Depends(
        utils.get_session_repository
    )
) -> Session:
    if not await repo.exists(session_id):
        raise HTTPException(status_code=404)

    session = Session(
        id=session_id,
        title=request.title
    )
    return await repo.update(session)
