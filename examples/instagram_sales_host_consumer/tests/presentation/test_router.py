"""FastAPI selected-connection route test."""

import asyncio
from uuid import UUID

from fastapi import FastAPI
import httpx

from instagram_api.application.contracts import InstagramAccountReader
from instagram_api.domain import (
    InstagramAccount,
    InstagramAccountId,
    InstagramConnectionId,
)
from instagram_sales_host_consumer_app.presentation import create_reference_router


class FakeAccountReader(InstagramAccountReader):
    """Minimal public-contract fake for the route adapter."""

    async def get_account(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramAccount:
        return InstagramAccount(
            id=InstagramAccountId(f"provider-{connection_id}"),
            username="selected_shop",
            biography="Selected connection",
        )


def test_fastapi_route_reads_explicit_selected_connection() -> None:
    async def scenario() -> None:
        app = FastAPI()
        app.include_router(create_reference_router(FakeAccountReader()))
        connection_id = str(UUID("00000000-0000-0000-0000-000000000011"))
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.get(
                f"/instagram/connections/{connection_id}/account"
            )

        assert response.status_code == 200
        assert response.json()["username"] == "selected_shop"
        assert response.json()["id"] == f"provider-{connection_id}"

    asyncio.run(scenario())
