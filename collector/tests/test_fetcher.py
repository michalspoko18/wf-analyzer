from unittest.mock import AsyncMock, MagicMock

import pytest

from collector.auth import WellFitnessAuth
from collector.fetcher import MONITORED_CLUBS, fetch_occupancy

_ALL_CLUBS_RESPONSE = {
    "UsersInClubList": [
        {
            "ClubName": "Stargard, Zachód",
            "ClubAddress": "Szczecińska 45",
            "UsersLimit": None,
            "UsersCountCurrentlyInClub": 12,
        },
        {
            "ClubName": "Szczecin, Hanza",
            "ClubAddress": "Wyzwolenia 46",
            "UsersLimit": None,
            "UsersCountCurrentlyInClub": 55,
        },
        {
            "ClubName": "Szczecin, Słoneczne Centrum",
            "ClubAddress": "Andrzeja Struga 18",
            "UsersLimit": None,
            "UsersCountCurrentlyInClub": 30,
        },
        {
            "ClubName": "Inny Klub",
            "ClubAddress": "Inna 1",
            "UsersLimit": None,
            "UsersCountCurrentlyInClub": 200,
        },
    ]
}


def _make_response(status_code: int, body: dict | None = None) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = body or {}
    resp.raise_for_status = MagicMock()
    return resp


async def test_fetch_occupancy_returns_only_monitored_clubs():
    mock_client = AsyncMock()
    mock_client.get.return_value = _make_response(200, _ALL_CLUBS_RESPONSE)

    mock_auth = AsyncMock(spec=WellFitnessAuth)
    mock_auth.get_client.return_value = mock_client

    result = await fetch_occupancy(mock_auth)

    assert len(result) == 3
    names = {r["ClubName"] for r in result}
    assert names == set(MONITORED_CLUBS)


async def test_fetch_occupancy_excludes_unmonitored_clubs():
    mock_client = AsyncMock()
    mock_client.get.return_value = _make_response(200, _ALL_CLUBS_RESPONSE)

    mock_auth = AsyncMock(spec=WellFitnessAuth)
    mock_auth.get_client.return_value = mock_client

    result = await fetch_occupancy(mock_auth)

    assert all(r["ClubName"] != "Inny Klub" for r in result)


async def test_fetch_occupancy_retries_on_401():
    ok_resp = _make_response(200, _ALL_CLUBS_RESPONSE)
    unauth_resp = _make_response(401)

    mock_client = AsyncMock()
    mock_client.get.side_effect = [unauth_resp, ok_resp]

    mock_auth = AsyncMock(spec=WellFitnessAuth)
    mock_auth.get_client.return_value = mock_client

    result = await fetch_occupancy(mock_auth)

    mock_auth.authenticate.assert_called_once()
    assert len(result) == 3


async def test_fetch_occupancy_returns_empty_after_two_401s():
    """After two failed attempts the function gives up and returns []."""
    unauth_resp = _make_response(401)

    mock_client = AsyncMock()
    mock_client.get.return_value = unauth_resp

    mock_auth = AsyncMock(spec=WellFitnessAuth)
    mock_auth.get_client.return_value = mock_client

    result = await fetch_occupancy(mock_auth)

    assert result == []
