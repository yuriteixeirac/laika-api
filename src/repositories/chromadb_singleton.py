import asyncio

import chromadb

from src.repositories.document_repository import DocumentRepository
from src import utils

_asyncio_lock = asyncio.Lock()
_document_repository: DocumentRepository | None = None


async def get_document_repository(config: utils.ChromaDBConfig) -> DocumentRepository:
    global _document_repository
    if not _document_repository:
        async with _asyncio_lock:
            client = await chromadb.AsyncHttpClient(**config)
            repo = DocumentRepository(client=client)
            await repo.initialize()
            _document_repository = repo
    return _document_repository
