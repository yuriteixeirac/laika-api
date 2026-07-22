from langchain_ollama import OllamaEmbeddings
from chromadb.utils.embedding_functions import register_embedding_function
from chromadb import EmbeddingFunction


@register_embedding_function
class LaikaEmbeddingFunction(EmbeddingFunction):
    """Embedding function for registering documents on a vector database."""
    def __init__(self, model: str = "nomic-embed-text") -> None:
        self._embeddings = OllamaEmbeddings(model=model)

    def __call__(self, input: list[str]) -> list[list[float]]:    # type: ignore
        return self._embeddings.embed_documents(input)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
