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

## Target end-to-end product flow

```text
User connects Instagram
        ↓
hamresan-instagram-auth
        ↓
authorized Instagram connection
        ↓
host application
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
normalized inbound event
      ↓
host automation / LLM
      ↓
reply command
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

The host composition root adapts its authorization/connection storage to these contracts.

## Initial capabilities

### Account/profile

- resolve/read the connected professional account;
- read supported profile/account fields;
- validate that the account connection is usable.

### Media

- list owned media/posts;
- read supported media details;
- handle pagination;
- support posts/reels and other media types exposed by the current API;
- preserve Meta IDs as opaque strings.

### Messaging

- list supported conversations;
- list messages in a conversation;
- read supported message metadata/details;
- send supported messages/replies;
- receive and normalize messaging webhook events;
- support pagination and provider constraints.

Important platform rule: the package must not promise arbitrary proactive DMs. Instagram messaging conversations are subject to Meta's current messaging policies and recipient/conversation eligibility rules.

### Comments

- list/read comments on owned supported media;
- receive and normalize comment webhook events;
- publish supported public replies;
- support Meta's private-reply flow where allowed;
- expose explicit failure reasons for expired or ineligible reply windows.

### Webhooks

- provide webhook verification helpers/adapters;
- validate provider signatures where applicable;
- parse Meta payloads through dedicated provider DTOs/mappers;
- normalize inbound events into package-owned event contracts;
- expose idempotency/deduplication boundaries;
- avoid invoking host business/AI logic inside the webhook parser.

Conceptual normalized events:

```text
InstagramMessageReceived
InstagramCommentCreated
InstagramCommentUpdated
InstagramConnectionChanged
```

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
- Fail closed when the connection lacks the required permission.

## Relationship with other packages

```text
hamresan-identity
    local user/session

hamresan-instagram-auth
    Instagram OAuth + permission + connection authorization

hamresan-instagram-api
    Instagram data/actions + webhooks

host automation/AI
    decides whether/how to reply
```

## Status

Initial package skeleton and roadmap only. See `ROADMAP.md` for staged implementation.
