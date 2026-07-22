import asyncio

import chromadb

from src.repositories.document_repository import DocumentRepository

_asyncio_lock = asyncio.Lock()
_document_repository: DocumentRepository | None = None


async def get_document_repository() -> DocumentRepository:
    global _document_repository
    if not _document_repository:
        async with _asyncio_lock:
            client = await chromadb.AsyncHttpClient(
                host="localhost",
                port=12000
            )
            repo = DocumentRepository(client=client)
            await repo.initialize()
            _document_repository = repo
    return _document_repository
