import asyncio

from langchain.tools import BaseTool
from langchain_core.messages import BaseMessage
from langchain.messages import AIMessage, HumanMessage, ToolMessage
from langchain_ollama.chat_models import ChatOllama

from tools import load_tools
import utils


async def main():
    llm = ChatOllama(
        model="qwen2.5:7b",
        temperature=0.15,
    )

    tools: list[BaseTool] = await load_tools()
    llm = llm.bind_tools(tools)

    tools_map = {tool.name: tool for tool in tools}

    messages: list[BaseMessage] = [await utils.load_system_prompt()]

    while True:
        msg = input("> ")
        if msg == "/quit":
            break

        messages.append(
            HumanMessage(msg)
        )

        output: AIMessage = await utils.stream_output(llm, messages)
        messages.append(output)

        while output.tool_calls:
            for tool_call in output.tool_calls:
                result = await tools_map[
                    tool_call["name"]
                ].ainvoke(tool_call["args"])

                messages.append(
                    ToolMessage(
                        content=result,
                        tool_call_id=tool_call["id"]
                    )
                )

            output = await utils.stream_output(llm, messages)
            messages.append(output)


if __name__ == "__main__":
    asyncio.run(main())
