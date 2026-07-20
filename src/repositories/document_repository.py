from datetime import datetime, timezone
from uuid import uuid4

import chromadb
from chromadb.api.models.AsyncCollection import AsyncCollection

import utils


class DocumentRepository:
    def __init__(self, client: chromadb.AsyncHttpClient) -> None: # type: ignore
        self._client = client

    async def initialize(self) -> None:
        self._collection: AsyncCollection = await self._client.get_or_create_collection(
            "laika", embedding_function=utils.LaikaEmbeddingFunction()
        )

    async def upsert_document(self, name: str, content: str, session_id: int) -> None:
        """Inserts or replace a document associated with a session."""
        await self._collection.delete(
            where={
                "$and": [{"session_id": session_id}, {"name": name}],
            }
        )

        await self._collection.add(
            ids=[str(uuid4())],
            documents=[content],
            metadatas=[{
                "session_id": session_id,
                "name": name,
                "inserted_at": datetime.now(
                    timezone.utc
                ).isoformat()
            }]
        )

    async def query_documents(self, query: str, session_id: int) -> chromadb.QueryResult:
        return await self._collection.query(
            query_texts=[query],
            where={
                "session_id": session_id
            },
            include=["documents", "metadatas"],
            n_results=5
        )


    async def delete_document(self, name: str, session_id: int) -> None:
        await self._collection.delete(
            where={
                "session_id": session_id,
                "name": name
            }
        )

    async def list_documents(self, session_id: int) -> chromadb.GetResult:
        return await self._collection.get(
            where={
                "session_id": session_id
            }
        )

    async def delete_session(self, session_id: int) -> None:
        await self._collection.delete(
            where={
                "session_id": session_id
            }
        )
