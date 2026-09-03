"""SQLAlchemy connection reader/lister tests."""

from asyncio import run
from pathlib import Path

from instagram_auth.infrastructure.persistence import (
    SqlAlchemyInstagramConnectionLister,
    SqlAlchemyInstagramConnectionReader,
    SqlAlchemyInstagramConnectionRepository,
)
from tests.infrastructure.persistence.builders import build_connection
from tests.infrastructure.persistence.database import build_database


def test_sqlalchemy_reader_and_lister_are_connection_and_owner_scoped(tmp_path: Path) -> None:
    async def scenario() -> None:
        engine, session_factory = await build_database(tmp_path / "reader.db")
        try:
            async with session_factory() as session:
                repository = SqlAlchemyInstagramConnectionRepository(session)
                first = build_connection(
                    connection_id="00000000-0000-0000-0000-000000000101",
                    owner_user_id="owner-1",
                    instagram_account_id="ig-101",
                )
                second = build_connection(
                    connection_id="00000000-0000-0000-0000-000000000102",
                    owner_user_id="owner-2",
                    instagram_account_id="ig-102",
                )
                await repository.add(first)
                await repository.add(second)
                await session.commit()

                reader = SqlAlchemyInstagramConnectionReader(session)
                lister = SqlAlchemyInstagramConnectionLister(session)

                assert await reader.get(first.id) == first
                assert await lister.list_for_owner("owner-1") == (first,)
        finally:
            await engine.dispose()

    run(scenario())
