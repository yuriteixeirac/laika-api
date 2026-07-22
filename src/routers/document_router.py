# TODO:
# router para recepção e embedding de documentos
# usando a conexão com chromaDB
from uuid import uuid4

import aiosqlite
from chromadb.api import AsyncClientAPI
from chromadb.api.models.AsyncCollection import AsyncCollection
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from src.repositories.chromadb_singleton import ChromaDBSingleton
from src.repositories.document_repository import DocumentRepository
from src.repositories.session_repository import SessionRepository
from src.repositories.sqlite_singleton import SqliteSingleton


document_router = APIRouter(prefix="/documents")


@document_router.post("/{session_id}", status_code=204)
async def add_document(
    session_id: int,
    document: UploadFile = File(...),
    chroma_conn: tuple[
        AsyncClientAPI, AsyncCollection
    ] = Depends(ChromaDBSingleton.get_conn),
    sqlite_conn: aiosqlite.Connection = Depends(SqliteSingleton.get_conn)
):
    # TODO:
    # verificar a validade da extensão do arquivo
    ses_repo = SessionRepository(sqlite_conn)
    doc_repo = DocumentRepository(*chroma_conn)

    if not await ses_repo.exists(session_id):
        raise HTTPException(status_code=404)

    content = await document.read()
    if not content:
        raise HTTPException(status_code=400)

    await doc_repo.upsert_document(
        name=document.filename or str(uuid4()),
        content=content.decode(),
        session_id=session_id
    )


@document_router.get("/{session_id}")
async def list_documents(
    session_id: int,
    chroma_conn: tuple[
        AsyncClientAPI, AsyncCollection
    ] = Depends(ChromaDBSingleton.get_conn),
):
    doc_repo = DocumentRepository(*chroma_conn)

    documents = await doc_repo.list_documents(session_id)
    if not documents["metadatas"]:
        raise HTTPException(status_code=404)
    return documents["metadatas"]


@document_router.delete("/{session_id}/{filename:path}", status_code=204)
async def remove_document(
    session_id: int,
    filename: str,
    sqlite_conn: aiosqlite.Connection = Depends(SqliteSingleton.get_conn),
    chroma_conn: tuple[AsyncClientAPI, AsyncCollection] = Depends(ChromaDBSingleton.get_conn),
):
    ses_repo = SessionRepository(sqlite_conn)
    doc_repo = DocumentRepository(*chroma_conn)

    if not await ses_repo.exists(session_id):
        raise HTTPException(status_code=404)

    await doc_repo.delete_document(
        name=filename,
        session_id=session_id
    )
