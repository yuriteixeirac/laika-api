from typing import Optional

import aiosqlite

from models.session import Session


class SessionRepository:
    def __init__(self, conn: aiosqlite.Connection) -> None:
        self._conn = conn

    async def add(self, session: Session) -> int:
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO session (title, created_at) VALUES (?, ?);",
                (session.title, session.created_at)
            )
            await self._conn.commit()

            session_id = cursor.lastrowid or -1

            session.id = session_id
            return session_id

    async def remove(self, session_id: int) -> int:
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM session WHERE id = ?;",
                (session_id,)
            )
            await self._conn.commit()
            return cursor.rowcount

    async def list(self) -> list[Session]:
        async with self._conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM session;")
            rows = await cursor.fetchall()

            if not rows:
                return []

            return [
                Session(
                    id=row["id"],
                    title=row["title"],
                    created_at=row["created_at"]
                ) for row in rows
            ]

    async def get(self, session_id: int) -> Optional[Session]:
        async with self._conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM session WHERE id = ?;", (session_id,))
            row = await cursor.fetchone()

            if not row:
                return None

            return Session(
                id=row["id"],
                title=row["title"],
                created_at=row["created_at"]
            )

    async def update(self, session: Session) -> Session:
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                "UPDATE session SET title = ? WHERE id = ?",
                (session.title, session.id,)
            )
            await self._conn.commit()
        return session
