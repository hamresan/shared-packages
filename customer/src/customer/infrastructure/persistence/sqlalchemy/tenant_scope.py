"""Set tenant scope only inside an active PostgreSQL transaction."""

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class PostgreSqlTenantScope:
    async def apply(self, session: AsyncSession, business_id: UUID) -> None:
        bind = session.get_bind()
        if bind.dialect.name != "postgresql":
            return
        await session.execute(
            text("SELECT set_config('app.customer_business_id', :business_id, true)"),
            {"business_id": str(business_id)},
        )
