import asyncio
import json

from langchain_core.messages import BaseMessage
from langchain.tools import tool
from langchain.messages import AIMessage, HumanMessage, ToolMessage
from langchain_ollama.chat_models import ChatOllama

from langchain_protocol.protocol import ToolCall
from rich import print


@tool
async def get_age() -> int:
    """Returns the user age."""
    return 18


@tool
def get_user_name() -> str:
    """Returns the user name."""
    return "Yuri Teixeira"


async def main():
    llm = ChatOllama(
        model="qwen2.5:7b",
        temperature=1.0,
    )

    llm = llm.bind_tools([get_age, get_user_name])

    messages: list[BaseMessage] = []

    while True:
        msg = input("> ")
        if msg == "/quit":
            break

        messages.append(HumanMessage(msg))

        output: AIMessage = await llm.ainvoke(messages)
        messages.append(output) # type: ignore

        if output.tool_calls:
            for tool_call in output.tool_calls:
                content = json.dumps({})
                if tool_call["name"] == "get_age":
                    result = await get_age.ainvoke(tool_call["args"])
                    content = json.dumps({"age": result})
                elif tool_call["name"] == "get_user_name":
                    result = await get_user_name.ainvoke(tool_call["args"])
                    content = json.dumps({"name": result})

                messages.append(
                    ToolMessage(
                        content=content,
                        tool_call_id=tool_call["id"]
                    )
                )

            output = await llm.ainvoke(messages)
            messages.append(output)

        print(output.content)


if __name__ == "__main__":
    asyncio.run(main())
