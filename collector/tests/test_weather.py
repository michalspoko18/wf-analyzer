from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from collector.weather import GYM_COORDS, fetch_weather


def _make_response(gym_name: str, temperature: float, rain: float) -> MagicMock:
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "current": {
            "temperature_2m": temperature,
            "rain": rain,
        }
    }
    resp.raise_for_status = MagicMock()
    return resp


async def test_fetch_weather_returns_one_reading_per_gym():
    responses = [
        _make_response("Stargard, Zachód", 15.0, 0.0),
        _make_response("Szczecin, Hanza", 16.5, 0.2),
        _make_response("Szczecin, Słoneczne Centrum", 16.5, 0.2),
    ]

    mock_client = AsyncMock()
    mock_client.get.side_effect = responses
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("collector.weather.httpx.AsyncClient", return_value=mock_client):
        result = await fetch_weather()

    assert len(result) == len(GYM_COORDS)
    names = {r["gym_name"] for r in result}
    assert names == set(GYM_COORDS.keys())


async def test_fetch_weather_fields():
    responses = [
        _make_response(gym, 20.0 + i, float(i) * 0.1)
        for i, gym in enumerate(GYM_COORDS)
    ]

    mock_client = AsyncMock()
    mock_client.get.side_effect = responses
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("collector.weather.httpx.AsyncClient", return_value=mock_client):
        result = await fetch_weather()

    for reading in result:
        assert "gym_name" in reading
        assert "temperature" in reading
        assert "rain" in reading


async def test_fetch_weather_skips_failed_gym():
    """A gym that throws should be skipped; others are still returned."""
    mock_client = AsyncMock()

    call_count = 0
    gyms = list(GYM_COORDS.keys())

    async def side_effect(*args, **kwargs):
        nonlocal call_count
        gym = gyms[call_count]
        call_count += 1
        if gym == "Szczecin, Hanza":
            raise Exception("network error")
        return _make_response(gym, 18.0, 0.0)

    mock_client.get.side_effect = side_effect
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("collector.weather.httpx.AsyncClient", return_value=mock_client):
        result = await fetch_weather()

    assert len(result) == len(GYM_COORDS) - 1
    assert all(r["gym_name"] != "Szczecin, Hanza" for r in result)
