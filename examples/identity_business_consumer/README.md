# Identity + Notification + Business host example

This consumer composes the public `Identity`, `Notification`, and `Business` APIs.
Identity handles OTP registration, JWT access-token issuance, active-user and session
validation; Notification queues the OTP; Business receives only a trusted
`AuthenticatedActor` derived from Identity's authenticated principal.

The sample uses a **capturing in-memory notification queue** and a disposable SQLite
database for deterministic integration testing. The queue is not a production OTP
transport; replace it with the host's real Notification queue and delivery worker.
`build_consumer_application` requires an externally supplied JWT signing secret.

From this directory:

```bash
uv sync --extra test
uv run pytest
```

The test covers OTP request, Notification enqueue, OTP verification, real signed
JWT authentication, creation and reading of a Business, and rejection of
missing/forged access tokens.

A second integration test composes Identity and Business metadata into a single
host-owned schema, applies initial table/index DDL through Alembic operations,
and verifies that Alembic autogeneration reports no schema drift. Production
hosts should maintain explicit, versioned Alembic revisions; the test harness
does not publish or substitute for their migration history.
