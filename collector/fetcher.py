import logging

from collector.auth import WellFitnessAuth

logger = logging.getLogger(__name__)

MEMBERS_URL = "/Clubs/Clubs/GetMembersInClubs"

MONITORED_CLUBS = frozenset(
    {
        "Stargard, Zachód",
        "Szczecin, Hanza",
        "Szczecin, Słoneczne Centrum",
    }
)


async def fetch_occupancy(auth: WellFitnessAuth) -> list[dict]:
    """
    Fetch current occupancy and return only the 3 monitored clubs.
    On 401 re-authenticates and retries once.
    """
    for attempt in range(2):
        client = await auth.get_client()
        response = await client.get(MEMBERS_URL)

        if response.status_code == 401 and attempt == 0:
            logger.warning("Got 401, re-authenticating…")
            await auth.authenticate()
            continue

        response.raise_for_status()
        clubs: list[dict] = response.json().get("UsersInClubList", [])
        filtered = [c for c in clubs if c.get("ClubName") in MONITORED_CLUBS]

        if len(filtered) != len(MONITORED_CLUBS):
            found = {c["ClubName"] for c in filtered}
            missing = MONITORED_CLUBS - found
            logger.warning("Clubs missing from API response: %s", missing)

        return filtered

    return []
