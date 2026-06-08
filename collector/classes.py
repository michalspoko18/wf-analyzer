import logging
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from collector.auth import WellFitnessAuth

logger = logging.getLogger(__name__)

CLASSES_URL = "/Classes/ClassCalendar/DailyClasses"
WARSAW = ZoneInfo("Europe/Warsaw")

# Gym name → PerfectGym club ID
CLUB_IDS: dict[str, int] = {
    "Stargard, Zachód":            103,
    "Szczecin, Hanza":             78,
    "Szczecin, Słoneczne Centrum": 80,
}


def _parse_duration_minutes(iso_duration: str) -> int:
    """Parse ISO 8601 duration like 'PT55M' or 'PT1H30M' to total minutes."""
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?", iso_duration)
    if not m:
        return 0
    hours = int(m.group(1) or 0)
    minutes = int(m.group(2) or 0)
    return hours * 60 + minutes


async def fetch_classes(auth: WellFitnessAuth, date: str | None = None) -> list[dict]:
    """
    Fetch today's class schedule for all monitored gyms from the PerfectGym API.

    Returns a flat list of class dicts, each with keys:
        gym_name, class_id, name, trainer, start_time (datetime),
        end_time (datetime), status, capacity, spots_available.
    """
    if date is None:
        date = datetime.now(WARSAW).strftime("%Y-%m-%d")

    results: list[dict] = []

    for gym_name, club_id in CLUB_IDS.items():
        try:
            client = await auth.get_client()
            payload = {
                "clubId": club_id,
                "date": date,
                "categoryId": None,
                "timeTableId": None,
                "trainerId": None,
            }
            response = await client.post(CLASSES_URL, json=payload)

            if response.status_code == 401:
                logger.warning("Got 401 fetching classes for %s, re-authenticating…", gym_name)
                await auth.invalidate()
                await auth.authenticate()
                client = await auth.get_client()
                response = await client.post(CLASSES_URL, json=payload)

            response.raise_for_status()
            data = response.json()

            for hour_block in data.get("CalendarData", []):
                for cls in hour_block.get("Classes", []):
                    duration_min = _parse_duration_minutes(cls.get("Duration", ""))
                    start_dt = datetime.fromisoformat(cls["StartTime"]).replace(tzinfo=WARSAW)
                    end_dt = start_dt + timedelta(minutes=duration_min)
                    booking = cls.get("BookingIndicator") or {}
                    results.append(
                        {
                            "gym_name": gym_name,
                            "class_id": cls["Id"],
                            "name": cls["Name"],
                            "trainer": cls.get("Trainer"),
                            "start_time": start_dt,
                            "end_time": end_dt,
                            "status": cls["Status"],
                            "capacity": booking.get("Limit"),
                            "spots_available": booking.get("Available"),
                        }
                    )
        except Exception:
            logger.exception("Failed to fetch classes for %s", gym_name)

    return results
