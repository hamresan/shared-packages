# Identity Security Remediation Roadmap

This roadmap addresses the findings from the August 2026 security audit of the passwordless OTP authentication flow.

## Principles

- Preserve clean architecture boundaries: application services must not depend on SQLAlchemy or HTTP details.
- Put concurrency guarantees at the persistence boundary behind repository contracts.
- Prefer default-deny security policies.
- Keep provider- and deployment-specific controls behind explicit abstractions.
- Add tests for every security invariant before considering a finding closed.

## Phase 1 — Authentication correctness and account-takeover blockers

### P1.1 — Atomic OTP verification and consumption — C-1

Status: **In progress**

- Read OTP challenges with a database row lock during verification.
- Increment failed-attempt counters atomically in SQL.
- Keep validation, attempt increment, successful consumption, and session creation in one transaction.
- Ensure a consumed OTP cannot create multiple sessions under concurrent verification.
- Add deterministic attempt-limit tests.
- Add a PostgreSQL concurrency regression test before marking C-1 fully closed.

### P1.2 — Default-deny OTP purpose handling — H-3

Status: **Planned**

- Restrict public OTP purposes to flows that are implemented.
- Change purpose policy to default-deny.
- Replace `registration / else` verification branching with explicit supported-purpose handling.
- Ensure verification/change/recovery purposes never implicitly create login sessions.
- Add tests for every supported and unsupported purpose.

### P1.3 — User status enforcement — M-1

Status: **Planned**

- Reject login/session creation for non-active users.
- Enforce user status during access-token authentication.
- Define explicit behavior for `PENDING`, `SUSPENDED`, and `DISABLED`.
- Add regression tests for existing and newly issued sessions.

## Phase 2 — Session and refresh-token security

### P2.1 — Atomic refresh rotation — H-2

- Lock the current session during refresh rotation.
- Prevent one refresh token from creating more than one successor.
- Add refresh-token reuse detection.
- Revoke the active token family when reuse is detected.
- Add a fixed absolute family expiration independent of sliding refresh TTL.
- Add PostgreSQL concurrent-refresh tests.

### P2.2 — Session recovery controls — M-8

- Add revoke-all-user-sessions capability.
- Add session listing only if required by the host product.
- Keep public APIs minimal and explicit.

## Phase 3 — Abuse resistance

### P3.1 — Rate limiting — M-3

- Introduce an application-level rate-limiter contract for semantic identity limits.
- Limit OTP requests by destination and requester identity.
- Limit OTP verification by challenge and requester/IP.
- Add daily destination limits and abuse thresholds where appropriate.
- Keep coarse traffic throttling at nginx/API-gateway level.
- Provide a Redis-backed implementation for multi-instance deployments.

### P3.2 — OTP request cooldown behavior — H-1

- Avoid allowing an anonymous requester to monopolize another user's login challenge lifecycle.
- Rework resend/cooldown semantics so a legitimate user is not locked out by an attacker-created challenge.
- Exclude consumed challenges from active resend decisions.
- Return correct `Retry-After` metadata where applicable.

### P3.3 — Account enumeration — M-2

- Make unauthenticated initiation responses non-enumerating where product UX permits.
- Avoid distinct error messages that disclose account existence.
- Apply rate limits before identity lookup behavior can be abused at scale.

## Phase 4 — Input and secret hardening

### P4.1 — Identity normalization and validation — M-5

- Normalize mobile numbers to E.164 using a dedicated phone-number component.
- Apply Unicode normalization before identity comparison.
- Validate email syntax at the presentation boundary.
- Ensure cooldown and uniqueness use the canonical normalized value.

### P4.2 — Secret requirements — M-4

- Require a sufficiently strong HMAC secret at configuration startup.
- Use one explicit minimum secret-strength policy across JWT and secret hashing.
- Update tests and deployment documentation with secure secret-generation guidance.

### P4.3 — Trusted request metadata — M-6

- Remove authoritative IP address input from public request bodies.
- Resolve client IP through a trusted proxy-aware infrastructure component.
- Treat device information as untrusted metadata unless independently attested.

## Phase 5 — Detection, operations, and cleanup

### P5.1 — Security event logging — M-7

- Add structured events for OTP failures, attempt exhaustion, refresh reuse, session revocation, and suspicious rate-limit activity.
- Never log OTP codes, raw refresh tokens, or secrets.
- Define host-facing hooks for metrics and alerting.

### P5.2 — Data retention and indexes — M-9 / L-6

- Add retention policy for expired OTP challenges and obsolete sessions.
- Add indexes based on measured hot queries.
- Provide cleanup guidance or a host-scheduled cleanup use case.

### P5.3 — Error mapping and operational hardening — Low findings

- Stop converting unexpected authenticator failures into HTTP 401.
- Define explicit domain/authentication exceptions.
- Document HMAC key rotation strategy.
- Review dead fields and public API surface after security behavior is stable.

## Definition of Done

A security finding is closed only when:

1. the invariant is enforced in production code;
2. the behavior has regression tests;
3. concurrency-sensitive findings have PostgreSQL integration tests;
4. public/deployment responsibilities are documented;
5. no clean-architecture boundary is weakened to implement the fix.
