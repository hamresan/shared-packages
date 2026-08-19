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

- Public HTTP OTP purposes are restricted to implemented flows.
- Purpose policy is default-deny.
- Verification uses explicit supported-purpose branches.
- Unsupported verification/change/recovery purposes cannot implicitly create login sessions.
- Regression tests cover supported and unsupported purposes.

### P1.3 — User status enforcement — M-1

Status: **Closed**

- Non-active users cannot obtain new authenticated sessions.
- Access-token authentication checks current user status.
- `PENDING`, `SUSPENDED`, and `DISABLED` are rejected.
- Regression tests cover login and existing access-token behavior.

## Phase 2 — Session and refresh-token security

### P2.1 — Atomic refresh rotation and reuse detection — H-2

Status: **Mostly closed**

Completed:
- Refresh rotation locks the current session.
- A refresh token cannot create more than one legitimate successor.
- Refresh-token reuse is detected.
- Reuse revokes the active token family.
- Refresh families have a fixed absolute expiration independent of sliding session TTL.
- Regression tests cover rotation, reuse, and absolute family lifetime.

Remaining:
- Add PostgreSQL concurrent-refresh integration coverage.

### P2.2 — Session recovery controls — M-8

Status: **Planned**

- Add revoke-all-user-sessions capability.
- Add session listing only if required by the host product.
- Keep public APIs minimal and authenticated.
- Support incident recovery without direct database manipulation.

## Phase 3 — Abuse resistance

### P3.1 — Rate limiting — M-3

Status: **Mostly closed**

Completed:
- Application-level `RateLimiter` abstraction exists.
- OTP request limits apply by canonical destination.
- OTP verification limits apply by challenge.
- Daily destination limits are supported.
- In-memory baseline implementation exists and distributed implementations can be injected.

Remaining:
- Add trusted per-IP/requester limits now that server-resolved request metadata exists.
- Keep coarse traffic throttling at nginx/API-gateway level for deployment defense in depth.

### P3.2 — OTP request cooldown behavior — H-1

Status: **Closed**

- Anonymous requesters can no longer monopolize another user's login challenge lifecycle.
- Repeated requests inside the resend window return the active challenge instead of locking out the legitimate user.
- Consumed/expired challenges do not block new requests.
- Regression tests cover idempotent cooldown and consumed-challenge behavior.

### P3.3 — Account enumeration — M-2

Status: **Closed**

- Unauthenticated OTP initiation no longer discloses account existence through registration/login mismatch behavior.
- Account-state mismatch is evaluated only after OTP ownership is proven.
- Rate limiting applies before the flow can be abused at scale.

## Phase 4 — Input, metadata, and secret hardening

### P4.1 — Identity normalization and validation — M-5

Status: **Closed**

- Unicode NFKC normalization is applied before canonicalization.
- Mobile identities use canonical international form with `00` to `+` conversion.
- Unicode decimal digits are converted to ASCII digits.
- E.164-style format is enforced without unsafe default-region guessing.
- Email identities are case-folded and malformed/whitespace/control-character inputs are rejected.
- Canonical values feed uniqueness and abuse-control keys.
- Regression tests cover equivalent phone representations and malformed identity input.

### P4.2 — Secret requirements — M-4

Status: **Closed**

- HMAC signing secrets require at least 32 bytes of key material.
- Weak configuration fails fast at startup.
- Regression tests cover below-threshold rejection and minimum-length acceptance.

### P4.3 — Trusted request metadata — M-6

Status: **Closed**

- Authoritative IP/device metadata is no longer accepted from public request bodies.
- Direct client IP is resolved from the server request context by default.
- Forwarded headers are ignored unless a trusted-proxy resolver is explicitly configured.
- Host deployment behind nginx/proxies is documented.

## Phase 5 — Detection, recovery, operations, and cleanup

### P5.1 — Security event logging — M-7

Status: **In progress**

- Add a host-facing security event sink contract.
- Emit structured events for failed OTP verification, exhausted attempts, rate-limit rejection, refresh reuse, and session revocation.
- Never include OTP codes, raw refresh tokens, signing secrets, or other credentials.
- Prefer stable IDs and non-reversible identifiers over raw PII in events.
- Provide a safe default implementation and allow hosts to route events to logging/metrics/SIEM providers.

### P5.2 — Data retention and cleanup — M-9

Status: **Planned**

- Define retention windows for expired/consumed OTP challenges and expired/revoked sessions.
- Provide cleanup repository/use-case contracts or explicit host scheduling guidance.
- Ensure cleanup can run in bounded batches.

### P5.3 — Hot-query indexes — L-6

Status: **Planned**

- Add a composite index supporting OTP active/latest lookup, based on the actual query shape.
- Review redundant single-column indexes after the composite index is introduced.
- Document required host migration changes.

## Phase 6 — Low-severity hardening and API cleanup

### P6.1 — Access-token error isolation — L-3

Status: **Planned**

- Replace broad authentication `except Exception` handling with explicit authentication exceptions.
- Preserve unexpected infrastructure/programming failures as 5xx/503-class errors instead of masking them as 401.

### P6.2 — JWT codec expiry safety — L-1

Status: **Planned**

- Remove the public-API trap created by `verify_exp=False`.
- Either enforce expiry inside the codec or narrow the codec's public/reusable surface.
- Keep deterministic testability without weakening direct codec use.

### P6.3 — OTP notification consistency — L-2

Status: **Planned**

- Prevent a notification enqueue failure from leaving a fresh cooldown/challenge that was never delivered.
- Prefer a transactional/outbox-safe design; otherwise explicitly invalidate the new challenge on send failure.

### P6.4 — Dead or misleading model/public members — L-4

Status: **Planned**

- Review `destination_snapshot`, `UserIdentity.value`, `User.updated_at`, `AuthenticatedPrincipal.permissions`, `IdentityUnitOfWork.transaction()`, and `Session.last_used_at`.
- Remove or implement members whose public/domain meaning is currently misleading.
- Align package description with actual authorization capabilities.

### P6.5 — Authenticated-request database lookup — L-5

Status: **Accepted tradeoff / optional optimization**

- Database-backed session validation intentionally gives immediate revocation semantics.
- Consider an optional short-TTL `SessionReader` cache only when throughput measurements justify it.

### P6.6 — HMAC key rotation — L-7

Status: **Planned**

- Introduce versioned/key-identified hashes.
- Verify with active keys while writing with the current key.
- Document operational rotation and emergency-compromise procedures.

## Final verification work

Before calling the audit fully remediated:

1. add PostgreSQL concurrency integration tests for C-1 and H-2;
2. rerun the original hostile audit against the updated `main` branch;
3. confirm deployment guidance covers Redis/distributed rate limiting, nginx trusted proxies, retention jobs, and schema migrations;
4. confirm no event/log path contains OTP codes, raw tokens, secrets, or unnecessary PII.

## Definition of Done

A security finding is closed only when:

1. the invariant is enforced in production code;
2. the behavior has regression tests;
3. concurrency-sensitive findings have PostgreSQL integration tests before the audit is considered fully complete;
4. public/deployment responsibilities are documented;
5. no clean-architecture boundary is weakened to implement the fix.
