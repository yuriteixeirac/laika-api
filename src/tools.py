import chromadb
from langchain.tools import BaseTool, tool

from repositories.chromadb_singleton import get_document_repository
from repositories.document_repository import DocumentRepository


def make_query_vector_database(document_repository: DocumentRepository) -> BaseTool:
    @tool
    async def query_vector_database(query: str, session_id: int) -> chromadb.QueryResult:
        """Queries the vector database for files semantically close to the query."""
        return await document_repository.query_documents(query=query, session_id=session_id)
    return query_vector_database


async def load_tools() -> list[BaseTool]:
    document_repository = await get_document_repository({"host": "localhost", "port": 8000})
    tools: list[BaseTool] = [
        make_query_vector_database(document_repository),
    ]

    return tools
