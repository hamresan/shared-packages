# Provider capability matrix

Verified on: 2026-09-04

This document implements Roadmap Stage 0 for `hamresan-instagram-api`.

The package targets **Instagram API with Instagram Login** for Instagram Professional accounts
(Business and Creator). The capability matrix is based on current Meta-owned Instagram API
documentation published in Meta's official Postman workspace and the linked Meta developer
documentation.

Stage 0 is documentation-only. It does not define application contracts, HTTP clients, domain
models, or provider adapters. Those belong to later roadmap stages.

## Verification policy

Each capability is classified as one of:

- **Verified**: current Meta documentation explicitly supports the capability.
- **Conditional**: Meta documents part of the behavior, but the package must re-check the exact
  endpoint/field/provider behavior during the implementation stage before exposing it as a stable
  public capability.
- **Unsupported / not promised**: no verified public API capability was found for the planned
  behavior, so the package must not claim support.

Meta IDs are treated as opaque strings. No capability may infer or silently switch the selected
Instagram connection.

## Provider baseline

| Concern | Verified provider behavior | Package decision |
| --- | --- | --- |
| Supported accounts | Instagram Professional Business and Creator accounts | Supported |
| Consumer/personal accounts | Not supported by this API setup | Out of scope |
| Login/API family | Instagram API with Instagram Login | Primary provider path |
| API host | `graph.instagram.com` | Configurable provider base URL, defaulting to the documented host |
| Access token | Instagram User access token | Supplied through the host authorization boundary in later stages |
| Base permission | `instagram_business_basic` | Required for account-scoped basic/profile/media capabilities |
| Messaging permission | `instagram_business_manage_messages` | Required for conversations/messages/send capabilities |
| Comment permission | `instagram_business_manage_comments` | Required for comment read/reply capabilities |
| Content publishing permission | `instagram_business_content_publish` | Not required by the current roadmap read/reply scope; do not request only for unused features |
| Ads/tagging | Instagram Login setup does not provide ads or tagging access | Out of scope |
| Access level | Standard Access for owned/managed test accounts; Advanced Access for accounts the app does not own/manage | Production/App Review concern, revisited in Stage 15 |

The older scope names such as `business_basic` and `business_manage_messages` were deprecated;
the package must use the `instagram_business_*` permission names.

## Capability matrix

### Account and profile

Status: **Verified capability; field selection is implementation-gated**

The API supports reading the selected Instagram Professional account/profile with
`instagram_business_basic`.

Planned Stage 3 data includes the provider account ID and supported profile fields such as username,
display name, biography, website, profile picture URL, follower/following counts, and media count
when exposed by the current Instagram User object.

Rules:

- Stage 3 must request only fields documented by Meta for the selected API version.
- Optional/missing profile fields must remain optional in normalized models.
- The provider Instagram account ID is the stable correlation key for provider account identity;
  it is not a local connection ID.
- A local `InstagramConnectionId` must remain explicit and separate from provider IDs.

### Media, posts, and reels

Status: **Verified**

The API supports reading media owned by the selected Instagram Professional account and supports
cursor-based pagination.

Relevant documented media data includes:

- media ID;
- caption;
- media type;
- media product type;
- media URL where exposed;
- thumbnail URL where exposed;
- permalink;
- timestamp;
- username/owner information where exposed;
- carousel children where supported.

The package may therefore support reading captions for posts and Reels in Stage 4.

Important constraints:

- field availability varies by media type;
- URLs can be absent or unavailable;
- carousel data can require child-media reads;
- deleted, unavailable, or inaccessible media must be represented explicitly rather than treated as
  an empty successful result;
- the implementation must not promise ordering controls that Meta does not support.

### Pagination

Status: **Verified**

Meta documents cursor-based pagination for Instagram Graph API collection endpoints. Later readers
must model cursors explicitly and must not expose provider paging DTOs directly.

No package-level assumption should be made that all historical objects are indefinitely available.

### Conversations and previous DMs

Status: **Verified with provider retention/visibility limitations**

The Conversations API supports:

- listing conversations for the selected Instagram Professional account;
- finding a conversation with a specific Instagram-scoped user;
- listing messages in a conversation;
- reading message details including sender and sent time.

Permissions:

- `instagram_business_basic`;
- `instagram_business_manage_messages`.

Therefore Stage 5 may expose previous DMs that Meta returns for the selected connection.

Provider limitations that must be preserved:

- the API does not guarantee unlimited message history;
- conversations in the Requests folder that have not been active for 30 days are not returned;
- message IDs can be returned for a conversation while full message details are limited to the 20
  most recent messages;
- messages outside that detail window must remain partial rather than receiving inferred sender or
  message text;
- shared media/message payloads can expose only the image/video URL rather than complete media
  details;
- one professional account converses with one customer per conversation; group messaging is not
  supported.

The package must not describe the feature as "complete DM archive" or "all historical DMs".

### Outbound messaging

Status: **Verified with eligibility restrictions**

The Send API supports replies/messages through the selected Instagram Professional account,
including documented text and supported media/message forms.

Permission:

- `instagram_business_manage_messages`.

Critical eligibility rule:

- a normal conversation is initiated by the Instagram user; the package must not promise arbitrary
  proactive DMs to users who have never contacted the professional account.

Additional rules:

- the message recipient must be eligible under current Meta messaging policy;
- Stage 6 verifies an existing conversation for the recipient through the Conversations API before
  sending;
- the initial send implementation supports text plus documented image/video URL attachments;
- provider request/policy rejections are normalized without guessing undocumented error-code
  subtypes;
- non-idempotent sends must not be blindly retried;
- host correlation identifiers are local metadata only and are not sent to Meta as idempotency keys;
- the selected connection must never fall back to another authorized Instagram account.

### Comment reading

Status: **Verified**

Meta documents comment moderation endpoints for owned Instagram media, including:

- `GET /<IG_MEDIA_ID>/comments`;
- `GET /<IG_COMMENT_ID>/replies`.

Permissions:

- `instagram_business_basic`;
- `instagram_business_manage_comments`.

The package can therefore support:

- reading comments on owned media;
- reading reply relationships;
- reading replies previously published by the account when those replies are returned by the
  documented comment/replies edges;
- commenter identity, comment text, timestamp, media reference, and parent/reply relationships where
  exposed.

Stage 7 must not infer that every historical reply is available if Meta does not return it.

### Public comment replies

Status: **Verified**

Meta documents public replies through:

- `POST /<IG_COMMENT_ID>/replies`.

Permissions:

- `instagram_business_basic`;
- `instagram_business_manage_comments`.

The package must send the reply through the explicit connection that owns the media/comment.

Stage 8 implementation decisions:

- public replies use `POST /<IG_COMMENT_ID>/replies` and are not retried automatically;
- blank reply text is rejected before provider execution;
- provider request/policy rejection is normalized without guessing undocumented error subtypes.

### Private replies to commenters

Status: **Verified with strict eligibility windows**

Meta documents private replies to a person who comments on the professional account's supported
content.

Permissions:

- `instagram_business_basic`;
- `instagram_business_manage_comments`.

Documented restrictions include:

- only one private reply can be sent to the commenter for the triggering comment;
- for normal post/reel comment flows, the private reply must be sent within 7 days of the comment;
- follow-up messages require the recipient to respond and then follow the applicable messaging
  window;
- Instagram Live has a separate rule: the private reply can be sent only while the Live broadcast is
  active.

Stage 8 models standard and Live eligibility separately:

- standard private replies carry the source comment creation time and are rejected locally once the
  documented 7-day window expires;
- Live private replies carry explicit broadcast-active state and are rejected locally when the
  broadcast is no longer active;
- the one-private-reply-per-comment restriction is not simulated with temporary in-memory state;
  duplicate/ineligible attempts are normalized from the Meta provider rejection until durable
  idempotency/state is introduced by its later roadmap stage;
- private reply POST requests are never retried automatically.

### Messaging webhooks and connection routing

Status: **Verified and implemented in Stage 10**

Meta messaging webhook payloads include the professional account identity in the webhook entry and
recipient/sender identifiers in messaging events. Stage 10 normalizes currently documented
messaging payload variants for inbound messages, postbacks, read receipts, reactions, message
edits, and referrals.

This is sufficient for deterministic host routing:

1. receive the provider webhook;
2. extract the provider Instagram Professional account ID;
3. ask the host-owned connection-resolution boundary for the matching local connection;
4. normalize the event with the resolved connection context;
5. process/reply using that same explicit connection.

The package must not look up an "active account" globally.

Stage 10 preserves provider message IDs and deterministic delivery event IDs separately: provider
message IDs remain available for correlation, while Stage 9 deterministic event IDs continue to
drive delivery deduplication.

Unknown messaging variants remain valid generic webhook events with no fabricated normalized
payload. They are not silently reinterpreted as a supported message type.

The implementation must continue to verify the exact subscription field set against the selected
Meta API version when host subscription configuration is added.

### Comment webhooks and connection routing

Status: **Verified**

Meta comment webhook payloads include the professional account ID in the webhook entry and comment
data such as comment ID, commenter identity, text, media ID, and media product type where exposed.

Documented subscription fields relevant to this roadmap include:

- `comments`;
- `live_comments`.

This provides the provider account correlation required to resolve the correct local Instagram
connection before host business/automation logic runs.

### Webhook verification and authenticity

Status: **Verified and implemented in Stage 9**

Stage 9 implements:

- GET verification handshake through an injected verify token;
- HMAC-SHA256 validation of `X-Hub-Signature-256` against the raw request body;
- generic Meta Instagram envelope parsing;
- deterministic event IDs for envelope items that do not expose a provider event ID;
- provider professional-account identity preservation for host connection resolution;
- atomic idempotency boundaries with acquire/complete/release semantics;
- separate host connection-resolution and normalized-event dispatch contracts;
- an optional thin FastAPI presentation adapter for GET/POST webhook routes.

Stage 9 deliberately does not interpret message/comment business semantics; those remain in
Stages 10 and 11.

### Rate limits and retry behavior

Status: **Conditional at operation level**

Meta Graph APIs expose rate-limit/usage behavior that can vary by product, app/account state, and
API version. No single hard-coded request-per-time-window number is safe as a package-wide contract.

Package decision:

- Stage 2 must preserve provider rate-limit errors/headers needed for observability;
- retry only operations that are safe and idempotent;
- use bounded backoff and respect provider retry/rate-limit signals when documented;
- do not retry non-idempotent message/comment sends automatically unless an explicit safe mechanism
  exists.

Exact thresholds must be re-verified for the configured API version rather than embedded in Stage 0.

### API version policy

Status: **Verified requirement; exact version remains configuration**

Meta endpoints are versioned. The package must use an explicit configurable API version and must not
hide an unversioned implicit default inside application/domain code.

Stage 2 will own provider URL/version configuration. Stage 15 will define the compatibility and
upgrade policy.

### Instagram Live comments

Status: **Partially verified and capability-gated**

Verified behavior:

- Meta documents a `live_comments` webhook subscription alongside normal `comments`;
- Meta documents private replies originating from comments on Instagram Live;
- a private reply to a Live commenter is allowed only while the Live broadcast is active.

Conditional behavior:

- active Live media/session discovery;
- broader Live-session metadata;
- historical Live-comment retrieval beyond documented webhook/comment behavior.

These conditional capabilities must not be exposed until a supported public endpoint and permission
are verified during Stage 12.

### Instagram Live video/audio stream

Status: **Unsupported / not promised**

No verified public Instagram API capability was identified for ingesting or reading the raw Live
video/audio stream as required by a generic live-stream reader.

The package must not advertise or model raw Live stream ingestion unless Meta introduces and
documents a supported public API for it.

## Capability-to-roadmap mapping

| Roadmap stage | Capability status after Stage 0 |
| --- | --- |
| Stage 1 — Core contracts | Ready to design against verified capability boundaries |
| Stage 2 — Meta HTTP foundation | Ready; host, versioning, pagination, error/rate-limit constraints identified |
| Stage 3 — Account/profile | Verified, with exact field list re-checked for selected API version |
| Stage 4 — Media/posts/reels | Verified |
| Stage 5 — Conversations/messages | Verified with history/Requests limitations |
| Stage 6 — Outbound messaging | Verified with recipient/conversation eligibility restrictions |
| Stage 7 — Comment reading | Verified |
| Stage 8 — Public/private replies | Verified; private reply windows explicitly constrained |
| Stage 9 — Webhook foundation | Verified routing identity is available |
| Stage 10 — Messaging webhooks | Verified, exact event subscriptions re-checked at implementation |
| Stage 11 — Comment webhooks | Verified for comments; Live remains separately capability-gated |
| Stage 12 — Live comments | Partially verified; discovery/history remain conditional |
| Stage 13 — Durable idempotency | Package concern, not a provider capability |
| Stage 14 — Auth consumer integration | Can integrate later through public contracts only |
| Stage 15 — Production/App Review | Access-level/version/rate-limit policy requires final production re-verification |

## Stage 0 exit-criteria check

- Every planned capability is tied to a verified Meta capability/permission or explicitly marked
  conditional/unsupported.
- Messaging and comment webhooks expose the provider Instagram Professional account identity needed
  for deterministic host-side connection resolution.
- Instagram Live comment/private-reply behavior is separated from unverified Live discovery/history.
- Raw Live video/audio stream ingestion is explicitly not promised.
- No Stage 1 contract or implementation has been introduced.

## Sources

Primary references are Meta-owned Instagram API documentation:

- Meta Instagram API Postman documentation:
  https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api
- Meta Instagram API with Instagram Login:
  https://www.postman.com/meta/instagram/folder/6raa77c/instagram-api-with-instagram-login
- Meta Conversations API:
  https://www.postman.com/meta/instagram/folder/23987686-6a91368f-1fa8-4614-9ed6-7d1e08c21e62
- Meta Private Replies documentation:
  https://www.postman.com/meta/instagram/request/23987686-189d7215-22b3-403f-b2f5-a46c7e66a514

Canonical Meta developer-documentation areas linked from those references:

- Instagram Platform overview:
  https://developers.facebook.com/docs/instagram-platform/overview
- Instagram API with Instagram Login:
  https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login
- Comment moderation:
  https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/comment-moderation
- Instagram comment reference:
  https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-comment

Provider documentation changes over time. Every later implementation stage must re-check the fields,
permissions, policy windows, and endpoint behavior it actually implements against the then-current
Meta documentation.
