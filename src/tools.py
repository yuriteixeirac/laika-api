import chromadb
from langchain.tools import BaseTool, tool

from src.repositories.document_repository import DocumentRepository
from src.repositories.chromadb_singleton import ChromaDBSingleton


def make_query_vector_database(document_repository: DocumentRepository) -> BaseTool:
    @tool
    async def query_vector_database(query: str, session_id: int) -> chromadb.QueryResult:
        """Queries the vector database for files semantically close to the query."""
        return await document_repository.query_documents(query=query, session_id=session_id)
    return query_vector_database


async def load_tools() -> list[BaseTool]:
    chroma_conn = await ChromaDBSingleton.get_conn()
    doc_repo = DocumentRepository(*chroma_conn)

    # MODIFY BY HAND!!!!
    tools: list[BaseTool] = [
        make_query_vector_database(doc_repo),
    ]

    return tools
