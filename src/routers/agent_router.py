from fastapi import APIRouter, Depends, HTTPException

from src.models.schemas import LLMInput
from src.repositories.message_repository import MessageRepository
from src.repositories.session_repository import SessionRepository
from src.utils import get_message_repository, get_session_repository


agent_router = APIRouter(prefix="/agent")


@agent_router.post("/{session_id}/ask")
async def ask(
    session_id: int,
    request: LLMInput,
    ses_repo: SessionRepository = Depends(get_session_repository),
    msg_repo: MessageRepository = Depends(get_message_repository)
):
    if not await ses_repo.exists(session_id):
        raise HTTPException(status_code=404)

    ...

    # TODO:
    # criar um singleton para o agent;
    # providenciar uma forma de passar
    # o histórico da sessão na conversa;
    # usar `StreamingResponse` para a saída;
