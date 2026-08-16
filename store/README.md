# hamresan-store

Reusable Store domain package for FastAPI applications.

This package is being extracted from the useful, stable parts of Sellora's Store module while keeping Sellora read-only. The package is designed for reuse across applications and does not depend on Sellora-specific module paths or Identity presentation code.

## Current scope

The current foundation contains:

- Store aggregate.
- Store setup, availability and moderation statuses.
- Store contact/address/currency/schedule value objects.
- Dedicated validators for store name, languages, country code, currency code and IANA timezone.
- Ruff, Pyright strict mode, Pytest and branch coverage with an 85% minimum gate.

Persistence, application services, FastAPI integration and migrations are implemented in later roadmap stages.

## Development

```bash
make install-dev
make check
```

`make check` runs lint, format check, strict type checking and tests with branch coverage.

## Architecture rules

- Domain code has no FastAPI, SQLAlchemy, Identity or Sellora dependencies.
- Host applications provide authentication/authorization context through contracts.
- SQLAlchemy session lifecycle will be host-owned through an injected async session factory.
- Package-owned database tables will use the `store_` prefix.
- Alembic revision history remains owned by the consuming application.

See `ROADMAP.md` for extraction decisions and the continuation checkpoint.
