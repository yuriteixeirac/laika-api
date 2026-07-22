import asyncio

import aiosqlite

from src import utils


class SqliteSingleton:
    _asyncio_lock = asyncio.Lock()
    _connection: aiosqlite.Connection | None = None

    @classmethod
    async def get_conn(cls, filepath: str = "data/sqlite3.db") -> aiosqlite.Connection:
        async with cls._asyncio_lock:
            if not cls._connection:
                cls._connection = await aiosqlite.connect(filepath)
                cls._connection.row_factory = utils.dict_factory    # type: ignore
                await cls._initialize()
        return cls._connection

    @classmethod
    async def _initialize(cls) -> None:
        if not cls._connection:
            raise ConnectionError("Database tried to be initialized without a running connection.")
        async with cls._connection.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS session (
                    id INTEGER NOT NULL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );""")

            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS message (
                    id INTEGER NOT NULL PRIMARY KEY,
                    content TEXT NOT NULL,
                    role VARCHAR(16) NOT NULL,
                    tool_calls TEXT, -- JSON,
                    tool_call_id VARCHAR(255),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                    session_id INTEGER NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES session(id)
                )
            """)
            await cls._connection.commit()
