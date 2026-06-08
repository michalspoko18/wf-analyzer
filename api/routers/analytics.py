import asyncpg
from fastapi import APIRouter, Depends, Query

from api.database import get_pool

router = APIRouter(tags=["analytics"])

_DOW_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@router.get("/analytics/best-times")
async def best_times(
    dows: list[int] = Query(default=list(range(7))),
    hour_from: int = Query(default=0, ge=0, le=23),
    hour_to: int = Query(default=23, ge=0, le=23),
    max_people: float = Query(default=80.0, gt=0),
    limit: int = Query(default=5, ge=1, le=100),
    pool: asyncpg.Pool = Depends(get_pool),
):
    """
    Quietest hours per gym filtered by day-of-week, hour range and avg occupancy cap.
    Returns all matching slots ordered by avg_people ASC, minimum 2 samples.
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
              AND h.dow        = ANY($1::int[])
              AND h.hour      >= $2
              AND h.hour      <= $3
              AND h.avg_people < $4
        )
        SELECT gym_id, gym_name, dow, hour, avg_people, samples_count
        FROM ranked
        WHERE rn <= $5
        ORDER BY gym_id, avg_people ASC
        """,
        dows,
        hour_from,
        hour_to,
        max_people,
        limit,
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
