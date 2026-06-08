from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from zoneinfo import ZoneInfo

import pytest

from collector.auth import WellFitnessAuth
from collector.classes import CLUB_IDS, _parse_duration_minutes, fetch_classes

WARSAW = ZoneInfo("Europe/Warsaw")

_DAILY_CLASSES_RESPONSE = {
    "CalendarData": [
        {
            "Hour": "1900-01-01T17:00:00",
            "Classes": [
                {
                    "Id": 891708,
                    "Status": "Bookable",
                    "StatusReason": None,
                    "Name": "WELL START",
                    "StartTime": "2026-06-09T17:00:00",
                    "Duration": "PT55M",
                    "BookingIndicator": {"Indicator": 5, "Limit": 6, "Available": 6},
                    "Trainer": "Adam Kobyłt",
                    "Users": [],
                    "HasRelatives": False,
                    "AllowBookSeatNumber": False,
                    "IsClassAvailableOnline": False,
                    "ClassRatingSummaryInfo": None,
                    "BookingPreReservationId": None,
                }
            ],
        },
        {
            "Hour": "1900-01-01T18:00:00",
            "Classes": [
                {
                    "Id": 600652,
                    "Status": "Bookable",
                    "StatusReason": None,
                    "Name": "ROWERY (basic)",
                    "StartTime": "2026-06-09T18:00:00",
                    "Duration": "PT55M",
                    "BookingIndicator": {"Indicator": 2, "Limit": 20, "Available": 6},
                    "Trainer": "Oskar Mościcki",
                    "Users": [],
                    "HasRelatives": False,
                    "AllowBookSeatNumber": False,
                    "IsClassAvailableOnline": False,
                    "ClassRatingSummaryInfo": None,
                    "BookingPreReservationId": None,
                }
            ],
        },
    ],
    "PagerData": {},
}


def _make_response(status_code: int, body: dict | None = None) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = body or {}
    resp.raise_for_status = MagicMock()
    return resp


@pytest.mark.parametrize(
    "duration,expected",
    [
        ("PT55M", 55),
        ("PT1H", 60),
        ("PT1H30M", 90),
        ("PT0M", 0),
        ("", 0),
    ],
)
def test_parse_duration_minutes(duration, expected):
    assert _parse_duration_minutes(duration) == expected


async def test_fetch_classes_returns_flat_list():
    mock_client = AsyncMock()
    mock_client.post.return_value = _make_response(200, _DAILY_CLASSES_RESPONSE)

    mock_auth = AsyncMock(spec=WellFitnessAuth)
    mock_auth.get_client.return_value = mock_client

    result = await fetch_classes(mock_auth, date="2026-06-09")

    # 3 gyms × 2 classes each
    assert len(result) == len(CLUB_IDS) * 2


async def test_fetch_classes_fields_and_timezone():
    mock_client = AsyncMock()
    mock_client.post.return_value = _make_response(200, _DAILY_CLASSES_RESPONSE)

    mock_auth = AsyncMock(spec=WellFitnessAuth)
    mock_auth.get_client.return_value = mock_client

    result = await fetch_classes(mock_auth, date="2026-06-09")
    cls = result[0]

    assert cls["class_id"] == 891708
    assert cls["name"] == "WELL START"
    assert cls["trainer"] == "Adam Kobyłt"
    assert cls["status"] == "Bookable"
    assert cls["capacity"] == 6
    assert cls["spots_available"] == 6
    assert isinstance(cls["start_time"], datetime)
    assert cls["start_time"].tzinfo is not None
    assert isinstance(cls["end_time"], datetime)
    # 17:00 + 55 min = 17:55
    assert cls["end_time"].hour == 17
    assert cls["end_time"].minute == 55


async def test_fetch_classes_skips_failed_gym():
    call_count = 0
    gyms = list(CLUB_IDS.keys())

    async def post_side_effect(*args, **kwargs):
        nonlocal call_count
        gym = gyms[call_count]
        call_count += 1
        if gym == "Szczecin, Hanza":
            raise Exception("network error")
        return _make_response(200, _DAILY_CLASSES_RESPONSE)

    mock_client = AsyncMock()
    mock_client.post.side_effect = post_side_effect

    mock_auth = AsyncMock(spec=WellFitnessAuth)
    mock_auth.get_client.return_value = mock_client

    result = await fetch_classes(mock_auth, date="2026-06-09")

    # Only 2 gyms succeeded × 2 classes
    assert len(result) == (len(CLUB_IDS) - 1) * 2
    assert all(r["gym_name"] != "Szczecin, Hanza" for r in result)
