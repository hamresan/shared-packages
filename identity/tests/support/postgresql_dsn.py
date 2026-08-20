from sqlalchemy.engine import make_url


class PostgresqlTestDsnPolicy:
    def ensure_safe(self, dsn: str) -> None:
        database_name = make_url(dsn).database
        if database_name is None or "test" not in database_name.casefold():
            raise ValueError(
                "IDENTITY_TEST_POSTGRES_DSN must target a disposable database whose name contains 'test'"
            )
