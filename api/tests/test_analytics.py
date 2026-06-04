async def test_best_times_returns_grouped_by_gym(client, mock_pool):
    mock_pool.fetch.return_value = [
        {"gym_id": 1, "gym_name": "Stargard, Zachód", "dow": 0, "hour": 7, "avg_people": 5.0, "samples_count": 3},
        {"gym_id": 1, "gym_name": "Stargard, Zachód", "dow": 2, "hour": 6, "avg_people": 6.0, "samples_count": 2},
        {"gym_id": 2, "gym_name": "Szczecin, Hanza", "dow": 5, "hour": 9, "avg_people": 20.0, "samples_count": 4},
    ]

    resp = await client.get("/api/analytics/best-times")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2

    gym1 = next(d for d in data if d["gym_id"] == 1)
    assert len(gym1["best_times"]) == 2
    assert gym1["best_times"][0]["dow_name"] == "Monday"
    assert gym1["best_times"][0]["hour"] == 7


async def test_best_times_empty(client, mock_pool):
    mock_pool.fetch.return_value = []

    resp = await client.get("/api/analytics/best-times")

    assert resp.status_code == 200
    assert resp.json() == []


async def test_health_endpoint(client, mock_pool):
    resp = await client.get("/health")

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
