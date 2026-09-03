# hamresan-instagram-api Roadmap

## Goal

Provide a reusable, clean Instagram API boundary that lets a consuming application use an already-authorized Instagram Professional account to:

1. read the connected account/profile;
2. read owned posts/media/reels;
3. list/read conversations and messages;
4. receive new-message webhooks;
5. send eligible message replies;
6. list/read comments;
7. receive comment webhooks;
8. reply publicly to comments;
9. use supported private-reply flows;
10. expose normalized events/actions to host automation or LLM orchestration;
11. support explicitly documented Instagram Live comment capabilities where available.

The package must not authenticate local application users and must not contain LLM decision logic.

## Stage 0 — Provider capability matrix

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
- unsupported or uncertain Live behavior is marked conditional rather than promised.

## Stage 1 — Core contracts and provider boundary

Define small capability-oriented contracts such as:

```text
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
- no direct auth-package persistence access.

Exit criteria:

- application contracts can be unit-tested entirely with fakes.

## Stage 2 — Meta HTTP foundation

Implement shared provider infrastructure with clear responsibility boundaries:

- HTTP transport abstraction/client;
- request builder;
- API version/base URL configuration;
- authorization header/token injection through an access-token provider;
- response/error decoder;
- pagination cursor mapper;
- timeout configuration;
- safe retry policy for eligible requests;
- structured masked logging/observability hooks.

Do not create a generic god client. Feature-specific clients should depend on shared transport primitives.

Exit criteria:

- Meta provider errors are normalized consistently;
- secrets are not logged;
- timeout/retry behavior is covered by tests.

## Stage 3 — Account/profile capability

- Implement connected professional account reader.
- Map supported account/profile fields.
- Validate connection usability and required basic permission.
- Add provider contract and mapper tests.

Exit criteria:

- host can display the connected Instagram account reliably.

## Stage 4 — Media/posts/reels reading

- List owned media.
- Read supported media details.
- Support cursor pagination.
- Normalize media type/status/URLs/captions/timestamps where exposed.
- Handle deleted/unavailable media explicitly.
- Add posts/reels coverage based on current Meta capability matrix.

Exit criteria:

- host can browse the connected account's supported media without Meta DTO leakage.

## Stage 5 — Conversations and message reading

- List conversations available to the professional account.
- Read messages in a conversation.
- Read supported sender/timestamp/message details.
- Support pagination.
- Represent unsupported/missing shared-media details accurately.
- Enforce `instagram_business_manage_messages` at the application boundary.

Document provider limitations explicitly, including that conversation initiation is governed by Meta policy and the package must not imply arbitrary proactive messaging.

Exit criteria:

- host can build an inbox from supported Instagram conversations/messages.

## Stage 6 — Outbound messaging

Implement supported message sending behind focused sender contracts.

Initial scope should prioritize:

- text replies;
- supported media replies where required;
- reply-to-existing-conversation behavior.

Later supported message types may be added only after capability verification.

Requirements:

- validate connection and permission;
- validate recipient/conversation eligibility where possible;
- normalize policy/window errors;
- avoid unsafe retries for non-idempotent sends;
- provide host idempotency/correlation support where possible.

Exit criteria:

- host can reply to an eligible inbound Instagram conversation through a clean application API.

## Stage 7 — Comment reading

- List/read comments on supported owned media.
- Map commenter identity, text, timestamps, media references, and reply relationships where exposed.
- Support pagination.
- Enforce `instagram_business_manage_comments`.
- Handle deleted/hidden/inaccessible comments explicitly.

Exit criteria:

- host can render comments for supported owned media.

## Stage 8 — Public and private comment replies

- Implement supported public comment reply operations.
- Implement supported private-reply-to-comment operations as a distinct use case.
- Model reply eligibility/window constraints explicitly.
- Normalize provider errors for expired/ineligible replies.
- Treat Instagram Live private-reply behavior separately because its timing rules differ.

Exit criteria:

- host can reply publicly to eligible comments and use private replies only when Meta permits them.

## Stage 9 — Webhook verification and HTTP adapter

Implement webhook infrastructure as independent responsibilities:

```text
verification handshake
signature/authenticity validation
payload parsing
provider DTO mapping
normalized event creation
idempotency/deduplication
host event dispatch boundary
```

Provide optional thin FastAPI adapters conceptually for:

```text
GET  /webhooks/instagram
POST /webhooks/instagram
```

The package should emit/return normalized events but must not call host LLM/automation logic directly.

Exit criteria:

- unauthentic webhook requests are rejected;
- duplicate webhook delivery does not produce duplicate host effects when configured with a durable idempotency store;
- parsing is covered with representative Meta payload fixtures.

## Stage 10 — Messaging webhook events

- Normalize new-message events.
- Normalize supported message metadata/event variants.
- Preserve provider event IDs/correlation identifiers needed for deduplication.
- Provide a clean host dispatch interface.

Target host flow:

```text
Instagram
   ↓
webhook
   ↓
InstagramMessageReceived
   ↓
host automation / LLM
   ↓
reply command
   ↓
InstagramMessageSender
```

Exit criteria:

- a new inbound DM can trigger a host-owned automation workflow without provider payload coupling.

## Stage 11 — Comment webhook events

- Normalize supported comment-created/changed events.
- Include media/commenter references needed by host logic.
- Support host correlation with media/comment readers when webhook payloads are intentionally minimal.

Target host flow:

```text
Instagram comment
      ↓
webhook
      ↓
InstagramCommentCreated
      ↓
host automation / LLM
      ↓
reply command
      ↓
InstagramCommentReplier
```

Exit criteria:

- a new comment can trigger a host-owned automation workflow and eligible reply.

## Stage 12 — Live comment capability

Treat Instagram Live as an explicitly gated capability.

### Supported/verified work

- Verify current Meta webhook/comment behavior for comments made on Instagram Live.
- Implement Live comment event normalization only if exposed through supported webhook contracts.
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

Exit criteria:

- production hosts can safely run multiple workers/instances without duplicate event processing caused by provider retries.

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

1. user authorizes Instagram;
2. host creates/maps local user;
3. host stores authorized connection;
4. API package reads account/media;
5. webhook receives a DM/comment;
6. host automation decides on a reply;
7. API package sends the reply.

Packages must integrate only through public contracts and host composition.

Exit criteria:

- no cross-package repository/model access;
- no circular dependencies;
- end-to-end integration test passes.

## Stage 15 — Production/App Review hardening

- Document Standard vs Advanced Access requirements.
- Document Meta App Review prerequisites for third-party professional accounts.
- Verify every requested permission is justified by an implemented feature.
- Add provider API-version compatibility policy.
- Add rate-limit/backoff strategy based on current Meta behavior.
- Add production observability and masked structured logging guidance.
- Add wheel smoke tests and public API checks.
- Run Ruff, format check, strict Pyright, unit/integration tests, and branch coverage gate.

## Final acceptance scenario

A user has already connected an eligible Instagram Professional account through `hamresan-instagram-auth`.

The consuming application can then:

- display the connected Instagram profile;
- list/read supported posts/media/reels;
- display supported conversations and messages;
- receive a new DM through a webhook;
- let host-owned automation/LLM decide a response;
- send the eligible DM reply;
- list/read comments on supported media;
- receive a new comment through a webhook;
- let host-owned automation/LLM decide a response;
- publish an eligible comment reply;
- use supported private comment replies;
- handle verified Instagram Live comment capabilities without claiming unsupported Live-stream access.
