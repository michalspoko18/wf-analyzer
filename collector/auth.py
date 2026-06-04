import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://wellfitness.perfectgym.pl/ClientPortal2"


class WellFitnessAuth:
    def __init__(self, login: str, password: str) -> None:
        self._login = login
        self._password = password
        self._client: Optional[httpx.AsyncClient] = None
        self._authenticated: bool = False

    async def authenticate(self) -> None:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=BASE_URL,
                timeout=30.0,
                headers={"Content-Type": "application/json"},
                follow_redirects=True,
            )

        payload = {"Login": self._login, "Password": self._password}
        response = await self._client.post("/Auth/Login", json=payload)
        response.raise_for_status()

        data = response.json()
        user = data.get("User")
        if not user:
            raise ValueError(f"Login failed, unexpected response: {data}")

        self._authenticated = True
        logger.info(
            "Authenticated as %s %s (cookies: %d)",
            user.get("Member", {}).get("FirstName", "?"),
            user.get("Member", {}).get("LastName", "?"),
            len(self._client.cookies),
        )

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None or not self._authenticated:
            await self.authenticate()
        assert self._client is not None
        return self._client

    async def invalidate(self) -> None:
        """Force re-authentication on next get_client() call."""
        self._authenticated = False

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
            self._authenticated = False


    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._token is None:
            await self.authenticate()
        assert self._client is not None
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
            self._token = None
