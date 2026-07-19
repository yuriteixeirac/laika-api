from types import CoroutineType
from typing import Any, TypedDict

import aiofiles
from langchain.messages import SystemMessage
from langchain_ollama import OllamaEmbeddings
from chromadb.utils.embedding_functions import register_embedding_function
from chromadb import EmbeddingFunction


async def load_system_prompt() -> SystemMessage:
    async with aiofiles.open("src/prompts/SYSTEM.md") as file:
        return SystemMessage(await file.read())


class ChromaDBConfig(TypedDict):
    host: str
    port: int


@register_embedding_function
class LaikaEmbeddingFunction(EmbeddingFunction):
    """Embedding function for registering documents on a vector database."""
    def __init__(self, model: str = "nomic-embed-text") -> None:
        self._embeddings = OllamaEmbeddings(model=model)

    async def __call__(self, input: list[str]) -> CoroutineType[Any, Any, list[list[float]]]:   # type: ignore
        return await self._embeddings.aembed_documents(input)   # type: ignore
