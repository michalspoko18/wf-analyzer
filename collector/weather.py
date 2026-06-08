import logging

import httpx

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Gym name → (latitude, longitude)
GYM_COORDS: dict[str, tuple[float, float]] = {
    "Stargard, Zachód":            (53.4289, 14.5530),
    "Szczecin, Hanza":             (53.2820, 14.9663),
    "Szczecin, Słoneczne Centrum": (53.2820, 14.9663),
}


async def fetch_weather() -> list[dict]:
    """
    Fetch current temperature and rain from Open-Meteo for each monitored gym.
    Returns list of dicts with keys: gym_name, temperature, rain.
    """
    results: list[dict] = []
    async with httpx.AsyncClient(timeout=15.0) as client:
        for gym_name, (lat, lon) in GYM_COORDS.items():
            try:
                response = await client.get(
                    OPEN_METEO_URL,
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "current": "temperature_2m,rain",
                    },
                )
                response.raise_for_status()
                data = response.json()
                current = data.get("current", {})
                results.append(
                    {
                        "gym_name": gym_name,
                        "temperature": current["temperature_2m"],
                        "rain": current["rain"],
                    }
                )
            except Exception:
                logger.exception("Failed to fetch weather for %s", gym_name)
    return results
