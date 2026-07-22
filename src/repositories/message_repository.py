import aiosqlite
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage, ToolMessage, HumanMessage


class MessageRepository:
    def __init__(self, conn: aiosqlite.Connection) -> None:
        self._conn = conn

    async def add(self, session_id: int, message: BaseMessage) -> int:
        async with self._conn.cursor() as cursor:
            match message:
                case SystemMessage(): role = "system"
                case AIMessage():     role = "ai"
                case ToolMessage():   role = "tool"
                case HumanMessage():  role = "human"
                case _:
                    raise ValueError("no valid instance was provided.")

            tool_calls = []
            if hasattr(message, "tool_calls"):
                tool_calls = message.tool_calls     # type: ignore

            await cursor.execute("""
                INSERT INTO message (
                    content, role, tool_calls, session_id
                ) VALUES (?, ?, ?, ?)
            """, (message.content, role, tool_calls, session_id))
            await self._conn.commit()

            return cursor.lastrowid     # type: ignore

    async def remove(self, message_id: int) -> None:
        async with self._conn.cursor() as cursor:
            await cursor.execute("DELETE FROM message WHERE id = ?", (message_id,))
            await self._conn.commit()
