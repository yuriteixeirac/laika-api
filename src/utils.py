from typing import TypedDict

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

    def __call__(self, input: list[str]) -> list[list[float]]:    # type: ignore
        return self._embeddings.embed_documents(input)
