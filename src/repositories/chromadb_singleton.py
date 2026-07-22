import asyncio

import chromadb
from chromadb.api import AsyncClientAPI
from chromadb.api.models.AsyncCollection import AsyncCollection

from src import utils


class ChromaDBSingleton:
    _asyncio_lock = asyncio.Lock()
    _client: AsyncClientAPI | None = None

    @classmethod
    async def get_conn(cls) -> tuple[AsyncClientAPI, AsyncCollection]:
        if not cls._client:
            async with cls._asyncio_lock:
                cls._client = await chromadb.AsyncHttpClient(
                    host="localhost",
                    port=12000
                )
        collection = await cls._client.get_or_create_collection(
            "laika", embedding_function=utils.LaikaEmbeddingFunction()
        )
        return cls._client, collection
