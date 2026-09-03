# hamresan-instagram-auth Roadmap

## Goal

Allow a consuming application to present a single Instagram connection/login experience that:

1. redirects the user to Instagram authorization;
2. authenticates an eligible Instagram Professional account;
3. requests the permissions required by the consuming application;
4. validates the callback and exchanges the authorization code;
5. resolves the Instagram account identity;
6. verifies the granted permissions;
7. persists a secure reusable connection authorization;
8. lets the host map that external identity to a local user and issue its own application session;
9. supplies a clean authorization boundary for `hamresan-instagram-api`.

The package must not read or reply to Instagram content itself.

## Stage 0 — Contract and provider capability baseline

- Confirm the current Meta Instagram API with Instagram Login requirements.
- Target Business and Creator accounts.
- Define required core permissions:
  - `instagram_business_basic`
  - `instagram_business_manage_messages`
  - `instagram_business_manage_comments`
- Define optional permission registry for insights/content publishing without requesting them by default.
- Define normalized provider errors and connection states.
- Document Standard Access vs Advanced Access/App Review expectations for host applications.
- Add tests for permission-set semantics and account-type eligibility rules.

Exit criteria:

- public contract names and responsibilities are fixed;
- package makes no unsupported claims about consumer/personal accounts;
- permissions are explicit and least-privilege.

## Stage 1 — Domain and application contracts

Introduce focused domain/application abstractions such as:

```text
InstagramExternalIdentity
InstagramAuthorizationGrant
InstagramConnection
InstagramConnectionStatus
InstagramPermission
InstagramAuthorizationProvider
InstagramAccessTokenProtector
InstagramConnectionRepository
Clock
StateGenerator
```

Rules:

- provider IDs are treated as opaque strings;
- domain entities contain no raw provider secrets;
- Meta-specific DTOs do not leak into application services;
- contracts are explicitly implemented by infrastructure adapters.

Exit criteria:

- domain/application layers pass unit tests without FastAPI, SQLAlchemy, or Meta HTTP dependencies.

## Stage 2 — Authorization URL and OAuth state security

- Build provider authorization requests.
- Generate cryptographically strong OAuth state.
- Persist/validate short-lived authorization state through an injected abstraction.
- Reject missing, expired, reused, or mismatched state.
- Add callback correlation metadata without leaking secrets.
- Support host-provided redirect URI configuration.

Exit criteria:

- state validation is fail-closed and covered by replay/expiry tests.

## Stage 3 — Meta authorization-code exchange

- Implement a Meta OAuth client behind `InstagramAuthorizationProvider`.
- Exchange authorization code for supported access token(s).
- Normalize provider errors/timeouts.
- Resolve the authenticated Instagram Professional account.
- Map provider responses through dedicated mappers.
- Add retry only where semantically safe.

Exit criteria:

- successful and failed callback flows have deterministic application results;
- raw tokens never appear in logs or domain entities.

## Stage 4 — Permission resolution and enforcement

- Retrieve/resolve granted permissions from the provider-supported flow.
- Compare granted permissions with host-requested required permissions.
- Persist permission snapshots/status.
- Detect partial authorization.
- Return an explicit actionable result when required scopes are missing.
- Support reconnect/re-authorization when permissions change.

Exit criteria:

- a connection cannot become usable when required permissions are absent.

## Stage 5 — Secure connection credential persistence

- Add async SQLAlchemy persistence behind repository/UoW contracts.
- Persist only protected access credentials.
- Require host-provided token protection/encryption abstraction.
- Track expiration/revocation/last-validation metadata where available.
- Expose package Alembic metadata/filter helpers; host owns revision history.
- Add concurrency tests around connection creation/update.

Suggested package-owned tables may use an `instagram_auth_` prefix.

Exit criteria:

- no raw access token is stored at rest by default;
- persistence has no foreign key dependency on `hamresan-identity`.

## Stage 6 — Host identity bootstrap integration

Provide a clean output that a host can map to `hamresan-identity` or another identity system.

Desired host flow:

```text
OAuth callback
   ↓
InstagramExternalIdentity
   ↓
host user linker
   ↓
find/create local user
   ↓
host identity session
```

- Add an example consumer integrating with `hamresan-identity`.
- Keep mapping/orchestration in the host composition root.
- Do not introduce a hard dependency from either package to the other.

Exit criteria:

- a first-time Instagram user can bootstrap a local application account;
- a returning Instagram identity maps to the same local user according to host policy.

## Stage 7 — Access boundary for hamresan-instagram-api

Expose or adapt narrow read contracts required by the API package, for example:

```text
InstagramConnectionReader
InstagramAccessTokenProvider
```

Requirements:

- `hamresan-instagram-api` does not access auth tables directly;
- no repository/model sharing between packages;
- host composition adapts auth-owned storage to API-owned contracts;
- revoked/disconnected/insufficient-permission connections fail closed.

Exit criteria:

- API package can obtain authorized provider access without persistence coupling.

## Stage 8 — FastAPI adapter

Provide optional thin routes/adapters for host installation, conceptually:

```text
GET /instagram/auth/start
GET /instagram/auth/callback
POST /instagram/auth/disconnect
GET /instagram/auth/connection
```

The host owns route prefixing, frontend redirect behavior, session issuance, observability, and deployment topology.

Exit criteria:

- routes contain no persistence/provider business logic;
- application use cases remain transport-independent.

## Stage 9 — Reauthorization, expiration, and connection health

- Detect expired/revoked credentials.
- Define reauthorization-required status.
- Re-check critical permissions before sensitive downstream operations when necessary.
- Support user-requested disconnect.
- Define security events for repeated OAuth failures or unexpected permission loss.
- Add host-invoked health/maintenance use cases where provider behavior requires them.

Exit criteria:

- downstream packages receive an explicit unusable-connection result rather than mysterious provider failures.

## Stage 10 — App Review and production hardening

- Document Meta App Review/Advanced Access requirements for serving third-party professional accounts.
- Add secure production configuration checklist.
- Add timeout, retry, masking, structured provider-error, and observability tests.
- Add wheel/package smoke tests.
- Run Ruff, formatting, strict Pyright, unit/integration tests, and branch coverage gate.
- Add consumer integration test with `hamresan-identity` and `hamresan-instagram-api` contracts.

## Final acceptance scenario

A user opens a consuming application and selects **Continue with Instagram**. The application redirects to Instagram, requests only the required permissions, validates the callback, resolves the professional Instagram account, securely stores the authorization, maps the Instagram external identity to a local user, issues the host application's own session, and exposes the connected account authorization to `hamresan-instagram-api` through explicit contracts.

At this point the authentication package is complete; reading messages/media/comments and sending replies remains the responsibility of `hamresan-instagram-api`.
