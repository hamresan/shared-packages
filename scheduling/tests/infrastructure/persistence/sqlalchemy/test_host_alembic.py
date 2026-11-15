"""Actual Alembic revision/upgrade/downgrade against a disposable host database."""

import os
from pathlib import Path

import pytest

from tests.support.migrations.host_migration_acceptance import assert_host_revision_lifecycle


@pytest.mark.asyncio
async def test_host_generates_and_applies_revision_with_sqlite(tmp_path: Path) -> None:
    await assert_host_revision_lifecycle(f"sqlite+aiosqlite:///{tmp_path / 'host.db'}", tmp_path)


@pytest.mark.asyncio
async def test_host_generates_and_applies_revision_with_postgresql(tmp_path: Path) -> None:
    url = os.getenv("SCHEDULING_TEST_POSTGRES_URL")
    if url is None:
        pytest.skip("Real PostgreSQL required for host Alembic migration acceptance.")
    await assert_host_revision_lifecycle(url, tmp_path)
