import asyncio

from langchain.tools import BaseTool
from langchain_core.messages import BaseMessage
from langchain.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_ollama.chat_models import ChatOllama

from repositories.chromadb_singleton import get_document_repository
from tools import load_tools
import utils

# TODO:
# antes de iniciar o modelo,
# implementar interface de criação
# e leitura de sessões


async def main():
    llm = ChatOllama(
        model="qwen2.5:7b",
        temperature=0.15,
    )

    document_repository = await get_document_repository({"host": "localhost", "port": 8000})

    tools: list[BaseTool] = await load_tools()
    llm = llm.bind_tools(tools)

    tools_map = {tool.name: tool for tool in tools}

    messages: list[BaseMessage] = [SystemMessage(await utils.read_file("src/prompts/SYSTEM.md"))]

    while True:
        msg = input("> ")

        # TODO:
        # melhorar a implementação
        # de comandos da interface
        if msg == "/quit":
            break
        elif msg.startswith("/add"):
            _, filepath = msg.split(" ")
            content = await utils.read_file(filepath)
            await document_repository.upsert_document(
                name=filepath, content=content, session_id=1
            )
            continue

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
