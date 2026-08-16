# hamresan-notification

Reusable notification package based on the notification boundaries proven in Sellora while keeping Sellora read-only.

## Responsibilities

- Stable public `NotificationSender` contract.
- Queue-first notification orchestration through a host-provided queue abstraction.
- Delivery service that renders a template, resolves a provider, and sends the message.
- Replaceable providers for console, SMTP email, and HTTP SMS.
- Filesystem/Jinja template infrastructure.
- Optional FastAPI test endpoint adapter.
- Mirrored tests matching the package layers.

## Host-owned infrastructure

The package does not create Redis, ARQ, Celery, or another worker system. A consuming application injects a `NotificationQueue`. This keeps job infrastructure, retries, connection lifecycle, and deployment choices outside the package.

Identity and other consumers should depend only on `NotificationSender` and the public command/DTO types.

## Development

Create and activate a virtual environment, then install the package with development/test dependencies:

```bash
make install-dev
```

Run all checks with:

```bash
make check
```

The package uses a `src/` layout. Pytest and Pyright are configured to resolve imports from `src`, while `make install-dev` installs FastAPI, pytest-asyncio, Ruff, Pyright, and the other test dependencies required by the full test suite.
