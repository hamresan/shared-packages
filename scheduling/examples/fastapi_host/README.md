# Standalone FastAPI consumer example

This host owns authentication, the database URL, SQLAlchemy session factory, authorization,
and startup/shutdown lifecycle. The scheduling package never accepts tenant identity from a
request body. The example uses a minimal API-key identity purely to demonstrate the trust
boundary; replace it with a production authentication and ownership implementation.

From `scheduling/`:

```bash
uv sync --frozen --group dev
export SCHEDULING_DEMO_API_KEY='replace-with-a-local-test-secret'
uv run --with uvicorn --frozen uvicorn examples.fastapi_host.app:create_app --factory
```

`uvicorn` is a host server dependency; install it in the consuming application. The
`--with uvicorn` example starts it without adding it to the scheduling core. The default SQLite database is `demo_scheduling.db` in
the current directory; set `SCHEDULING_DEMO_DB_URL` for a different host-controlled URL.

The demo authorizes `org-1`, `location-1`, `location-2`, `resource-1`, and `resource-2` for
one hard-coded demonstration principal. Request authentication requires `X-API-Key`.
Use `POST /scheduling/calendars` to create one calendar per scope, then
`POST /scheduling/availability` for advisory per-resource slots. External busy intervals
are supplied by the host's `BusyIntervalReader` implementation; the demo reader is empty
because the sample contains no reservation system.

The example calls `metadata.create_all()` for local demonstration only. Production hosts
must review and apply their own Alembic revisions rather than relying on create-all.
