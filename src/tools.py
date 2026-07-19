import inspect
import sys

from langchain.tools import BaseTool, tool


def get_tools() -> list:
    cur = sys.modules[__name__]
    return [
        reference for _, reference in inspect.getmembers(
            cur, predicate=lambda f: isinstance(f, BaseTool)
        )
    ]


@tool
def query_vector_database(query: str, session_id: int): pass


if __name__ == "__main__":
    print(get_tools())
