import logging

import asyncpg

logger = logging.getLogger(__name__)

# Timezone used for DOW/hour bucketing
_TZ = "Europe/Warsaw"


async def aggregate_hourly(pool: asyncpg.Pool) -> None:
    """
    Upsert gym_occupancy_hourly from raw samples.
    DOW: 0 = Monday … 6 = Sunday.
    """
    async with pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO gym_occupancy_hourly
                (gym_id, dow, hour, avg_people, min_people, max_people, samples_count)
            SELECT
                gym_id,
                (EXTRACT(isodow FROM measured_at AT TIME ZONE '{_TZ}')::int - 1) AS dow,
                EXTRACT(hour  FROM measured_at AT TIME ZONE '{_TZ}')::int        AS hour,
                AVG(people_count)::float,
                MIN(people_count),
                MAX(people_count),
                COUNT(*)
            FROM gym_occupancy_samples
            GROUP BY gym_id, dow, hour
            ON CONFLICT (gym_id, dow, hour) DO UPDATE SET
                avg_people    = EXCLUDED.avg_people,
                min_people    = EXCLUDED.min_people,
                max_people    = EXCLUDED.max_people,
                samples_count = EXCLUDED.samples_count
            """
        )
    logger.info("Aggregated hourly occupancy data")


async def aggregate_daily(pool: asyncpg.Pool) -> None:
    """
    Upsert gym_occupancy_daily from hourly aggregates.
    peak_hour = hour with the highest avg_people for that gym+dow.
    """
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO gym_occupancy_daily
                (gym_id, dow, avg_people, min_people, max_people, peak_hour, samples_count)
            SELECT
                h.gym_id,
                h.dow,
                AVG(h.avg_people)::float,
                MIN(h.min_people),
                MAX(h.max_people),
                (
                    SELECT hour FROM gym_occupancy_hourly h2
                    WHERE h2.gym_id = h.gym_id AND h2.dow = h.dow
                    ORDER BY h2.avg_people DESC
                    LIMIT 1
                ) AS peak_hour,
                SUM(h.samples_count)
            FROM gym_occupancy_hourly h
            GROUP BY h.gym_id, h.dow
            ON CONFLICT (gym_id, dow) DO UPDATE SET
                avg_people    = EXCLUDED.avg_people,
                min_people    = EXCLUDED.min_people,
                max_people    = EXCLUDED.max_people,
                peak_hour     = EXCLUDED.peak_hour,
                samples_count = EXCLUDED.samples_count
            """
        )
    logger.info("Aggregated daily occupancy data")
