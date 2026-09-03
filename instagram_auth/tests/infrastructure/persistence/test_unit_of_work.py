from asyncio import run
from pathlib import Path

from instagram_auth.infrastructure.persistence import SqlAlchemyInstagramAuthUnitOfWork
from tests.infrastructure.persistence.builders import build_connection
from tests.infrastructure.persistence.database import build_database


def test_unit_of_work_commits_connection_transaction(tmp_path: Path) -> None:
    async def execute() -> None:
        engine, factory = await build_database(tmp_path / "uow.sqlite")
        connection = build_connection(
            connection_id="00000000-0000-0000-0000-000000000009",
            instagram_account_id="ig-uow",
        )
        async with SqlAlchemyInstagramAuthUnitOfWork(factory) as unit_of_work:
            await unit_of_work.connections.add(connection)
            await unit_of_work.commit()

        async with factory() as session:
            from instagram_auth.infrastructure.persistence import (
                SqlAlchemyInstagramConnectionRepository,
            )

            stored = await SqlAlchemyInstagramConnectionRepository(session).get_by_id(connection.id)
            assert stored == connection
        await engine.dispose()

    run(execute())
