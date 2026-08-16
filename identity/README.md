# hamresan-identity

Reusable identity package extracted from the architectural ideas already proven in Sellora, while keeping Sellora itself read-only.

## Goals

- Passwordless identity with mobile/email identifiers and OTP challenges.
- Session and refresh-token persistence boundaries.
- Public authorization models/contracts that consuming applications can depend on.
- FastAPI presentation adapter.
- SQLAlchemy async persistence adapter.
- Database ownership remains with the host application: the host injects an `AsyncSessionFactory`.
- All identity tables use the `identity_` prefix.
- Tests mirror the package structure.

## Database integration

The package intentionally does not create an SQLAlchemy engine. The host application builds its engine/sessionmaker and adapts it to `AsyncSessionFactory`. This keeps connection configuration, pooling, transactions, and database lifecycle under the host application's control.
