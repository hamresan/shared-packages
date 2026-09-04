"""Host-owned Instagram connection association repository."""

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncEngine

from instagram_api.application.contracts import InstagramWebhookConnectionResolver
from instagram_api.domain import (
    InstagramAccountId,
    InstagramConnectionId,
)
from identity import AuthenticatedPrincipal

from .models import instagram_connection_links


class SqlAlchemyHostConnectionRegistry(InstagramWebhookConnectionResolver):
    """Stores host ownership/routing facts without reading auth package tables."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def link(
        self,
        principal: AuthenticatedPrincipal,
        connection_id: InstagramConnectionId,
        provider_account_id: InstagramAccountId,
    ) -> None:
        async with self._engine.begin() as connection:
            await connection.execute(
                insert(instagram_connection_links).values(
                    connection_id=str(connection_id),
                    owner_user_id=str(principal.user_id),
                    provider_account_id=str(provider_account_id),
                )
            )

    async def resolve(
        self,
        provider_account_id: InstagramAccountId,
    ) -> InstagramConnectionId:
        async with self._engine.connect() as connection:
            value = await connection.scalar(
                select(instagram_connection_links.c.connection_id).where(
                    instagram_connection_links.c.provider_account_id
                    == str(provider_account_id)
                )
            )
        if not isinstance(value, str):
            raise LookupError(
                f"No host connection for provider account: {provider_account_id}"
            )
        return InstagramConnectionId(value)

    async def list_owner_connections(
        self,
        principal: AuthenticatedPrincipal,
    ) -> tuple[InstagramConnectionId, ...]:
        async with self._engine.connect() as connection:
            rows = await connection.scalars(
                select(instagram_connection_links.c.connection_id)
                .where(
                    instagram_connection_links.c.owner_user_id
                    == str(principal.user_id)
                )
                .order_by(instagram_connection_links.c.connection_id)
            )
            values = tuple(rows.all())
        return tuple(InstagramConnectionId(value) for value in values)
