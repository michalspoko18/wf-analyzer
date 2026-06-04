from unittest.mock import AsyncMock, MagicMock

from collector.aggregator import aggregate_daily, aggregate_hourly


def _make_pool() -> tuple[MagicMock, AsyncMock]:
    """Return (pool, conn) where pool.acquire() is an async context manager."""
    conn = AsyncMock()
    acquire_ctx = MagicMock()
    acquire_ctx.__aenter__ = AsyncMock(return_value=conn)
    acquire_ctx.__aexit__ = AsyncMock(return_value=None)
    pool = MagicMock()
    pool.acquire.return_value = acquire_ctx
    return pool, conn


async def test_aggregate_hourly_executes_upsert():
    pool, conn = _make_pool()

    await aggregate_hourly(pool)

    conn.execute.assert_called_once()
    sql: str = conn.execute.call_args[0][0]
    assert "INSERT INTO gym_occupancy_hourly" in sql
    assert "ON CONFLICT" in sql
    assert "avg_people" in sql


async def test_aggregate_hourly_includes_dow_and_hour():
    pool, conn = _make_pool()

    await aggregate_hourly(pool)

    sql: str = conn.execute.call_args[0][0]
    assert "dow" in sql
    assert "hour" in sql


async def test_aggregate_daily_executes_upsert():
    pool, conn = _make_pool()

    await aggregate_daily(pool)

    conn.execute.assert_called_once()
    sql: str = conn.execute.call_args[0][0]
    assert "INSERT INTO gym_occupancy_daily" in sql
    assert "ON CONFLICT" in sql
    assert "peak_hour" in sql


async def test_aggregate_daily_includes_peak_hour_subquery():
    pool, conn = _make_pool()

    await aggregate_daily(pool)

    sql: str = conn.execute.call_args[0][0]
    assert "gym_occupancy_hourly" in sql
    assert "ORDER BY" in sql
