import asyncio
import logging
import os
from datetime import datetime, timezone

import asyncpg
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from collector.aggregator import aggregate_daily, aggregate_hourly
from collector.auth import WellFitnessAuth
from collector.fetcher import fetch_occupancy

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

WF_LOGIN = os.environ["WF_LOGIN"]
WF_PASSWORD = os.environ["WF_PASSWORD"]
DATABASE_URL = os.environ["DATABASE_URL"]

_pool: asyncpg.Pool
_auth: WellFitnessAuth


async def collect_sample() -> None:
    try:
        samples = await fetch_occupancy(_auth)
        if not samples:
            logger.warning("No samples returned — skipping insert")
            return

        async with _pool.acquire() as conn:
            for sample in samples:
                gym = await conn.fetchrow(
                    "SELECT id FROM gyms WHERE name = $1", sample["ClubName"]
                )
                if not gym:
                    logger.error("Unknown gym name: %s", sample["ClubName"])
                    continue
                await conn.execute(
                    "INSERT INTO gym_occupancy_samples (gym_id, measured_at, people_count)"
                    " VALUES ($1, $2, $3)",
                    gym["id"],
                    datetime.now(timezone.utc),
                    sample["UsersCountCurrentlyInClub"],
                )
        logger.info("Stored %d samples", len(samples))
    except Exception:
        logger.exception("Error during sample collection")


async def run_aggregation() -> None:
    try:
        await aggregate_hourly(_pool)
        await aggregate_daily(_pool)
    except Exception:
        logger.exception("Error during aggregation")


async def main() -> None:
    global _pool, _auth

    _pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=5)
    _auth = WellFitnessAuth(WF_LOGIN, WF_PASSWORD)
    await _auth.authenticate()

    scheduler = AsyncIOScheduler(timezone="Europe/Warsaw")
    scheduler.add_job(collect_sample, "interval", minutes=5, id="collect")
    scheduler.add_job(run_aggregation, "interval", hours=1, id="aggregate")
    scheduler.start()

    logger.info("Scheduler started — sampling every 5 min, aggregating every hour")

    # Collect immediately on startup
    await collect_sample()

    try:
        await asyncio.Event().wait()
    finally:
        scheduler.shutdown()
        await _auth.close()
        await _pool.close()


if __name__ == "__main__":
    asyncio.run(main())
