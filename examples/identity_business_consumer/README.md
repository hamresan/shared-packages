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
