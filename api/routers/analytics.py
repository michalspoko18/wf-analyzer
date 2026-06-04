import asyncpg
from fastapi import APIRouter, Depends

from api.database import get_pool

router = APIRouter(tags=["analytics"])

_DOW_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@router.get("/analytics/best-times")
async def best_times(pool: asyncpg.Pool = Depends(get_pool)):
    """
    Top-5 quietest hours per gym (by lowest avg_people), minimum 2 samples.
    """
    rows = await pool.fetch(
        """
        WITH ranked AS (
            SELECT
                h.gym_id,
                g.name  AS gym_name,
                h.dow,
                h.hour,
                h.avg_people,
                h.samples_count,
                ROW_NUMBER() OVER (
                    PARTITION BY h.gym_id
                    ORDER BY h.avg_people ASC
                ) AS rn
            FROM gym_occupancy_hourly h
            JOIN gyms g ON g.id = h.gym_id
            WHERE h.samples_count >= 2
        )
        SELECT gym_id, gym_name, dow, hour, avg_people, samples_count
        FROM ranked
        WHERE rn <= 5
        ORDER BY gym_id, avg_people
        """
    )

    result: dict = {}
    for row in rows:
        gid = row["gym_id"]
        if gid not in result:
            result[gid] = {"gym_id": gid, "gym_name": row["gym_name"], "best_times": []}
        result[gid]["best_times"].append(
            {
                "dow": row["dow"],
                "dow_name": _DOW_NAMES[row["dow"]],
                "hour": row["hour"],
                "avg_people": round(row["avg_people"], 1),
                "samples_count": row["samples_count"],
            }
        )

    return list(result.values())
