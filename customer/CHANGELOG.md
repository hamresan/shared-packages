# Changelog

This project follows SemVer for its documented public API. Dates and releases
are recorded here when versions are tagged; unpublished work is not a release.

## Unreleased

- Complete tenant-scoped customer profiles, contact details, preferences,
  internal notes and optional internal/provider identity links.
- Add PostgreSQL SQLAlchemy persistence, forced RLS policies and host-owned
  Alembic composition helpers.
- Provide idempotent guest creation, optimistic concurrency, mandatory
  transactional audit and policy-gated privacy erasure.
- Add an optional FastAPI adapter with host-authenticated actor dependency.
- Verify concurrency, migration composition, installation and distribution
  contents in CI with real PostgreSQL.

The current `0.1.0a1` build is a development prerelease identifier, not a
published package release.
