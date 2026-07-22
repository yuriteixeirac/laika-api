import json

import aiosqlite
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage, ToolMessage, HumanMessage



class MessageRepository:
    def __init__(self, conn: aiosqlite.Connection) -> None:
        self._conn = conn

    async def add(self, session_id: int, message: BaseMessage) -> int:
        async with self._conn.cursor() as cursor:
            match message:
                case SystemMessage(): role = "system"
                case HumanMessage():  role = "human"
                case AIMessage():     role = "ai"
                case ToolMessage():   role = "tool"
                case _:
                    raise ValueError(f"unsupported message type: {type(message).__name__}")

            tool_calls = json.dumps(getattr(message, "tool_calls", None) or [])
            tool_call_id = getattr(message, "tool_call_id", None)

            await cursor.execute("""
                INSERT INTO message (
                    content, role, tool_calls, tool_call_id, session_id
                ) VALUES (?, ?, ?, ?, ?)
            """, (message.content, role, tool_calls, tool_call_id, session_id),
            )
            await self._conn.commit()
            return cursor.lastrowid     # type: ignore

    async def remove(self, message_id: int) -> None:
        async with self._conn.cursor() as cursor:
            await cursor.execute("DELETE FROM message WHERE id = ?", (message_id,))
            await self._conn.commit()

    async def list(self, session_id: int) -> list[BaseMessage]:
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM message WHERE session_id = ? ORDER BY id",
                (session_id,),
            )
            rows = await cursor.fetchall()

            messages: list[BaseMessage] = []
            for row in rows:
                content = row["content"]
                tool_calls = json.loads(row["tool_calls"]) if row["tool_calls"] else []
                tool_call_id = str(row["tool_call_id"]) if row["tool_call_id"] is not None else ""

                match row["role"]:
                    case "system":
                        messages.append(SystemMessage(content=content))
                    case "human":
                        messages.append(HumanMessage(content=content))
                    case "ai":
                        messages.append(AIMessage(content=content, tool_calls=tool_calls))
                    case "tool":
                        messages.append(ToolMessage(
                            content=content,
                            tool_call_id=tool_call_id,
                            tool_calls=tool_calls,
                        ))

        return messages
