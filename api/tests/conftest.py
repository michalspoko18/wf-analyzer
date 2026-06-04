from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from api.database import get_pool
from api.main import app


@pytest.fixture
def mock_pool():
    return AsyncMock()


@pytest.fixture
async def client(mock_pool):
    app.dependency_overrides[get_pool] = lambda: mock_pool
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
