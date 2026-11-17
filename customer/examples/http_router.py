"""Host composition example for the optional FastAPI adapter."""

from collections.abc import Awaitable, Callable

from fastapi import FastAPI

from customer import CustomerActor, CustomerModule
from customer.presentation.http import create_customer_router


def mount_customer_api(
    app: FastAPI,
    module: CustomerModule,
    authenticated_actor: Callable[..., CustomerActor | Awaitable[CustomerActor]],
) -> None:
    """The host must authenticate before producing its trusted CustomerActor."""
    app.include_router(create_customer_router(module, authenticated_actor))
