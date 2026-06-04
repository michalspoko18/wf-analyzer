from datetime import datetime, timezone


async def test_history_returns_samples(client, mock_pool):
    mock_pool.fetchrow.return_value = {"id": 1}
    mock_pool.fetch.return_value = [
        {"measured_at": datetime(2026, 6, 4, 8, 0, tzinfo=timezone.utc), "people_count": 10},
        {"measured_at": datetime(2026, 6, 4, 9, 0, tzinfo=timezone.utc), "people_count": 20},
    ]

    resp = await client.get("/api/gyms/1/history")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["people_count"] == 10
    assert "measured_at" in data[0]


async def test_history_gym_not_found(client, mock_pool):
    mock_pool.fetchrow.return_value = None

    resp = await client.get("/api/gyms/999/history")

    assert resp.status_code == 404


async def test_hourly_returns_data(client, mock_pool):
    mock_pool.fetchrow.return_value = {"id": 1}
    mock_pool.fetch.return_value = [
        {"dow": 0, "hour": 8, "avg_people": 15.5, "min_people": 10, "max_people": 20, "samples_count": 4},
    ]

    resp = await client.get("/api/gyms/1/hourly")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["dow"] == 0
    assert data[0]["hour"] == 8


async def test_hourly_gym_not_found(client, mock_pool):
    mock_pool.fetchrow.return_value = None

    resp = await client.get("/api/gyms/999/hourly")

    assert resp.status_code == 404


async def test_daily_returns_data(client, mock_pool):
    mock_pool.fetchrow.return_value = {"id": 1}
    mock_pool.fetch.return_value = [
        {"dow": 1, "avg_people": 30.0, "min_people": 20, "max_people": 50, "peak_hour": 18, "samples_count": 10},
    ]

    resp = await client.get("/api/gyms/1/daily")

    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["peak_hour"] == 18


async def test_daily_gym_not_found(client, mock_pool):
    mock_pool.fetchrow.return_value = None

    resp = await client.get("/api/gyms/999/daily")

    assert resp.status_code == 404
