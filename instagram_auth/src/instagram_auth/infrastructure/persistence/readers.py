"""Narrow SQLAlchemy read adapters for connection management."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from instagram_auth.application.contracts import InstagramConnectionLister, InstagramConnectionReader
from instagram_auth.domain import InstagramConnection, InstagramConnectionId
from instagram_auth.infrastructure.persistence.mappers import InstagramConnectionRecordMapper
from instagram_auth.infrastructure.persistence.models import InstagramConnectionRecord


class SqlAlchemyInstagramConnectionReader(InstagramConnectionReader):
    """Read one explicit Instagram connection from SQLAlchemy persistence."""

    def __init__(
        self,
        session: AsyncSession,
        mapper: InstagramConnectionRecordMapper | None = None,
    ) -> None:
        self._session = session
        self._mapper = mapper or InstagramConnectionRecordMapper()

    async def get(self, connection_id: InstagramConnectionId) -> InstagramConnection | None:
        record = await self._session.get(InstagramConnectionRecord, str(connection_id.value))
        return None if record is None else self._mapper.to_domain(record)


class SqlAlchemyInstagramConnectionLister(InstagramConnectionLister):
    """List all Instagram connections for one explicit host owner."""

    def __init__(
        self,
        session: AsyncSession,
        mapper: InstagramConnectionRecordMapper | None = None,
    ) -> None:
        self._session = session
        self._mapper = mapper or InstagramConnectionRecordMapper()

    async def list_for_owner(self, owner_user_id: str) -> tuple[InstagramConnection, ...]:
        statement = (
            select(InstagramConnectionRecord)
            .where(InstagramConnectionRecord.owner_user_id == owner_user_id)
            .order_by(InstagramConnectionRecord.connected_at, InstagramConnectionRecord.id)
        )
        records = (await self._session.scalars(statement)).all()
        return tuple(self._mapper.to_domain(record) for record in records)
