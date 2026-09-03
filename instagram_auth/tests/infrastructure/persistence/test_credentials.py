from asyncio import run
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import select

from instagram_auth.application.credentials import StoreInstagramConnectionCredential
from instagram_auth.application.models import InstagramAuthorizationGrant
from instagram_auth.infrastructure.persistence import (
    InstagramConnectionRecord,
    SqlAlchemyInstagramConnectionRepository,
    SqlAlchemyInstagramCredentialRepository,
)
from tests.infrastructure.persistence.builders import build_connection
from tests.infrastructure.persistence.database import build_database
from tests.infrastructure.persistence.fakes import PrefixTokenProtector

NOW = datetime(2026, 9, 3, 15, 0, tzinfo=UTC)


def test_raw_access_token_is_never_persisted(tmp_path: Path) -> None:
    async def execute() -> None:
        engine, factory = await build_database(tmp_path / "credential.sqlite")
        connection = build_connection(
            connection_id="00000000-0000-0000-0000-000000000008",
            instagram_account_id="ig-secure",
        )
        async with factory() as session:
            await SqlAlchemyInstagramConnectionRepository(session).add(connection)
            service = StoreInstagramConnectionCredential(
                SqlAlchemyInstagramCredentialRepository(session),
                PrefixTokenProtector(),
            )
            await service.execute(
                connection_id=connection.id,
                grant=InstagramAuthorizationGrant(
                    access_token="raw-secret-token",
                    expires_at=NOW + timedelta(hours=1),
                ),
                last_validated_at=NOW,
            )
            await session.commit()

            record = await session.scalar(
                select(InstagramConnectionRecord).where(
                    InstagramConnectionRecord.id == str(connection.id.value)
                )
            )
            assert record is not None
            assert record.protected_access_token == "protected::nekot-terces-war"
            assert record.protected_access_token != "raw-secret-token"

            credential = await SqlAlchemyInstagramCredentialRepository(session).get(connection.id)
            assert credential is not None
            assert credential.expires_at == NOW + timedelta(hours=1)
            assert credential.last_validated_at == NOW
        await engine.dispose()

    run(execute())
