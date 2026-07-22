from typing import Optional

import aiosqlite
import chromadb
from chromadb.api.async_api import AsyncClientAPI
from chromadb.api.models.AsyncCollection import AsyncCollection
from fastapi import APIRouter, Depends, HTTPException
from src.models import Session

from src.models.schemas import SessionInput
from src.repositories.sqlite_singleton import SqliteSingleton
from src.repositories.chromadb_singleton import ChromaDBSingleton
from src.repositories.document_repository import DocumentRepository
from src.repositories.session_repository import SessionRepository


session_router = APIRouter(prefix="/sessions")


@session_router.get("/")
async def list_sessions(
    sqlite_conn: aiosqlite.Connection = Depends(
        SqliteSingleton.get_conn
    )
) -> list[Session]:
    ses_repo = SessionRepository(sqlite_conn)
    return await ses_repo.list()


@session_router.get("/{session_id}")
async def get_session(
    session_id: int,
    sqlite_conn: aiosqlite.Connection = Depends(SqliteSingleton.get_conn)
) -> Optional[Session]:
    ses_repo = SessionRepository(sqlite_conn)
    session = await ses_repo.get(session_id)
    if not session:
        raise HTTPException(status_code=404)
    return session


@session_router.post("/")
async def add_session(
    request: SessionInput,
    sqlite_conn: aiosqlite.Connection = Depends(
        SqliteSingleton.get_conn
    )
) -> Session:
    ses_repo = SessionRepository(sqlite_conn)

    session = Session(title=request.title)
    session.id = await ses_repo.add(session)
    return session


@session_router.delete("/{session_id}", status_code=204)
async def remove_session(
    session_id: int,
    sqlite_conn: aiosqlite.Connection = Depends(SqliteSingleton.get_conn),
    chroma_conn: tuple[
        AsyncClientAPI, AsyncCollection
    ] = Depends(ChromaDBSingleton.get_conn)
):
    ses_repo = SessionRepository(sqlite_conn)
    doc_repo = DocumentRepository(*chroma_conn)

    if not await ses_repo.exists(session_id=session_id):
        raise HTTPException(status_code=404)

    await ses_repo.remove(session_id)
    await doc_repo.delete_from_session(session_id)


@session_router.patch("/{session_id}")
async def update_session(
    session_id: int,
    request: SessionInput,
    sqlite_conn: aiosqlite.Connection = Depends(
        SqliteSingleton.get_conn
    )
) -> Session:
    ses_repo = SessionRepository(sqlite_conn)

    if not await ses_repo.exists(session_id):
        raise HTTPException(status_code=404)

    session = Session(
        id=session_id,
        title=request.title
    )
    return await ses_repo.update(session)
