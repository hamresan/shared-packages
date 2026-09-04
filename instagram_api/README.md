# hamresan-instagram-api

Reusable Instagram API integration package for Python/FastAPI applications.

```text
Distribution: hamresan-instagram-api
Import:       instagram_api
Python:       >= 3.12
```

## Purpose

`hamresan-instagram-api` provides the application-facing capabilities required to work with an already-authorized Instagram Professional account.

It consumes an authorized Instagram connection/access-token boundary supplied by the host application and exposes clean contracts/use cases for:

- Instagram account/profile reading;
- media/post/reel reading;
- conversation and message reading;
- sending supported Instagram messages/replies;
- comment reading;
- public comment replies;
- supported private replies to commenters;
- webhook verification and inbound event normalization;
- connection/API health and provider error normalization.

The package does **not** authenticate local application users, own local user sessions, or decide what an LLM should say. Authentication/authorization belongs to `hamresan-instagram-auth` and the host identity layer. AI/automation orchestration belongs to the consuming application or a separate automation/AI package.

The package must be **connection-aware**. A local user may have multiple authorized Instagram accounts, so every account-scoped operation must target a specific Instagram connection rather than assuming one Instagram account per user.

## Target end-to-end product flow

```text
User connects one or more Instagram accounts
        ↓
hamresan-instagram-auth
        ↓
authorized Instagram connections
        ↓
host selects a connection
        ↓
hamresan-instagram-api
        ├── read account/media
        ├── read conversations/messages
        ├── receive message webhooks
        ├── send replies
        ├── read comments
        ├── receive comment webhooks
        └── reply to comments
```

For an AI-enabled application:

```text
Instagram webhook
      ↓
hamresan-instagram-api
      ↓
normalized inbound event + connection identity
      ↓
host automation / LLM
      ↓
reply command for the same connection
      ↓
hamresan-instagram-api
      ↓
Instagram
```

The package must never call an LLM directly.

## Supported account type

The initial package targets Instagram Professional accounts supported by the current Instagram API:

- Business accounts
- Creator accounts

Consumer/personal accounts are outside the initial contract.

## Authorization boundary

The package should not own Instagram OAuth persistence and should not access `hamresan-instagram-auth` tables directly.

It should depend on narrow contracts such as:

```text
InstagramAccessTokenProvider
InstagramConnectionReader
```

Token/access lookup must be keyed by an explicit connection identifier. The host composition root adapts its authorization/connection storage to these contracts.

The package must not infer a globally active Instagram account from the current user. Selecting the connection for inbox, comments, media, or any other account-scoped operation belongs to the host application.

## Initial capabilities

### Account/profile

- resolve/read the selected connected professional account;
- read supported profile/account fields;
- validate that the selected connection is usable.

### Media

- list owned media/posts for a selected connection;
- read supported media details;
- handle pagination;
- support posts/reels and other media types exposed by the current API;
- preserve Meta IDs as opaque strings.

### Messaging

- list supported conversations for a selected connection;
- list messages in a conversation;
- read supported message metadata/details;
- send supported messages/replies using the same selected connection;
- receive and normalize messaging webhook events with enough connection/account identity for host routing;
- support pagination and provider constraints.

Important platform rules:

- outbound Stage 6 messaging is reply-oriented: the recipient must have an existing conversation
  discoverable for the selected connection before the package sends;
- the initial send capability supports text plus documented image/video URL attachments;
- host `correlation_id` values are returned for host correlation but are never sent to Meta and do
  not create provider-side idempotency;
- non-idempotent Send API POST requests are never retried automatically;
- provider request/policy rejection is normalized without inventing undocumented Meta error-code
  semantics;
- the package must not promise arbitrary proactive DMs;
- conversations in the Requests folder that have been inactive for 30 days are not returned by Meta;
- message IDs may be listed beyond the range for which Meta exposes full details;
- Meta currently exposes message details only for the 20 most recent messages in a conversation;
- unsupported or detail-ineligible messages remain normalized as partial messages instead of being
  filled with invented sender/text data;
- shared-media/message data may be incomplete and must not be presented as complete media metadata.

Instagram messaging conversations are subject to Meta's current messaging policies and
recipient/conversation eligibility rules. The package must not describe conversation reads as a
complete DM archive.

### Comments

- list/read comments on owned supported media for a selected connection;
- receive and normalize comment webhook events with account/connection correlation data;
- publish supported public replies through the correct connection;
- support Meta's private-reply flow where allowed;
- expose explicit failure reasons for expired or ineligible reply windows.

### Webhooks

- provide webhook verification helpers/adapters;
- validate provider signatures where applicable;
- parse Meta payloads through dedicated provider DTOs/mappers;
- normalize inbound events into package-owned event contracts;
- preserve enough provider account identity for the host to resolve the owning `InstagramConnection`;
- expose idempotency/deduplication boundaries;
- avoid invoking host business/AI logic inside the webhook parser.

Conceptual normalized events:

```text
InstagramMessageReceived
InstagramCommentCreated
InstagramCommentUpdated
InstagramConnectionChanged
```

Normalized events should carry the provider account/connection correlation required to route an event to the correct authorized account when one local user owns multiple Instagram connections.

Only events actually supported by the current provider API should be implemented.

## Instagram Live scope

Live support is deliberately capability-gated.

Current Meta documentation includes comment/private-reply behavior involving Instagram Live, but the package must **not** promise generic reading/streaming of the live video or arbitrary live-session data unless a supported public API endpoint and permission are verified during implementation.

The roadmap therefore separates:

- Live comment events/replies that are explicitly supported by Meta;
- active Live media/session discovery, which remains research/conditional;
- live video/audio stream ingestion, which is outside scope unless Meta exposes an appropriate supported API.

Provider capability checks must be based on current Meta documentation rather than assumptions.

## Suggested package structure

```text
instagram_api/
├── src/
│   └── instagram_api/
│       ├── domain/
│       ├── application/
│       │   ├── contracts/
│       │   ├── accounts/
│       │   ├── media/
│       │   ├── messaging/
│       │   ├── comments/
│       │   └── webhooks/
│       ├── infrastructure/
│       │   └── meta/
│       │       ├── accounts/
│       │       ├── media/
│       │       ├── messaging/
│       │       ├── comments/
│       │       └── webhooks/
│       └── presentation/
│           └── fastapi/
├── tests/
├── README.md
├── ROADMAP.md
└── pyproject.toml
```

Tests should mirror the package's internal responsibility/layer structure.

## Architectural rules

- Domain/application code must not depend on FastAPI, SQLAlchemy, or Meta SDK implementations.
- External HTTP communication stays behind explicit provider/client contracts.
- Public use cases are small and capability-oriented.
- Provider DTO ↔ domain/application mapping lives in dedicated mappers.
- Webhook verification, parsing, deduplication, and dispatch boundaries remain separate responsibilities.
- No service locator.
- Dependencies are injected explicitly.
- No direct dependency on host application modules.
- No direct dependency on `hamresan-identity`.
- No direct persistence coupling to `hamresan-instagram-auth`.
- No one-user/one-Instagram-account assumption.
- Account-scoped operations require explicit connection context.
- No LLM calls or AI prompt logic inside this package.

## Security and reliability requirements

- Never log raw access tokens or app secrets.
- Mask sensitive provider payload fields in logs where required.
- Validate webhook authenticity before processing events.
- Make webhook handling idempotent.
- Use bounded provider timeouts.
- Retry only safe/idempotent operations according to operation semantics.
- Preserve provider error codes internally while returning normalized application errors.
- Respect current Meta rate limits, messaging policies, reply windows, and permission requirements.
- Fail closed when the selected connection lacks the required permission or is unusable.
- Never allow an operation intended for one connection to fall back silently to another connection.

## Relationship with other packages

```text
hamresan-identity
    local user/session

hamresan-instagram-auth
    Instagram OAuth + permission + multiple connection authorizations

hamresan-instagram-api
    connection-aware Instagram data/actions + webhooks

host automation/AI
    selects connection and decides whether/how to reply
```

## Provider capability matrix

Roadmap Stage 0 is documented in
[`docs/PROVIDER_CAPABILITY_MATRIX.md`](docs/PROVIDER_CAPABILITY_MATRIX.md).

The matrix records the verified Instagram Login host/permissions, profile/media/messaging/comment
capabilities, webhook routing identifiers, provider limitations, pagination/version expectations,
and capability-gated Instagram Live behavior.

## Status

Implementation progress is tracked stage by stage in `ROADMAP.md`. This package must not be
considered complete beyond the latest merged roadmap stage and its passing quality gates.
