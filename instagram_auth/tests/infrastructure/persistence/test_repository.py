from asyncio import run
from dataclasses import replace
from pathlib import Path

import pytest

from instagram_auth.application.errors import (
    DuplicateInstagramConnectionError,
    InstagramConnectionConcurrencyError,
)
from instagram_auth.infrastructure.persistence import SqlAlchemyInstagramConnectionRepository
from tests.infrastructure.persistence.builders import build_connection
from tests.infrastructure.persistence.database import build_database


def test_repository_supports_multiple_connections_for_one_owner(tmp_path: Path) -> None:
    async def execute() -> None:
        engine, factory = await build_database(tmp_path / "multiple.sqlite")
        async with factory() as session:
            repository = SqlAlchemyInstagramConnectionRepository(session)
            first = build_connection(
                connection_id="00000000-0000-0000-0000-000000000001",
                instagram_account_id="ig-1",
            )
            second = build_connection(
                connection_id="00000000-0000-0000-0000-000000000002",
                instagram_account_id="ig-2",
            )
            await repository.add(first)
            await repository.add(second)
            await session.commit()

            assert (
                await repository.find_by_owner_and_account(
                    owner_user_id="owner-1", instagram_account_id="ig-1"
                )
                == first
            )
            assert (
                await repository.find_by_owner_and_account(
                    owner_user_id="owner-1", instagram_account_id="ig-2"
                )
                == second
            )
        await engine.dispose()

    run(execute())


def test_same_instagram_account_can_belong_to_different_owners(tmp_path: Path) -> None:
    async def execute() -> None:
        engine, factory = await build_database(tmp_path / "owners.sqlite")
        async with factory() as session:
            repository = SqlAlchemyInstagramConnectionRepository(session)
            await repository.add(
                build_connection(
                    connection_id="00000000-0000-0000-0000-000000000003",
                    owner_user_id="owner-1",
                    instagram_account_id="ig-shared",
                )
            )
            await repository.add(
                build_connection(
                    connection_id="00000000-0000-0000-0000-000000000004",
                    owner_user_id="owner-2",
                    instagram_account_id="ig-shared",
                )
            )
            await session.commit()
        await engine.dispose()

    run(execute())


def test_duplicate_owner_account_is_rejected_deterministically(tmp_path: Path) -> None:
    async def execute() -> None:
        engine, factory = await build_database(tmp_path / "duplicate.sqlite")
        async with factory() as first_session:
            first_repository = SqlAlchemyInstagramConnectionRepository(first_session)
            await first_repository.add(
                build_connection(
                    connection_id="00000000-0000-0000-0000-000000000005",
                    instagram_account_id="ig-duplicate",
                )
            )
            await first_session.commit()

        async with factory() as second_session:
            second_repository = SqlAlchemyInstagramConnectionRepository(second_session)
            with pytest.raises(DuplicateInstagramConnectionError):
                await second_repository.add(
                    build_connection(
                        connection_id="00000000-0000-0000-0000-000000000006",
                        instagram_account_id="ig-duplicate",
                    )
                )
            await second_session.rollback()
        await engine.dispose()

    run(execute())


def test_stale_connection_update_is_rejected(tmp_path: Path) -> None:
    async def execute() -> None:
        engine, factory = await build_database(tmp_path / "concurrency.sqlite")
        original = build_connection(
            connection_id="00000000-0000-0000-0000-000000000007",
            instagram_account_id="ig-concurrency",
        )
        async with factory() as session:
            repository = SqlAlchemyInstagramConnectionRepository(session)
            await repository.add(original)
            await session.commit()

        async with factory() as first_session, factory() as second_session:
            first_repo = SqlAlchemyInstagramConnectionRepository(first_session)
            second_repo = SqlAlchemyInstagramConnectionRepository(second_session)
            first_snapshot = await first_repo.get_by_id(original.id)
            second_snapshot = await second_repo.get_by_id(original.id)
            assert first_snapshot is not None and second_snapshot is not None

            await first_repo.update(replace(first_snapshot, username="first"))
            await first_session.commit()
            with pytest.raises(InstagramConnectionConcurrencyError):
                await second_repo.update(replace(second_snapshot, username="second"))
            await second_session.rollback()
        await engine.dispose()

    run(execute())
