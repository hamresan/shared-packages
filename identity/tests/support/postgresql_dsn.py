from sqlalchemy.engine import make_url


class PostgresqlTestDsnPolicy:
    def ensure_safe(self, dsn: str) -> None:
        url = make_url(dsn)
        if url.drivername != "postgresql+asyncpg":
            raise ValueError(
                "IDENTITY_TEST_POSTGRES_DSN must use the postgresql+asyncpg SQLAlchemy driver"
            )

        database_name = url.database
        if database_name is None or "test" not in database_name.casefold():
            raise ValueError(
                "IDENTITY_TEST_POSTGRES_DSN must target a disposable database whose name contains 'test'"
            )
