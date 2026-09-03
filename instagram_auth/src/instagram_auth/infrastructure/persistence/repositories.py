"""Async SQLAlchemy repositories for Instagram authorization persistence."""

from typing import cast

from sqlalchemy import select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from instagram_auth.application.contracts import (
    InstagramConnectionRepository,
    InstagramCredentialRepository,
)
from instagram_auth.application.errors import (
    DuplicateInstagramConnectionError,
    InstagramConnectionConcurrencyError,
)
from instagram_auth.application.models import InstagramProtectedCredential
from instagram_auth.domain import InstagramConnection, InstagramConnectionId
from instagram_auth.infrastructure.persistence.mappers import (
    InstagramConnectionRecordMapper,
    InstagramCredentialRecordMapper,
)
from instagram_auth.infrastructure.persistence.models import InstagramConnectionRecord


class SqlAlchemyInstagramConnectionRepository(InstagramConnectionRepository):
    """Persist independent Instagram connections through an injected async session."""

    def __init__(
        self,
        session: AsyncSession,
        mapper: InstagramConnectionRecordMapper | None = None,
    ) -> None:
        self._session = session
        self._mapper = mapper or InstagramConnectionRecordMapper()

    async def add(self, connection: InstagramConnection) -> None:
        self._session.add(self._mapper.to_record(connection))
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise DuplicateInstagramConnectionError(
                "Instagram account is already connected for this owner"
            ) from exc

    async def update(self, connection: InstagramConnection) -> None:
        statement = (
            update(InstagramConnectionRecord)
            .where(
                InstagramConnectionRecord.id == str(connection.id.value),
                InstagramConnectionRecord.version == connection.version,
            )
            .values(
                username=connection.username,
                account_type=connection.account_type.value,
                permissions=sorted(permission.value for permission in connection.permissions),
                status=connection.status.value,
                connected_at=connection.connected_at,
                credential_expires_at=connection.credential_expires_at,
                revoked_at=connection.revoked_at,
                last_validated_at=connection.last_validated_at,
                version=connection.version + 1,
            )
        )
        result = cast(CursorResult[object], await self._session.execute(statement))
        if result.rowcount != 1:
            raise InstagramConnectionConcurrencyError("Instagram connection update is stale")
        await self._session.flush()

    async def find_by_owner_and_account(
        self,
        *,
        owner_user_id: str,
        instagram_account_id: str,
    ) -> InstagramConnection | None:
        statement = select(InstagramConnectionRecord).where(
            InstagramConnectionRecord.owner_user_id == owner_user_id,
            InstagramConnectionRecord.instagram_account_id == instagram_account_id,
        )
        record = await self._session.scalar(statement)
        return None if record is None else self._mapper.to_domain(record)

    async def get_by_id(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramConnection | None:
        record = await self._session.get(InstagramConnectionRecord, str(connection_id.value))
        return None if record is None else self._mapper.to_domain(record)


class SqlAlchemyInstagramCredentialRepository(InstagramCredentialRepository):
    """Persist only already-protected provider credentials."""

    def __init__(
        self,
        session: AsyncSession,
        mapper: InstagramCredentialRecordMapper | None = None,
    ) -> None:
        self._session = session
        self._mapper = mapper or InstagramCredentialRecordMapper()

    async def save(self, credential: InstagramProtectedCredential) -> None:
        statement = (
            update(InstagramConnectionRecord)
            .where(InstagramConnectionRecord.id == str(credential.connection_id.value))
            .values(
                protected_access_token=credential.protected_access_token,
                credential_expires_at=credential.expires_at,
                revoked_at=credential.revoked_at,
                last_validated_at=credential.last_validated_at,
            )
        )
        result = cast(CursorResult[object], await self._session.execute(statement))
        if result.rowcount != 1:
            raise LookupError("Instagram connection not found")
        await self._session.flush()

    async def get(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramProtectedCredential | None:
        record = await self._session.get(InstagramConnectionRecord, str(connection_id.value))
        if record is None:
            return None
        return self._mapper.to_application(record)
