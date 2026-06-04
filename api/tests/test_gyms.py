from datetime import datetime, timezone


async def test_list_gyms_returns_all(client, mock_pool):
    mock_pool.fetch.return_value = [
        {"id": 1, "name": "Stargard, Zachód", "address": "Szczecińska 45"},
        {"id": 2, "name": "Szczecin, Hanza", "address": "Wyzwolenia 46"},
        {"id": 3, "name": "Szczecin, Słoneczne Centrum", "address": "Andrzeja Struga 18"},
    ]

    resp = await client.get("/api/gyms")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    assert data[0]["name"] == "Stargard, Zachód"


async def test_list_gyms_empty(client, mock_pool):
    mock_pool.fetch.return_value = []

    resp = await client.get("/api/gyms")

    assert resp.status_code == 200
    assert resp.json() == []


async def test_current_occupancy_returns_latest_sample(client, mock_pool):
    mock_pool.fetchrow.side_effect = [
        {"id": 1, "name": "Stargard, Zachód", "address": "Szczecińska 45"},
        {
            "people_count": 42,
            "measured_at": datetime(2026, 6, 4, 10, 0, tzinfo=timezone.utc),
        },
    ]

    resp = await client.get("/api/gyms/1/current")

    assert resp.status_code == 200
    data = resp.json()
    assert data["people_count"] == 42
    assert data["gym"]["name"] == "Stargard, Zachód"
    assert "measured_at" in data


async def test_current_occupancy_no_sample(client, mock_pool):
    mock_pool.fetchrow.side_effect = [
        {"id": 1, "name": "Stargard, Zachód", "address": "Szczecińska 45"},
        None,
    ]

    resp = await client.get("/api/gyms/1/current")

    assert resp.status_code == 200
    data = resp.json()
    assert data["people_count"] is None
    assert data["measured_at"] is None


async def test_current_occupancy_gym_not_found(client, mock_pool):
    mock_pool.fetchrow.return_value = None

    resp = await client.get("/api/gyms/999/current")

    assert resp.status_code == 404
