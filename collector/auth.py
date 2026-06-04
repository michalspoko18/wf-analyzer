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
        self._token: Optional[str] = None

    async def authenticate(self) -> None:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=BASE_URL,
                timeout=30.0,
                headers={"Content-Type": "application/json"},
            )

        payload = {"Login": self._login, "Password": self._password}
        response = await self._client.post("/Auth/Login", json=payload)
        response.raise_for_status()

        data = response.json()
        user = data.get("User") or {}
        self._token = (
            data.get("token")
            or data.get("Token")
            or data.get("access_token")
            or data.get("AccessToken")
            or user.get("token")
            or user.get("Token")
            or user.get("access_token")
            or user.get("AccessToken")
            or user.get("AuthToken")
            or user.get("authToken")
        )
        if not self._token:
            raise ValueError(f"No JWT token found in login response: {data}")

        self._client.headers.update({"Authorization": f"Bearer {self._token}"})
        logger.info("Authenticated with WellFitness")

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
