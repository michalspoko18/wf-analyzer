import asyncpg
import os
from typing import Optional

_pool: Optional[asyncpg.Pool] = None


async def create_pool() -> asyncpg.Pool:
    global _pool
    _pool = await asyncpg.create_pool(
        os.environ["DATABASE_URL"],
        min_size=2,
        max_size=10,
    )
    return _pool


async def get_pool() -> asyncpg.Pool:
    assert _pool is not None, "DB pool not initialized"
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
