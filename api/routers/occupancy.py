from datetime import datetime
from typing import Optional

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query

from api.database import get_pool

router = APIRouter(tags=["occupancy"])


@router.get("/gyms/{gym_id}/history")
async def history(
    gym_id: int,
    from_: Optional[datetime] = Query(None, alias="from"),
    to: Optional[datetime] = Query(None),
    pool: asyncpg.Pool = Depends(get_pool),
):
    gym = await pool.fetchrow("SELECT id FROM gyms WHERE id = $1", gym_id)
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")

    query = (
        "SELECT measured_at, people_count FROM gym_occupancy_samples WHERE gym_id = $1"
    )
    params: list = [gym_id]

    if from_:
        params.append(from_)
        query += f" AND measured_at >= ${len(params)}"
    if to:
        params.append(to)
        query += f" AND measured_at <= ${len(params)}"

    query += " ORDER BY measured_at"
    rows = await pool.fetch(query, *params)
    return [
        {"measured_at": r["measured_at"].isoformat(), "people_count": r["people_count"]}
        for r in rows
    ]


@router.get("/gyms/{gym_id}/hourly")
async def hourly(gym_id: int, pool: asyncpg.Pool = Depends(get_pool)):
    gym = await pool.fetchrow("SELECT id FROM gyms WHERE id = $1", gym_id)
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")

    rows = await pool.fetch(
        """
        SELECT dow, hour, avg_people, min_people, max_people, samples_count
        FROM gym_occupancy_hourly
        WHERE gym_id = $1
        ORDER BY dow, hour
        """,
        gym_id,
    )
    return [dict(r) for r in rows]


@router.get("/gyms/{gym_id}/daily")
async def daily(gym_id: int, pool: asyncpg.Pool = Depends(get_pool)):
    gym = await pool.fetchrow("SELECT id FROM gyms WHERE id = $1", gym_id)
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")

    rows = await pool.fetch(
        """
        SELECT dow, avg_people, min_people, max_people, peak_hour, samples_count
        FROM gym_occupancy_daily
        WHERE gym_id = $1
        ORDER BY dow
        """,
        gym_id,
    )
    return [dict(r) for r in rows]
