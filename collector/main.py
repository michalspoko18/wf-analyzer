import asyncio
import logging
import os
from datetime import datetime, timezone

import asyncpg
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from collector.aggregator import aggregate_daily, aggregate_hourly
from collector.auth import WellFitnessAuth
from collector.classes import fetch_classes
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


async def collect_classes() -> None:
    try:
        classes = await fetch_classes(_auth)
        if not classes:
            logger.warning("No classes returned — skipping upsert")
            return

        async with _pool.acquire() as conn:
            for cls in classes:
                gym = await conn.fetchrow(
                    "SELECT id FROM gyms WHERE name = $1", cls["gym_name"]
                )
                if not gym:
                    logger.error("Unknown gym name: %s", cls["gym_name"])
                    continue
                await conn.execute(
                    """
                    INSERT INTO gym_classes
                        (class_id, gym_id, name, trainer, start_time, end_time,
                         status, capacity, spots_available, last_updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW())
                    ON CONFLICT (class_id) DO UPDATE SET
                        status          = EXCLUDED.status,
                        spots_available = EXCLUDED.spots_available,
                        last_updated_at = EXCLUDED.last_updated_at
                    """,
                    cls["class_id"],
                    gym["id"],
                    cls["name"],
                    cls["trainer"],
                    cls["start_time"],
                    cls["end_time"],
                    cls["status"],
                    cls["capacity"],
                    cls["spots_available"],
                )
        logger.info("Upserted %d classes", len(classes))
    except Exception:
        logger.exception("Error during classes collection")


async def main() -> None:
    global _pool, _auth

    _pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=5)
    _auth = WellFitnessAuth(WF_LOGIN, WF_PASSWORD)
    await _auth.authenticate()

    scheduler = AsyncIOScheduler(timezone="Europe/Warsaw")
    scheduler.add_job(collect_sample, "interval", minutes=5, id="collect")
    scheduler.add_job(run_aggregation, "interval", hours=1, id="aggregate")
    scheduler.add_job(collect_classes, "interval", hours=1, id="classes")
    scheduler.start()

    logger.info("Scheduler started — sampling every 5 min, aggregating every hour, classes every hour")

    # Collect immediately on startup
    await collect_sample()
    await collect_classes()

    try:
        await asyncio.Event().wait()
    finally:
        scheduler.shutdown()
        await _auth.close()
        await _pool.close()


if __name__ == "__main__":
    asyncio.run(main())
