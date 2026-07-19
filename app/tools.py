import sys

from langchain.tools import BaseTool, tool
import inspect


@tool
async def get_age() -> int:
    """Returns the user age."""
    return 18


@tool
def get_user_name() -> str:
    """Returns the user name."""
    return "Yuri Teixeira"


def get_tools() -> list[BaseTool]:
    """Reads its own module to automatically fetch all tools."""
    cur = sys.modules[__name__]
    tools = []
    for _, object in inspect.getmembers(cur):
        if isinstance(object, BaseTool): tools.append(object)
    return tools


if __name__ == "__main__":
    print(get_tools())
