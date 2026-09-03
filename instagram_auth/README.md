# hamresan-instagram-auth

Reusable Instagram OAuth and authorization package for Python/FastAPI applications.

```text
Distribution: hamresan-instagram-auth
Import:       instagram_auth
Python:       >= 3.12
```

## Purpose

`hamresan-instagram-auth` owns the boundary required to let an application user authenticate with an eligible Instagram Professional account and authorize the application to access that Instagram account.

The package is intentionally limited to authentication, authorization, permissions, token lifecycle, and Instagram account identity resolution. It does **not** read conversations, messages, comments, media, or send replies. Those capabilities belong to `hamresan-instagram-api`.

The package does not own the application's local user sessions. A host application may use the resolved Instagram identity to create or find a local user through `hamresan-identity`, then issue its own session/access token.

A local application user may authorize **multiple Instagram Professional accounts**. Each authorization is represented as an independent `InstagramConnection` with its own provider account identity, permission snapshot, credential lifecycle, status, and connection metadata. The host must not store a single Instagram account identifier directly on the local user model.

## Target user flow

The desired application experience is:

```text
Continue with Instagram
        ↓
Instagram authorization
        ↓
User grants required permissions
        ↓
OAuth callback
        ↓
Resolve Instagram Professional account identity
        ↓
Find/create local application user
        ↓
Create or update Instagram connection
        ↓
Issue host application session
        ↓
Application dashboard
```

Authentication and the first Instagram account connection may happen during the same OAuth flow, while remaining separate concerns internally.

After the local user exists, the same authorization flow can be used to connect additional Instagram accounts without creating another local user:

```text
Existing local User
        ↓
Connect another Instagram account
        ↓
Instagram authorization
        ↓
Resolve Instagram Professional account
        ↓
Create/update another InstagramConnection
```

Conceptually:

```text
User
 ├── InstagramConnection #1
 ├── InstagramConnection #2
 └── InstagramConnection #3
```

The host application owns the association between its local user and one or more Instagram connections. A connection remains an independent authorization resource rather than being embedded inside the user entity.

## Supported account type

The initial package targets Instagram Professional accounts supported by the current Instagram API with Instagram Login:

- Business accounts
- Creator accounts

Consumer/personal Instagram accounts are outside the initial package contract unless Meta later exposes equivalent supported APIs.

## Initial permissions

The initial application use case requires the package to request and verify the permissions needed by downstream Instagram API capabilities.

Core permissions:

```text
instagram_business_basic
instagram_business_manage_messages
instagram_business_manage_comments
```

Optional permissions should be requested only when the consuming application needs them. For example:

```text
instagram_business_manage_insights
instagram_business_content_publish
```

The package must follow least-privilege authorization: do not request publishing or insights permissions unless a host feature actually requires them.

## Package responsibilities

The package should own:

- building the Instagram authorization URL;
- OAuth state generation and validation;
- PKCE or equivalent provider-supported flow protections when applicable;
- OAuth callback validation;
- authorization-code exchange;
- Instagram account identity resolution;
- granted-permission retrieval and validation;
- access-token lifecycle orchestration supported by Meta;
- connection status and authorization status;
- create/update/list/read/disconnect semantics for independent Instagram connections;
- protection against duplicate connection records for the same host owner and Instagram account;
- disconnect/revoke orchestration where supported;
- provider error normalization;
- secure token handoff/persistence boundaries;
- public contracts for host integration;
- optional FastAPI adapters for login and callback endpoints.

The package should not own:

- local application user/session management;
- host ownership/workspace/store concepts;
- active-account UI selection;
- DM/conversation reading;
- message sending;
- media/post reading;
- comment reading or replying;
- webhook event processing;
- LLM or automation behavior;
- business/store domain concepts.

## Multi-account connection model

`InstagramConnection` is an independent authorization resource. The host may associate many connections with one local user.

Conceptual host-owned association:

```text
User
- id

InstagramConnection
- id
- owner_user_id
- instagram_account_id
- username
- account_type
- status
- permissions
- credential metadata
- connected_at
```

The package should preserve provider account IDs as opaque strings. Persistence should enforce uniqueness appropriate to the host ownership model so that the same Instagram account is not accidentally connected twice for the same owner.

The design must not assume a global "active Instagram account" inside this package. Selecting which connection is active for an inbox, comments view, or API request is a host application concern.

## Integration with hamresan-identity

`hamresan-instagram-auth` and `hamresan-identity` should remain independent packages.

Conceptually:

```text
Instagram OAuth
      ↓
hamresan-instagram-auth
      ↓
InstagramExternalIdentity
      ↓
host composition/orchestration
      ↓
hamresan-identity
      ↓
local User + Session
```

A resolved external identity should expose stable provider identity information without making `hamresan-identity` depend on Meta-specific SDKs or models.

Example conceptual output:

```text
InstagramExternalIdentity
- provider = "instagram"
- provider_user_id
- username
- account_type
```

The host decides how that identity maps to its local user model and whether the OAuth callback bootstraps a new local user or attaches another Instagram connection to an existing user.

## Integration with hamresan-instagram-api

`hamresan-instagram-api` needs authorized access to a selected connected Instagram account but must not depend on this package's persistence implementation.

Use narrow contracts such as:

```text
InstagramAccessTokenProvider
InstagramConnectionReader
InstagramConnectionLister
```

Connection-aware reads should use an explicit connection identifier rather than assuming one connection per user.

The host composition root can adapt `hamresan-instagram-auth` persistence to those contracts.

This keeps the dependency direction clean:

```text
instagram_api application contracts
            ↑
host adapter/composition
            ↓
instagram_auth authorization storage
```

## Security requirements

The package must:

- validate OAuth state before accepting callbacks;
- never log authorization codes or raw access tokens;
- protect persisted access tokens using a host-provided secret/encryption abstraction;
- avoid provider-specific secrets in domain entities;
- fail closed when required permissions are missing;
- make permission changes observable to the host;
- support token expiration/revocation handling per connection;
- prevent one local user from reading or mutating another user's connection through host-provided ownership authorization;
- normalize provider IDs as opaque strings unless Meta guarantees another type;
- keep Meta app secret/configuration in the host's secret-management layer;
- use explicit provider contracts and dependency injection;
- avoid direct dependency on `hamresan-identity`.

## Suggested package structure

```text
instagram_auth/
├── src/
│   └── instagram_auth/
│       ├── domain/
│       ├── application/
│       │   ├── contracts/
│       │   ├── login/
│       │   ├── callback/
│       │   ├── permissions/
│       │   └── connections/
│       ├── infrastructure/
│       │   ├── meta/
│       │   ├── persistence/
│       │   └── security/
│       └── presentation/
│           └── fastapi/
├── tests/
├── README.md
├── ROADMAP.md
└── pyproject.toml
```

Tests should mirror the package's internal responsibility/layer structure.

## Architectural rules

- Domain/application code must not depend on FastAPI or SQLAlchemy.
- Meta-specific HTTP behavior stays behind provider/client contracts.
- OAuth orchestration stays in focused application services.
- DTO/entity/provider transformations stay in dedicated mappers.
- Token protection stays in dedicated security components.
- Persistence stays behind repositories/UoW contracts.
- FastAPI routes remain thin adapters.
- Dependencies are injected explicitly.
- Avoid generic helpers and service-locator patterns.
- Do not couple the package to a specific host application.
- Do not model a one-user/one-Instagram-account restriction in package contracts or persistence.

## Status

Initial package skeleton and roadmap only. See `ROADMAP.md` for implementation stages.
