import os
from collections.abc import AsyncGenerator

import pytest

from tests.support.postgresql_database import PostgresqlIdentityDatabase
from tests.support.postgresql_dsn import PostgresqlTestDsnPolicy

POSTGRES_DSN_ENV = "IDENTITY_TEST_POSTGRES_DSN"


@pytest.fixture
async def postgres_database() -> AsyncGenerator[PostgresqlIdentityDatabase]:
    dsn = os.getenv(POSTGRES_DSN_ENV)
    if not dsn:
        pytest.skip(f"Set {POSTGRES_DSN_ENV} to run PostgreSQL integration tests")

    PostgresqlTestDsnPolicy().ensure_safe(dsn)
    database = PostgresqlIdentityDatabase(dsn)
    await database.start()
    try:
        yield database
    finally:
        await database.close()
