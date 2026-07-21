import aiosqlite

from src.models.session import Session


class SessionRepository:
    def __init__(self, conn: aiosqlite.Connection) -> None:
        self._conn = conn

    async def add(self, session: Session) -> int:
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO session (title, created_at) VALUES (?, ?);",
                (session.title, session.created_at)
            )
            return cursor.lastrowid or -1

    async def remove(self, session: Session) -> int:
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM session WHERE id = ?;",
                (session.id,)
            )
            return cursor.rowcount

    async def list(self) -> list[Session]:
        async with self._conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM session;")
