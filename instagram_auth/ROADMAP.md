# hamresan-instagram-auth Roadmap

## Goal

Allow a consuming application to present an Instagram connection/login experience that:

1. redirects the user to Instagram authorization;
2. authenticates an eligible Instagram Professional account;
3. requests the permissions required by the consuming application;
4. validates the callback and exchanges the authorization code;
5. resolves the Instagram account identity;
6. verifies the granted permissions;
7. persists a secure reusable connection authorization;
8. lets the host map that external identity to a local user and issue its own application session;
9. allows an existing local user to connect additional Instagram Professional accounts without creating additional local users;
10. supplies clean connection-aware authorization boundaries for `hamresan-instagram-api`.

The package must not read or reply to Instagram content itself.

A local user may own multiple independent Instagram connections:

```text
User
 ├── InstagramConnection #1
 ├── InstagramConnection #2
 └── InstagramConnection #3
```

The package must not encode a one-user/one-Instagram-account assumption.

## Stage 0 — Contract and provider capability baseline

- Confirm the current Meta Instagram API with Instagram Login requirements.
- Target Business and Creator accounts.
- Define required core permissions:
  - `instagram_business_basic`
  - `instagram_business_manage_messages`
  - `instagram_business_manage_comments`
- Define optional permission registry for insights/content publishing without requesting them by default.
- Define normalized provider errors and connection states.
- Define connection identity/uniqueness semantics for multiple Instagram accounts owned by one host user.
- Document Standard Access vs Advanced Access/App Review expectations for host applications.
- Add tests for permission-set semantics and account-type eligibility rules.

Exit criteria:

- public contract names and responsibilities are fixed;
- package makes no unsupported claims about consumer/personal accounts;
- permissions are explicit and least-privilege;
- contracts do not assume one Instagram account per local user.

## Stage 1 — Domain and application contracts

Introduce focused domain/application abstractions such as:

```text
InstagramExternalIdentity
InstagramAuthorizationGrant
InstagramConnection
InstagramConnectionId
InstagramConnectionStatus
InstagramPermission
InstagramAuthorizationProvider
InstagramAccessTokenProtector
InstagramConnectionRepository
InstagramConnectionReader
InstagramConnectionLister
Clock
StateGenerator
```

Rules:

- provider IDs are treated as opaque strings;
- domain entities contain no raw provider secrets;
- Meta-specific DTOs do not leak into application services;
- contracts are explicitly implemented by infrastructure adapters;
- every downstream operation can identify a specific Instagram connection explicitly;
- no package contract assumes a globally active connection.

Exit criteria:

- domain/application layers pass unit tests without FastAPI, SQLAlchemy, or Meta HTTP dependencies;
- tests cover multiple connections for the same host owner.

## Stage 2 — Authorization URL and OAuth state security

- Build provider authorization requests.
- Generate cryptographically strong OAuth state.
- Persist/validate short-lived authorization state through an injected abstraction.
- Reject missing, expired, reused, or mismatched state.
- Add callback correlation metadata without leaking secrets.
- Support host-provided redirect URI configuration.
- Preserve enough host correlation context to distinguish first-time login from adding another Instagram connection to an already-authenticated user.

Exit criteria:

- state validation is fail-closed and covered by replay/expiry tests;
- callback correlation cannot accidentally attach a connection to the wrong local user.

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
- Persist permission snapshots/status per connection.
- Detect partial authorization.
- Return an explicit actionable result when required scopes are missing.
- Support reconnect/re-authorization when permissions change.

Exit criteria:

- a connection cannot become usable when required permissions are absent;
- permission changes on one connection do not affect another connection owned by the same local user.

## Stage 5 — Secure multi-connection credential persistence

- Add async SQLAlchemy persistence behind repository/UoW contracts.
- Persist each Instagram authorization as an independent connection record.
- Persist only protected access credentials.
- Require host-provided token protection/encryption abstraction.
- Track expiration/revocation/last-validation metadata per connection where available.
- Support one host owner having multiple Instagram connections.
- Enforce appropriate uniqueness so the same Instagram account is not accidentally connected twice for the same owner.
- Avoid foreign key dependency on `hamresan-identity`; host ownership IDs remain external identifiers.
- Expose package Alembic metadata/filter helpers; host owns revision history.
- Add concurrency tests around connection creation/update and duplicate prevention.

Suggested package-owned tables may use an `instagram_auth_` prefix.

Conceptual persistence shape:

```text
InstagramConnection
- id
- owner_user_id
- instagram_account_id
- username
- account_type
- protected_access_token
- permissions
- status
- expires_at
- connected_at
```

Exit criteria:

- no raw access token is stored at rest by default;
- persistence has no foreign key dependency on `hamresan-identity`;
- one user can own multiple independent connections;
- duplicate connection creation is handled deterministically.

## Stage 6 — Host identity bootstrap and additional-account linking

Provide a clean output that a host can map to `hamresan-identity` or another identity system.

First-time login flow:

```text
OAuth callback
   ↓
InstagramExternalIdentity
   ↓
host user linker
   ↓
find/create local user
   ↓
create InstagramConnection
   ↓
host identity session
```

Additional-account flow:

```text
Authenticated local user
   ↓
Connect another Instagram account
   ↓
OAuth callback
   ↓
InstagramExternalIdentity
   ↓
create/update another InstagramConnection
   ↓
return to account management
```

- Add an example consumer integrating with `hamresan-identity`.
- Keep mapping/orchestration in the host composition root.
- Do not introduce a hard dependency from either package to the other.
- Make the host explicitly decide whether an OAuth result bootstraps a new local user or attaches a connection to an existing authenticated user.

Exit criteria:

- a first-time Instagram user can bootstrap a local application account;
- a returning Instagram identity maps to the same local user according to host policy;
- an authenticated local user can connect a second Instagram account without creating another local user.

## Stage 7 — Connection management use cases

Add focused application use cases for host account management:

```text
ListInstagramConnections
GetInstagramConnection
DisconnectInstagramConnection
ReconnectInstagramConnection
```

Requirements:

- every use case operates on an explicit connection ID;
- host ownership authorization is supplied/validated at the application boundary;
- one user's connection cannot be read or modified by another user;
- disconnecting one connection does not affect the user's other connections;
- reconnect authorization is correlated to the intended connection across OAuth state;
- a callback resolving a different Instagram account is rejected rather than creating or updating
  another connection;
- reconnect updates the intended connection rather than creating accidental duplicates.

Exit criteria:

- a host can render an Instagram account-management screen with multiple connections;
- individual connections can be disconnected or reauthorized independently.

## Stage 8 — Access boundary for hamresan-instagram-api

Expose or adapt narrow read contracts required by the API package, for example:

```text
InstagramConnectionReader
InstagramConnectionLister
InstagramAccessTokenProvider
```

Requirements:

- downstream token/access lookup is keyed by an explicit connection identifier;
- `hamresan-instagram-api` does not access auth tables directly;
- no repository/model sharing between packages;
- host composition adapts auth-owned storage to API-owned contracts;
- revoked/disconnected/insufficient-permission connections fail closed.

Exit criteria:

- API package can obtain authorized provider access for a selected connection without persistence coupling;
- two connections owned by the same local user remain fully isolated at the authorization boundary.

## Stage 9 — FastAPI adapter

Provide optional thin routes/adapters for host installation, conceptually:

```text
GET    /instagram/auth/start
GET    /instagram/auth/callback
GET    /instagram/connections
GET    /instagram/connections/{connection_id}
POST   /instagram/connections/{connection_id}/disconnect
POST   /instagram/connections/{connection_id}/reauthorization
POST   /instagram/connections/{connection_id}/reconnect
```

The host owns route prefixing, frontend redirect behavior, session issuance, ownership authorization, observability, and deployment topology.

Exit criteria:

- routes contain no persistence/provider business logic;
- application use cases remain transport-independent;
- multiple connections can be managed without an implicit active/global connection.

## Stage 10 — Reauthorization, expiration, and connection health

- Detect expired/revoked credentials per connection.
- Define reauthorization-required status.
- Re-check critical permissions before sensitive downstream operations when necessary.
- Support user-requested disconnect for a selected connection.
- Define security events for repeated OAuth failures or unexpected permission loss.
- Add host-invoked health/maintenance use cases where provider behavior requires them.
- Ensure one unhealthy connection does not mark unrelated connections unhealthy.

Exit criteria:

- downstream packages receive an explicit unusable-connection result rather than mysterious provider failures;
- connection health is isolated per Instagram account.

## Stage 11 — App Review and production hardening

- Document Meta App Review/Advanced Access requirements for serving third-party professional accounts.
- Add secure production configuration checklist.
- Add timeout, retry, masking, structured provider-error, and observability tests.
- Add authorization/ownership tests for connection-management use cases.
- Add wheel/package smoke tests.
- Run Ruff, formatting, strict Pyright, unit/integration tests, and branch coverage gate.
- Add consumer integration test with `hamresan-identity` and `hamresan-instagram-api` contracts.

## Final acceptance scenario

A first-time user opens a consuming application and selects **Continue with Instagram**. The application redirects to Instagram, requests only the required permissions, validates the callback, resolves the professional Instagram account, securely stores an independent `InstagramConnection`, maps the Instagram external identity to a local user, and issues the host application's own session.

The same authenticated user can later select **Connect another Instagram account**, authorize another eligible professional account, and receive another independent connection under the same local user. The host can list the user's connections, select a specific connection for downstream API operations, disconnect or reconnect one account without affecting the others, and expose the selected connection authorization to `hamresan-instagram-api` through explicit contracts.

At this point the authentication package is complete; reading messages/media/comments and sending replies remains the responsibility of `hamresan-instagram-api`.
