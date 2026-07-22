from typing import Any, AsyncGenerator

from langchain.messages import AIMessage, AIMessageChunk, HumanMessage, ToolMessage
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_core.tools.base import BaseTool

from src.repositories.message_repository import MessageRepository


class AgentService:
    def __init__(
        self,
        agent: Runnable,
        tools: dict[str, BaseTool],
        message_repository: MessageRepository
    ) -> None:
        self.__agent = agent
        self.__tools = tools
        self.__message_repository = message_repository

    async def ask(
        self,
        session_id: int,
        prompt: str,
        messages: list[BaseMessage]
    ) -> AsyncGenerator[AIMessageChunk, Any]:
        human = HumanMessage(content=prompt)
        messages.append(human)

        await self.__message_repository.add(session_id, human)

        i, max_i = 0, 10

        while i <= max_i:
            i += 1

            output: AIMessageChunk | None = None
            async for chunk in self.__agent.astream(messages):
                if output is None:
                    output = chunk if isinstance(
                        chunk, AIMessageChunk
                    ) else AIMessageChunk(content=chunk.content or "")
                else:
                    output += chunk

                if isinstance(chunk, AIMessageChunk) and chunk.content:
                    yield chunk

            final = AIMessage(
                content=output.content if output else "",
                tool_calls=output.tool_calls if output else []
            )
            messages.append(final)
            await self.__message_repository.add(session_id, final)

            if not final.tool_calls:
                break

            for tool_call in final.tool_calls:
                result = await self.__tools[
                    tool_call["name"]
                ].ainvoke(tool_call["args"])

                tool_message = ToolMessage(
                    content=result.content,
                    tool_call_id=tool_call["id"]
                )
                await self.__message_repository.add(session_id, tool_message)
                messages.append(tool_message)
