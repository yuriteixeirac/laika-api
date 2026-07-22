from langchain.tools import BaseTool
from langchain_core.runnables import Runnable
from langchain_ollama import ChatOllama

from src.tools import load_tools

class AgentSingleton:
    _agent: Runnable | None = None
    _tools: dict[str, BaseTool]

    @classmethod
    async def get_agents_and_tools(cls) -> tuple[Runnable, dict[str, BaseTool]]:
        if not cls._agent:
            tools: list[BaseTool] = await load_tools()

            cls._agent = ChatOllama(
                model="qwen2.5:7b",
                temperature=0.15,
            ).bind_tools(tools)
            cls._tools = {tool.name: tool for tool in tools}

        return cls._agent, cls._tools
