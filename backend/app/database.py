import asyncpg
from app.config import settings

_pool: asyncpg.Pool | None = None
_schema_ready = False


async def _ensure_schema(pool: asyncpg.Pool) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            """
            ALTER TABLE questions
            ADD COLUMN IF NOT EXISTS tags text[] NOT NULL DEFAULT '{}'::text[]
            """
        )
        await conn.execute(
            """
            UPDATE questions
            SET tags = '{}'::text[]
            WHERE tags IS NULL
            """
        )
        await conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_questions_tags_gin
            ON questions
            USING gin (tags)
            """
        )


async def get_pool() -> asyncpg.Pool:
    global _pool, _schema_ready
    if _pool is None:
        _pool = await asyncpg.create_pool(dsn=settings.database_url)
    if not _schema_ready:
        await _ensure_schema(_pool)
        _schema_ready = True
    return _pool


async def close_pool() -> None:
    global _pool, _schema_ready
    if _pool is not None:
        await _pool.close()
        _pool = None
        _schema_ready = False
