import json

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain.tools import BaseTool
from langchain_core.runnables import Runnable

from src.models.schemas import LLMInput
from src.repositories import (
    MessageRepository,
    SessionRepository,
    SqliteSingleton
)
from src.repositories.agent_singleton import AgentSingleton
from src.services.agent_service import AgentService


agent_router = APIRouter(prefix="/agent")


@agent_router.post("/{session_id}/ask")
async def ask(
    session_id: int,
    request: LLMInput,
    sqlite_conn: aiosqlite.Connection = Depends(SqliteSingleton.get_conn),
    agent_and_tools: tuple[Runnable, dict[str, BaseTool]] = Depends(AgentSingleton.get_agents_and_tools)
):
    ses_repo = SessionRepository(sqlite_conn)
    msg_repo = MessageRepository(sqlite_conn)

    agent_service = AgentService(*agent_and_tools, message_repository=msg_repo)

    if not await ses_repo.exists(session_id):
        raise HTTPException(status_code=404)

    messages = await msg_repo.list(session_id)

    async def sse_wrapper():
        async for chunk in agent_service.ask(session_id, request.prompt, messages):
            yield f"data: {json.dumps({"token": chunk.content})}\n\n"
        yield "data: {\"done\": true}\n\n"

    return StreamingResponse(sse_wrapper(), media_type="text/event-stream")
