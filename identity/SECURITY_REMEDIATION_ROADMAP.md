# Identity Security Remediation Roadmap

This roadmap tracks remediation of the August 2026 security audit for the passwordless OTP authentication flow.

## Principles

- Preserve clean architecture boundaries: application services must not depend on SQLAlchemy or HTTP details.
- Put concurrency guarantees at the persistence boundary behind repository contracts.
- Prefer default-deny security policies.
- Keep provider- and deployment-specific controls behind explicit abstractions.
- Add regression tests for every security invariant before considering a finding closed.
- Keep security findings in focused PRs so review and rollback remain straightforward.

## Status legend

- **Closed**: production behavior and regression tests are implemented.
- **Mostly closed**: the primary issue is fixed but one follow-up remains.
- **In progress**: implementation is currently under review.
- **Planned**: finding remains open.
- **Accepted tradeoff**: documented behavior that is not currently treated as a security defect.

## Phase 1 — Authentication correctness and account-takeover blockers

### P1.1 — Atomic OTP verification and consumption — C-1

Status: **Mostly closed**

Completed:
- OTP challenges are read under a row lock during verification.
- Failed-attempt counters are incremented atomically in persistence.
- Validation, attempt accounting, successful consumption, and session creation remain inside one transaction.
- Regression tests enforce the configured attempt ceiling.

Remaining:
- Add PostgreSQL concurrency integration coverage proving one OTP cannot create multiple sessions and failed attempts cannot be lost under parallel verification.

### P1.2 — Default-deny OTP purpose handling — H-3

Status: **Closed**

### P1.3 — User status enforcement — M-1

Status: **Closed**

## Phase 2 — Session and refresh-token security

### P2.1 — Atomic refresh rotation and reuse detection — H-2

Status: **Mostly closed**

Completed:
- Refresh rotation locks the current session.
- Refresh-token reuse is detected and revokes the active family.
- Refresh families have a fixed absolute expiration.

Remaining:
- Add PostgreSQL concurrent-refresh integration coverage.

### P2.2 — Session recovery controls — M-8

Status: **Closed**

- Authenticated users can revoke all active sessions.
- The public API exposes a bulk-revocation use case for trusted host/operator recovery workflows.
- Bulk revocation is implemented as one persistence operation and emits a security event.
- Session listing remains optional and is not required to close the recovery gap.

## Phase 3 — Abuse resistance

### P3.1 — Rate limiting — M-3

Status: **Mostly closed**

Completed:
- Application-level `RateLimiter` abstraction exists.
- OTP request limits apply by canonical destination.
- OTP verification limits apply by challenge.
- Daily destination limits are supported.
- In-memory baseline implementation exists and distributed implementations can be injected.
- OTP request limits also apply by trusted requester/IP across different destinations.
- FastAPI resolves requester IP server-side through `RequestMetadataResolver`; the default resolver ignores forwarding headers.
- Trusted proxy deployment requirements and distributed/edge throttling guidance are documented in `RATE_LIMITING.md`.
- Trusted per-IP/requester OTP rate limiting has been implemented and merged into `main`.

Remaining:
- Validate the trusted requester/IP flow with the full quality suite before closing M-3.
- Keep coarse traffic throttling at nginx/API-gateway level as a deployment responsibility.

### P3.2 — OTP request cooldown behavior — H-1

Status: **Closed**

### P3.3 — Account enumeration — M-2

Status: **Closed**

## Phase 4 — Input, metadata, and secret hardening

### P4.1 — Identity normalization and validation — M-5

Status: **Closed**

### P4.2 — Secret requirements — M-4

Status: **Closed**

### P4.3 — Trusted request metadata — M-6

Status: **Closed**

## Phase 5 — Detection, recovery, operations, and cleanup

### P5.1 — Security event logging — M-7

Status: **Closed**

- A host-facing `SecurityEventSink` contract exists.
- Structured events cover OTP failures/exhaustion, rate-limit rejection, refresh reuse, and session revocation.
- Events avoid OTP codes, raw tokens, signing secrets, and raw destination PII.
- Hosts can route events to logging, metrics, or SIEM providers.

### P5.2 — Data retention and cleanup — M-9

Status: **Closed**

- OTP and session retention windows are configurable.
- Cleanup runs in bounded batches.
- The package exposes a host-invoked cleanup use case and does not own scheduling.
- Host scheduling guidance is documented.

### P5.3 — Hot-query indexes — L-6

Status: **Closed**

- The OTP latest-active lookup has a composite index on `(normalized_destination, purpose, created_at)`.
- Metadata regression coverage verifies index shape and column order.
- Existing-database migration requirements are documented.

## Phase 6 — Low-severity hardening and API cleanup

### P6.1 — Access-token error isolation — L-3

Status: **Closed**

- Invalid/unacceptable access-token credentials use public `AccessTokenAuthenticationError`.
- FastAPI maps only that typed authentication error to HTTP 401.
- Unexpected infrastructure/programming failures propagate instead of being masked as authentication failures.
- Regression coverage distinguishes invalid credentials from backend failures.

### P6.2 — JWT codec expiry safety — L-1

Status: **Closed**

- JWT codec verification enables PyJWT expiration validation instead of passing `verify_exp=False`.
- Direct codec consumers reject expired tokens without relying on the higher-level authenticator.
- The authenticator keeps its explicit expiration check as defense in depth and for fake/test verifiers.
- Regression coverage verifies expired JWTs are rejected by the codec itself.

### P6.3 — OTP notification consistency — L-2

Status: **Closed**

- A newly created OTP challenge is not committed until notification dispatch has been accepted successfully.
- Notification dispatch failure exits the unit of work with an exception, so the pending challenge is rolled back and does not create a cooldown for an OTP the user never received.
- Regression coverage verifies that a failed first dispatch can be retried immediately and causes a second notification attempt rather than reusing an undelivered challenge.
- A future transactional outbox remains the preferred architecture if identity and notification persistence are later coordinated in one durable transaction.

### P6.4 — Dead or misleading model/public members — L-4

Status: **Closed**

- Removed the unused `AuthenticatedPrincipal.permissions` member so the public principal no longer implies authorization behavior the package does not implement.
- Removed the extra `SqlAlchemyIdentityUnitOfWork.transaction()` helper because it was outside the unit-of-work contract and created a second transaction API with unclear semantics.
- Aligned package metadata with the implemented authentication/session scope rather than claiming authorization support.
- Retained persisted compatibility fields (`UserIdentity.value`, `OtpChallenge.destination_snapshot`, `User.updated_at`, and `Session.last_used_at`) without destructive schema changes and documented their current non-authoritative semantics.

### P6.5 — Authenticated-request database lookup — L-5

Status: **Accepted tradeoff / optional optimization**

- Database-backed session validation intentionally gives immediate revocation semantics.
- Consider an optional short-TTL `SessionReader` cache only when throughput measurements justify it.

### P6.6 — HMAC key rotation — L-7

Status: **Closed**

- New OTP and refresh-token hashes are versioned with a key identifier and are written only with the current HMAC key.
- Verification accepts explicitly configured active previous keys during an overlap window.
- Legacy unversioned hashes remain verifiable during migration using the active key set.
- Refresh-token lookup is rotation-aware by querying all active versioned and legacy hash candidates, so pre-rotation sessions remain usable during the configured overlap period.
- Operational normal-rotation and compromised-key procedures are documented in `HMAC_KEY_ROTATION.md`.
- Regression coverage includes previous-key verification, legacy hashes, unknown/retired keys, and refresh-session continuity across a key rotation.
- HMAC digest calculation, hash formatting, key validation, and keyring responsibilities are separated into dedicated components; the hasher remains a focused orchestrator.

## Final verification work

Before calling the audit fully remediated:

1. add PostgreSQL concurrency integration tests for C-1 and H-2;
2. complete full-quality-suite validation of the already-merged trusted per-IP/requester rate limiting and close M-3;
3. rerun the original hostile audit against the updated `main` branch;
4. confirm deployment guidance covers Redis/distributed rate limiting, nginx trusted proxies, retention jobs, and schema migrations;
5. confirm no event/log path contains OTP codes, raw tokens, secrets, or unnecessary PII.

## Definition of Done

A security finding is closed only when:

1. the invariant is enforced in production code;
2. the behavior has regression tests;
3. concurrency-sensitive findings have PostgreSQL integration tests before the audit is considered fully complete;
4. public/deployment responsibilities are documented;
5. no clean-architecture boundary is weakened to implement the fix.
