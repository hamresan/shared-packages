# Identity + Notification consumer integration

This example shows how a consuming FastAPI application composes `hamresan-identity` and `hamresan-notification` without letting either package own the host application's infrastructure lifecycle.

## What the consumer owns

The consumer owns:

- the SQLAlchemy async engine and sessionmaker;
- the `AsyncSessionFactory` passed to Identity;
- the Notification queue implementation;
- the access-token issuer/authenticator implementation;
- FastAPI application creation and router installation.

Identity receives `NotificationModule.sender` through the public `NotificationSender` contract. It does not know which notification queue, SMS provider, SMTP provider, or worker is used.

## Composition flow

```text
Consumer application
  |
  +-- ConsumerDatabase
  |     +-- AsyncSessionFactory
  |
  +-- NotificationModule
  |     +-- InMemoryNotificationQueue
  |     +-- sender
  |
  +-- InMemoryAccessTokenAdapter
  |     +-- AccessTokenIssuer
  |     +-- AccessTokenAuthenticator
  |
  +-- IdentityModule
        +-- session_factory = ConsumerDatabase.session_factory
        +-- notification_sender = NotificationModule.sender
        +-- access_token_issuer = InMemoryAccessTokenAdapter
        +-- access_token_authenticator = InMemoryAccessTokenAdapter
```

## Smoke test

The integration test performs a real registration flow:

1. Identity creates an OTP challenge in SQLite.
2. Identity sends the OTP through `NotificationModule.sender`.
3. The consumer queue receives the notification job payload.
4. The test reads the OTP from that queued payload.
5. Identity verifies the OTP and creates the user, identity, and session records.
6. The consumer access-token adapter issues an access token.
7. The FastAPI `/identity/me` endpoint authenticates that token and returns the created user/session IDs.

This tests the package boundaries together while keeping provider-specific notification delivery outside the smoke test.

## Run locally

From this directory:

```bash
make install-dev
make check
```

`make typecheck` resolves the local `src/consumer_app` package directly through the Pyright execution environment, so the source layout is type-checkable even before installing the example itself.

## Run in Docker

The Docker image is test-only. It installs Notification, Identity, and this consumer example from the monorepo and runs Ruff, format checking, Pyright, and Pytest inside the container.

From this directory:

```bash
make docker-test
```

The Dockerfile deliberately does not expose or map any port. The integration test uses FastAPI through an in-process ASGI transport, so no network port is required and it cannot conflict with services already running on the host.

The example is intentionally small and should be treated as a reference composition pattern, not production token or queue infrastructure.
