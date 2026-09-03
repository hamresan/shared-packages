import asyncio
from asyncio import run
from pathlib import Path

from instagram_auth.application.errors import DuplicateInstagramConnectionError
from instagram_auth.infrastructure.persistence import SqlAlchemyInstagramConnectionRepository
from tests.infrastructure.persistence.builders import build_connection
from tests.infrastructure.persistence.database import build_database


def test_concurrent_duplicate_creation_allows_only_one_connection(tmp_path: Path) -> None:
    async def execute() -> None:
        engine, factory = await build_database(tmp_path / "concurrent-duplicate.sqlite")

        async def create(connection_id: str) -> str:
            async with factory() as session:
                repository = SqlAlchemyInstagramConnectionRepository(session)
                try:
                    await repository.add(
                        build_connection(
                            connection_id=connection_id,
                            instagram_account_id="ig-race",
                        )
                    )
                    await session.commit()
                except DuplicateInstagramConnectionError:
                    await session.rollback()
                    return "duplicate"
                return "created"

        results = await asyncio.gather(
            create("00000000-0000-0000-0000-000000000010"),
            create("00000000-0000-0000-0000-000000000011"),
        )
        assert sorted(results) == ["created", "duplicate"]
        await engine.dispose()

    run(execute())
