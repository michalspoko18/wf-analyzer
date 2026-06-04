import asyncpg
from fastapi import APIRouter, Depends, HTTPException

from api.database import get_pool

router = APIRouter(tags=["gyms"])


@router.get("/gyms")
async def list_gyms(pool: asyncpg.Pool = Depends(get_pool)):
    rows = await pool.fetch("SELECT id, name, address FROM gyms ORDER BY id")
    return [dict(r) for r in rows]


@router.get("/gyms/{gym_id}/current")
async def current_occupancy(gym_id: int, pool: asyncpg.Pool = Depends(get_pool)):
    gym = await pool.fetchrow(
        "SELECT id, name, address FROM gyms WHERE id = $1", gym_id
    )
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")

    sample = await pool.fetchrow(
        """
        SELECT people_count, measured_at
        FROM gym_occupancy_samples
        WHERE gym_id = $1
        ORDER BY measured_at DESC
        LIMIT 1
        """,
        gym_id,
    )

    return {
        "gym": dict(gym),
        "people_count": sample["people_count"] if sample else None,
        "measured_at": sample["measured_at"].isoformat() if sample else None,
    }
