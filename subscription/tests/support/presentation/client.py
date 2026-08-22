from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from subscription.presentation import FastApiSubscriptionAdapter


@asynccontextmanager
async def subscription_test_client(
    adapter: FastApiSubscriptionAdapter,
) -> AsyncIterator[AsyncClient]:
    app = FastAPI()
    adapter.install(app)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
