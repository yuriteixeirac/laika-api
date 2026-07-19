import asyncio

from langchain_core.messages import BaseMessage
from langchain.messages import AIMessage, HumanMessage, ToolMessage
from langchain_ollama.chat_models import ChatOllama

import tools
import utils


async def main():
    llm = ChatOllama(
        model="qwen2.5:7b",
        temperature=0.15,
    )

    llm = llm.bind_tools(tools.get_tools())

    messages: list[BaseMessage] = [await utils.load_system_prompt()]

    while True:
        msg = input("> ")
        if msg == "/quit":
            break

        messages.append(HumanMessage(msg))

        output: AIMessage = await llm.ainvoke(messages)
        messages.append(output) # type: ignore

        if output.tool_calls:
            for tool_call in output.tool_calls:
                result = await getattr(
                    tools, tool_call["name"]
                ).ainvoke(tool_call["args"])

                messages.append(
                    ToolMessage(
                        content=result,
                        tool_call_id=tool_call["id"]
                    )
                )

            output = await llm.ainvoke(messages)
            messages.append(output)

        print(output.content)


if __name__ == "__main__":
    asyncio.run(main())
