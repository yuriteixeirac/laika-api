from pathlib import Path
from typing import TypedDict

import aiofiles
import aiosqlite
from langchain.messages import AIMessage, AIMessageChunk
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.runnables import Runnable
from langchain_ollama import OllamaEmbeddings
from chromadb.utils.embedding_functions import register_embedding_function
from chromadb import EmbeddingFunction

from src.repositories.sqlite_singleton import SqliteSingleton
from src.repositories.session_repository import SessionRepository


class ChromaDBConfig(TypedDict):
    host: str
    port: int


async def load_system_prompt() -> SystemMessage:
    async with aiofiles.open("src/prompts/SYSTEM.md") as file:
        return SystemMessage(await file.read())


@register_embedding_function
class LaikaEmbeddingFunction(EmbeddingFunction):
    """Embedding function for registering documents on a vector database."""
    def __init__(self, model: str = "nomic-embed-text") -> None:
        self._embeddings = OllamaEmbeddings(model=model)

    def __call__(self, input: list[str]) -> list[list[float]]:    # type: ignore
        return self._embeddings.embed_documents(input)


async def stream_output(llm: Runnable, messages: list[BaseMessage]) -> AIMessage:
    output: AIMessageChunk | None = None
    async for chunk in llm.astream(messages):
        if output is None:
            output = chunk if isinstance(chunk, AIMessageChunk) else AIMessageChunk(content=chunk.content or "")
        else:
            output += chunk

        if isinstance(chunk, AIMessageChunk) and chunk.content:
            print(chunk.content, end="", flush=True)
    print()

    return AIMessage(
        content=output.content if output else "",
        tool_calls=output.tool_calls if output else []
    )


async def read_file(filepath: str | Path) -> str:
    async with aiofiles.open(filepath) as file:
        return await file.read()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


async def get_sqlite_connection() -> aiosqlite.Connection:
    conn = await SqliteSingleton.get_conn()
    await SqliteSingleton.initialize()

    return conn


async def get_session_repository() -> SessionRepository:
    return SessionRepository(await get_sqlite_connection())
