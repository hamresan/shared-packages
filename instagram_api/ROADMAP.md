# hamresan-instagram-api Roadmap

## Goal

Provide a reusable, clean Instagram API boundary that lets a consuming application use one of its already-authorized Instagram Professional account connections to:

1. read the selected connected account/profile;
2. read owned posts/media/reels for that connection;
3. list/read conversations and messages;
4. receive new-message webhooks and correlate them to the correct connection;
5. send eligible message replies through the correct connection;
6. list/read comments;
7. receive comment webhooks and correlate them to the correct connection;
8. reply publicly to comments;
9. use supported private-reply flows;
10. expose normalized events/actions to host automation or LLM orchestration;
11. support explicitly documented Instagram Live comment capabilities where available.

The package must not authenticate local application users and must not contain LLM decision logic.

A host user may own multiple Instagram connections. Therefore, all account-scoped use cases must operate with explicit connection context and must never assume one Instagram account per user.

## Stage 0 — Provider capability matrix

Status: **Complete (2026-09-04)**. See [`docs/PROVIDER_CAPABILITY_MATRIX.md`](docs/PROVIDER_CAPABILITY_MATRIX.md).

Build and maintain a verified matrix against current Meta documentation for:

- account/profile fields;
- media types and fields;
- posts/reels retrieval;
- conversations/messages retrieval;
- outbound message types;
- messaging eligibility restrictions;
- comment retrieval;
- public replies;
- private replies and reply windows;
- webhook event types;
- provider account identifiers available in webhook payloads for connection routing;
- required permissions for every capability;
- API host/version requirements;
- pagination/rate-limit behavior;
- Instagram Live comment behavior;
- any unsupported Live media/session/video-stream capability.

Initial expected permissions supplied by the connection layer:

```text
instagram_business_basic
instagram_business_manage_messages
instagram_business_manage_comments
```

Optional features may introduce additional explicit permissions later.

Exit criteria:

- every planned capability links to a verified provider capability/permission;
- webhook routing can identify the provider Instagram account needed to resolve the correct connection;
- unsupported or uncertain Live behavior is marked conditional rather than promised.

## Stage 1 — Core contracts and connection-aware provider boundary

Define small capability-oriented contracts such as:

```text
InstagramConnectionId
InstagramAccessTokenProvider
InstagramConnectionReader
InstagramAccountReader
InstagramMediaReader
InstagramConversationReader
InstagramMessageReader
InstagramMessageSender
InstagramCommentReader
InstagramCommentReplier
InstagramWebhookVerifier
InstagramWebhookParser
```

Define normalized application/domain models for provider data without leaking Meta DTOs.

Rules:

- Instagram IDs are opaque strings;
- contracts are explicitly implemented;
- no Meta HTTP details in application services;
- no direct auth-package persistence access;
- account-scoped contracts accept explicit connection context;
- no global/implicit active connection exists inside the package.

Exit criteria:

- application contracts can be unit-tested entirely with fakes;
- tests demonstrate two Instagram connections can be used independently for the same host user.

## Stage 2 — Meta HTTP foundation

Implement shared provider infrastructure with clear responsibility boundaries:

- HTTP transport abstraction/client;
- request builder;
- API version/base URL configuration;
- authorization header/token injection through a connection-aware access-token provider;
- response/error decoder;
- pagination cursor mapper;
- timeout configuration;
- safe retry policy for eligible requests;
- structured masked logging/observability hooks.

Do not create a generic god client. Feature-specific clients should depend on shared transport primitives.

Exit criteria:

- Meta provider errors are normalized consistently;
- secrets are not logged;
- timeout/retry behavior is covered by tests;
- token lookup cannot silently fall back from one connection to another.

## Stage 3 — Account/profile capability

- Implement selected connected professional account reader.
- Require explicit connection context.
- Map supported account/profile fields.
- Validate selected connection usability and required basic permission.
- Add provider contract and mapper tests.

Exit criteria:

- host can display any selected connected Instagram account reliably.

## Stage 4 — Media/posts/reels reading

- List owned media for a selected connection.
- Read supported media details.
- Support cursor pagination.
- Normalize media type/status/URLs/captions/timestamps where exposed.
- Handle deleted/unavailable media explicitly.
- Add posts/reels coverage based on current Meta capability matrix.

Exit criteria:

- host can browse supported media for a selected Instagram connection without Meta DTO leakage.

## Stage 5 — Conversations and message reading

- List conversations available to the selected professional-account connection.
- Read messages in a conversation.
- Read supported sender/timestamp/message details.
- Support pagination.
- Represent unsupported/missing shared-media details accurately.
- Enforce `instagram_business_manage_messages` for the selected connection at the application boundary.

Document provider limitations explicitly, including that conversation initiation is governed by Meta policy and the package must not imply arbitrary proactive messaging.

Exit criteria:

- host can build an inbox scoped to a selected Instagram connection;
- conversation reads cannot cross connection boundaries accidentally.

## Stage 6 — Outbound messaging

Implement supported message sending behind focused sender contracts.

Initial scope should prioritize:

- text replies;
- supported media replies where required;
- reply-to-existing-conversation behavior.

Later supported message types may be added only after capability verification.

Requirements:

- require explicit connection context;
- validate selected connection and permission;
- validate recipient/conversation eligibility where possible;
- normalize policy/window errors;
- avoid unsafe retries for non-idempotent sends;
- provide host idempotency/correlation support where possible;
- never send through a different connection when the selected connection is unavailable.

Exit criteria:

- host can reply to an eligible inbound Instagram conversation through the intended Instagram connection.

## Stage 7 — Comment reading

- List/read comments on supported owned media for a selected connection.
- Map commenter identity, text, timestamps, media references, and reply relationships where exposed.
- Support pagination.
- Enforce `instagram_business_manage_comments` for the selected connection.
- Handle deleted/hidden/inaccessible comments explicitly.

Exit criteria:

- host can render comments scoped to a selected Instagram connection.

## Stage 8 — Public and private comment replies

- Implement supported public comment reply operations with explicit connection context.
- Implement supported private-reply-to-comment operations as a distinct use case.
- Model reply eligibility/window constraints explicitly.
- Normalize provider errors for expired/ineligible replies.
- Treat Instagram Live private-reply behavior separately because its timing rules differ.
- Ensure replies are sent through the connection that owns the target media/comment.

Exit criteria:

- host can reply publicly to eligible comments and use private replies only when Meta permits them, without cross-account routing errors.

## Stage 9 — Webhook verification, routing, and HTTP adapter

Implement webhook infrastructure as independent responsibilities:

```text
verification handshake
signature/authenticity validation
payload parsing
provider DTO mapping
provider account identity extraction
normalized event creation
idempotency/deduplication
host connection-resolution boundary
host event dispatch boundary
```

Provide optional thin FastAPI adapters conceptually for:

```text
GET  /webhooks/instagram
POST /webhooks/instagram
```

The package should emit/return normalized events but must not call host LLM/automation logic directly.

Normalized webhook events must preserve enough provider account identity for the host to resolve which `InstagramConnection` owns the event.

Exit criteria:

- unauthentic webhook requests are rejected;
- duplicate webhook delivery does not produce duplicate host effects when configured with a durable idempotency store;
- events from multiple connected Instagram accounts route deterministically to the correct host connection;
- parsing is covered with representative Meta payload fixtures.

## Stage 10 — Messaging webhook events

- Normalize new-message events.
- Normalize supported message metadata/event variants.
- Preserve provider event IDs/correlation identifiers needed for deduplication.
- Preserve provider account identity required to resolve the connection.
- Provide a clean host dispatch interface.

Target host flow:

```text
Instagram
   ↓
webhook
   ↓
InstagramMessageReceived
   ↓
resolve InstagramConnection
   ↓
host automation / LLM
   ↓
reply command using same connection
   ↓
InstagramMessageSender
```

Exit criteria:

- a new inbound DM can trigger a host-owned automation workflow without provider payload coupling;
- the response can be routed through the same Instagram connection that received the DM.

## Stage 11 — Comment webhook events

- Normalize supported comment-created/changed events.
- Include media/commenter/provider-account references needed by host logic.
- Support host correlation with media/comment readers when webhook payloads are intentionally minimal.

Target host flow:

```text
Instagram comment
      ↓
webhook
      ↓
InstagramCommentCreated
      ↓
resolve InstagramConnection
      ↓
host automation / LLM
      ↓
reply command using same connection
      ↓
InstagramCommentReplier
```

Exit criteria:

- a new comment can trigger a host-owned automation workflow and eligible reply through the correct Instagram connection.

## Stage 12 — Live comment capability

Treat Instagram Live as an explicitly gated capability.

### Supported/verified work

- Verify current Meta webhook/comment behavior for comments made on Instagram Live.
- Implement Live comment event normalization only if exposed through supported webhook contracts.
- Preserve account/connection routing identity for Live comment events.
- Implement supported private reply behavior during the Live broadcast when current Meta API permits it.
- Add capability flags so hosts can distinguish normal-media comments from Live-specific constraints.

### Conditional research

Investigate whether the current public Instagram API provides supported endpoints for:

- discovering an active Live session as media;
- reading broader live-session metadata;
- retrieving historical Live comments beyond webhook-supported behavior.

### Explicitly not promised

Do not claim support for ingesting/reading the live video/audio stream unless Meta exposes a documented supported public API for it.

Exit criteria:

- README/capability matrix accurately distinguishes verified Live comment support from unsupported Live-stream access.

## Stage 13 — Durable webhook idempotency and operational resilience

- Define injected `WebhookEventDeduplicator`/store contract.
- Provide optional SQLAlchemy implementation if justified.
- Add atomic duplicate detection.
- Define poison-event/error handling boundary.
- Expose structured events/metrics for provider failures, signature rejection, rate limits, and repeated webhook duplicates.
- Document multi-worker deployment requirements.
- Include connection/account correlation keys in observability without leaking credentials.

Exit criteria:

- production hosts can safely run multiple workers/instances without duplicate event processing caused by provider retries;
- operational logs make cross-account routing diagnosable without exposing secrets.

## Stage 14 — Consumer integration with hamresan-instagram-auth

Create a reference consumer demonstrating:

```text
hamresan-identity
hamresan-instagram-auth
hamresan-instagram-api
FastAPI
host-owned SQLAlchemy/Alembic
host-owned automation stub
```

Scenario:

1. user authorizes a first Instagram account;
2. host creates/maps local user;
3. host stores the authorized connection;
4. same local user authorizes a second Instagram account;
5. host stores another independent connection;
6. host selects one connection and API package reads account/media;
7. webhook receives a DM/comment for either account;
8. host resolves the owning connection;
9. host automation decides on a reply;
10. API package sends the reply through the same connection.

Packages must integrate only through public contracts and host composition.

Exit criteria:

- no cross-package repository/model access;
- no circular dependencies;
- multiple Instagram connections for one local user remain isolated;
- end-to-end integration test passes.

## Stage 15 — Production/App Review hardening

- Document Standard vs Advanced Access requirements.
- Document Meta App Review prerequisites for third-party professional accounts.
- Verify every requested permission is justified by an implemented feature.
- Add provider API-version compatibility policy.
- Add rate-limit/backoff strategy based on current Meta behavior.
- Add production observability and masked structured logging guidance.
- Add cross-account isolation/authorization tests.
- Add wheel smoke tests and public API checks.
- Run Ruff, format check, strict Pyright, unit/integration tests, and branch coverage gate.

## Final acceptance scenario

A local user has already connected one or more eligible Instagram Professional accounts through `hamresan-instagram-auth`.

The consuming application can then select a specific connection and:

- display that connected Instagram profile;
- list/read supported posts/media/reels;
- display supported conversations and messages;
- receive a new DM through a webhook and resolve the correct connection;
- let host-owned automation/LLM decide a response;
- send the eligible DM reply through the same connection;
- list/read comments on supported media;
- receive a new comment through a webhook and resolve the correct connection;
- let host-owned automation/LLM decide a response;
- publish an eligible comment reply through the same connection;
- use supported private comment replies;
- handle verified Instagram Live comment capabilities without claiming unsupported Live-stream access.

No operation may silently use a different Instagram connection because another connection belongs to the same local user.
