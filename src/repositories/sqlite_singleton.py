import aiosqlite

from src import utils


class SqliteSingleton:
    _connection: aiosqlite.Connection | None = None

    @classmethod
    async def get_conn(cls, filepath: str = "data/sqlite3.db") -> aiosqlite.Connection:
        if not cls._connection:
            cls._connection = await aiosqlite.connect(filepath)
            cls._connection.row_factory = utils.dict_factory    # type: ignore
        return cls._connection

    @classmethod
    async def initialize(cls) -> None:
        if not cls._connection:
            raise ConnectionError("Database tried to be initialized without a running connection.")
        async with cls._connection.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS session (
                    id INTEGER NOT NULL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
