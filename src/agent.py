import asyncio
from typing import Optional

from langchain.tools import BaseTool
from langchain.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama

from repositories.chromadb_singleton import get_document_repository
from models.session import Session
from repositories.session_repository import SessionRepository
from src.repositories.sqlite_singleton import SqliteSingleton
from tools import load_tools
import utils

# TODO:
# PROVIDENCIAR ESSE AGENT ATRAVÉS DE UM SINGLETON
# A CADA MENSAGEM, SALVAR NO BANCO PARA HISTÓRICO


async def main():
    print("THIS IS A PLACEHOLDER FOR A MENU.")
    print("PRESS A NUMBER FOR ITS RESPECTIVE COMMAND:")
    print("1. Create new session.")
    print("2. List sessions.")
    print("3. Find a session.")
    print("4. Delete a session.")
    print("5. Choose session")

    SESSION_ID: Optional[int] = None

    session_repository = SessionRepository(conn=await SqliteSingleton.get_conn())

    while True:
        command = input()

        if command == "1":
            title = input("Insira um título para sua sessão (não obrigatório): ")
            session = Session(title=title)
            await session_repository.add(session)
            print("CREATED!")
        elif command == "2":
            print("LISTING")
            for session in await session_repository.list():
                print(session)
        elif command == "3":
            id = int(input("id: "))
            session = await session_repository.get(id)

            print(session)
        elif command == "4":
            id = int(input("id: "))
            session = await session_repository.remove(id)
        elif command == "5":
            id = int(input("id: "))
            session = await session_repository.get(id)
            if not session:
                print("SESSION DOES NOT EXIST.")
                continue
            SESSION_ID = session.id
            break

    tools: list[BaseTool] = await load_tools()
    tools_map = {tool.name: tool for tool in tools}

    llm = ChatOllama(
        model="qwen2.5:7b",
        temperature=0.15,
    ).bind_tools(tools)

    messages: list[BaseMessage] = [await utils.load_system_prompt()]

    doc_repository = await get_document_repository(
        {"host": "localhost", "port": 8000}
    )

    while True:
        msg = input("> ")

        # TODO:
        # melhorar a implementação
        # de comandos da interface
        if msg == "/quit":
            break

        messages.append(HumanMessage(msg))

        output: AIMessage = await utils.stream_output(llm, messages)
        messages.append(output)

        while output.tool_calls:
            for tool_call in output.tool_calls:
                result = await tools_map[
                    tool_call["name"]
                ].ainvoke(tool_call["args"])

                messages.append(
                    ToolMessage(content=result, tool_call_id=tool_call["id"])
                )

            output = await utils.stream_output(llm, messages)
            messages.append(output)


if __name__ == "__main__":
    asyncio.run(main())
