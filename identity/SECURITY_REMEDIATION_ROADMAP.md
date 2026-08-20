# Identity Security Remediation Roadmap

This roadmap tracks remediation of the August 2026 security audit for the passwordless OTP authentication flow.

The roadmap distinguishes between:

- **finding closure**: the vulnerable production behavior has been corrected and regression coverage exists;
- **validation work**: real PostgreSQL concurrency or full-suite validation is still required;
- **deployment follow-up**: the package exposes or documents the required control, but the host deployment must configure or operate it;
- **accepted scope decisions**: an audit recommendation was intentionally not implemented exactly as suggested because the security invariant is satisfied by a narrower design decision.

## Principles

- Preserve clean architecture boundaries: application services must not depend on SQLAlchemy or HTTP details.
- Put concurrency guarantees at the persistence boundary behind repository contracts.
- Prefer default-deny security policies.
- Keep provider- and deployment-specific controls behind explicit abstractions.
- Add regression tests for every security invariant before considering a finding closed.
- Keep security findings in focused PRs so review and rollback remain straightforward.

## Status legend

- **Closed**: production behavior and regression tests are implemented.
- **Mostly closed**: the primary issue is fixed but validation or another focused follow-up remains.
- **In progress**: implementation is currently under review.
- **Planned**: finding remains open.
- **Accepted tradeoff**: documented behavior that is not currently treated as a security defect.

## Audit coverage summary

| Audit finding | Current status | Remaining work |
| --- | --- | --- |
| C-1 Atomic OTP verification/consumption | **Mostly closed** | PostgreSQL concurrency integration validation |
| H-1 OTP cooldown abuse / login lockout | **Closed** | Re-verify during final hostile audit |
| H-2 Refresh rotation / reuse detection | **Mostly closed** | PostgreSQL concurrent-refresh integration validation |
| H-3 OTP purpose misuse | **Closed** | Re-verify during final hostile audit |
| M-1 User status enforcement | **Closed** | Re-verify during final hostile audit |
| M-2 Account enumeration | **Closed** | Re-verify during final hostile audit |
| M-3 Rate limiting | **Mostly closed** | Full quality-suite validation plus deployment-level distributed/edge throttling review |
| M-4 Secret requirements | **Closed** | Deployment secret configuration review |
| M-5 Identity normalization/validation | **Closed** | Re-verify during final hostile audit |
| M-6 Trusted request metadata | **Closed** | Trusted-proxy/nginx deployment review |
| M-7 Security event logging | **Closed** | Host alerting/SIEM integration review and sensitive-data verification |
| M-8 Session recovery / revoke-all | **Closed** | Session listing remains an optional product/operations enhancement, not required for finding closure |
| M-9 Data retention/cleanup | **Closed** | Confirm host scheduling/retention job configuration |
| L-1 JWT expiry safety | **Closed** | Re-verify during final hostile audit |
| L-2 OTP notification consistency | **Closed** | Re-verify during final hostile audit |
| L-3 Access-token error isolation | **Closed** | Re-verify during final hostile audit |
| L-4 Dead/misleading model and public API members | **Closed** | Re-verify retained compatibility-field semantics |
| L-5 Authenticated-request DB lookup | **Accepted tradeoff** | Optional performance optimization only if measurements justify it |
| L-6 Hot-query indexes | **Closed** | Confirm existing-database migration/index rollout guidance |
| L-7 HMAC key rotation | **Closed** | Operational key-rotation configuration/procedure review |

## Phase 1 — Authentication correctness and account-takeover blockers

### P1.1 — Atomic OTP verification and consumption — C-1

Status: **Mostly closed**

Completed:
- OTP challenges are read under a row lock during verification.
- Failed-attempt counters are incremented atomically in persistence.
- Validation, attempt accounting, successful consumption, and session creation remain inside one transaction.
- Regression tests enforce the configured attempt ceiling.

Remaining:
- Add PostgreSQL concurrency integration coverage proving concurrent verification of the same OTP cannot create multiple sessions.
- Add PostgreSQL concurrency integration coverage proving failed-attempt accounting cannot be lost under parallel invalid verification.
- Re-run the original C-1 hostile scenario after the integration tests pass.

### P1.2 — Default-deny OTP purpose handling — H-3

Status: **Closed**

Remaining verification:
- Re-run invalid/unimplemented-purpose hostile cases during the final audit and confirm they cannot fall through to session issuance.

### P1.3 — User status enforcement — M-1

Status: **Closed**

Remaining verification:
- Re-test suspended/disabled users at OTP verification and authenticated-request boundaries during the final audit.

## Phase 2 — Session and refresh-token security

### P2.1 — Atomic refresh rotation and reuse detection — H-2

Status: **Mostly closed**

Completed:
- Refresh rotation locks the current session.
- Refresh-token reuse is detected and revokes the active family.
- Refresh families have a fixed absolute expiration.

Remaining:
- Add PostgreSQL concurrency integration coverage proving concurrent use of the same refresh token cannot create multiple valid rotated sessions.
- Validate refresh-token reuse detection and family revocation under real PostgreSQL concurrency.
- Re-run the original H-2 hostile scenarios after the integration tests pass.

### P2.2 — Session recovery controls — M-8

Status: **Closed**

Completed:
- Authenticated users can revoke all active sessions.
- The public API exposes a bulk-revocation use case for trusted host/operator recovery workflows.
- Bulk revocation is implemented as one persistence operation and emits a security event.

Audit recommendation reconciliation:
- The original audit roadmap suggested both bulk revocation and user session listing.
- Bulk revocation closes the security recovery gap.
- Session listing remains an optional product/operations enhancement and is not required to close M-8 unless later product requirements make it necessary.

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
- Confirm request, verify, and daily-destination limits cannot be bypassed through normalization or requester-metadata variations.
- Review the production distributed limiter expectation, including Redis or another shared backend when multiple workers/instances are used.
- Confirm coarse traffic throttling exists at nginx/API-gateway level and is not treated as a replacement for application-level security limits.
- Re-run the original SMS-pumping and high-rate brute-force amplification scenarios during the final hostile audit.

### P3.2 — OTP request cooldown behavior — H-1

Status: **Closed**

Remaining verification:
- Re-run the original victim-lockout/cooldown abuse scenario and confirm an unauthenticated requester cannot indefinitely block the legitimate user from obtaining a usable challenge.

### P3.3 — Account enumeration — M-2

Status: **Closed**

Remaining verification:
- Re-run registration/login enumeration cases and compare status codes, response bodies, and observable flow differences.
- Confirm rate limiting prevents scalable enumeration even where some product-level flow distinction is unavoidable.

## Phase 4 — Input, metadata, and secret hardening

### P4.1 — Identity normalization and validation — M-5

Status: **Closed**

Remaining verification:
- Re-test E.164 normalization, Unicode normalization, non-Latin digits, direction-control characters, and malformed email/mobile inputs.
- Confirm alternate textual representations cannot create duplicate identities or bypass cooldown/rate-limit buckets.

### P4.2 — Secret requirements — M-4

Status: **Closed**

Remaining deployment review:
- Confirm production HMAC/JWT secrets meet documented entropy and length requirements.
- Confirm secrets are provided through an appropriate secrets-management mechanism and are not committed or logged.

### P4.3 — Trusted request metadata — M-6

Status: **Closed**

Remaining deployment review:
- Confirm production nginx/API-gateway trusted-proxy behavior matches `RequestMetadataResolver` assumptions.
- Confirm forwarding headers are accepted only from explicitly trusted proxies.
- Confirm untrusted clients cannot directly control stored requester IP/device forensic metadata.

## Phase 5 — Detection, recovery, operations, and cleanup

### P5.1 — Security event logging — M-7

Status: **Closed**

Completed:
- A host-facing `SecurityEventSink` contract exists.
- Structured events cover OTP failures/exhaustion, rate-limit rejection, refresh reuse, and session revocation.
- Events avoid OTP codes, raw tokens, signing secrets, and raw destination PII.
- Hosts can route events to logging, metrics, or SIEM providers.

Remaining deployment/operations review:
- Confirm the host actually wires security events to logging, metrics, or SIEM in production.
- Confirm alerting exists for suspicious failed-verify rates, attempts exhaustion, repeated rate-limit rejection, and refresh-token reuse where operationally appropriate.
- Inspect all security event/log paths to confirm they contain no OTP codes, raw access/refresh tokens, secrets, or unnecessary destination PII.

### P5.2 — Data retention and cleanup — M-9

Status: **Closed**

Completed:
- OTP and session retention windows are configurable.
- Cleanup runs in bounded batches.
- The package exposes a host-invoked cleanup use case and does not own scheduling.
- Host scheduling guidance is documented.

Remaining deployment review:
- Confirm the host schedules cleanup jobs at an appropriate cadence.
- Confirm retention values match operational/security requirements.
- Confirm cleanup behavior is safe on production-sized datasets and does not leave unbounded historical growth.

### P5.3 — Hot-query indexes — L-6

Status: **Closed**

Completed:
- The OTP latest-active lookup has a composite index on `(normalized_destination, purpose, created_at)`.
- Metadata regression coverage verifies index shape and column order.
- Existing-database migration requirements are documented.

Remaining deployment review:
- Confirm existing installations apply the required index/schema migration rather than relying only on fresh metadata creation.
- Verify the production migration path is documented and reversible/operationally safe.

## Phase 6 — Low-severity hardening and API cleanup

### P6.1 — Access-token error isolation — L-3

Status: **Closed**

Completed:
- Invalid/unacceptable access-token credentials use public `AccessTokenAuthenticationError`.
- FastAPI maps only that typed authentication error to HTTP 401.
- Unexpected infrastructure/programming failures propagate instead of being masked as authentication failures.
- Regression coverage distinguishes invalid credentials from backend failures.

Remaining verification:
- Re-test backend/database failures during authenticated requests and confirm they are not misreported as invalid credentials.

### P6.2 — JWT codec expiry safety — L-1

Status: **Closed**

Completed:
- JWT codec verification enables PyJWT expiration validation instead of passing `verify_exp=False`.
- Direct codec consumers reject expired tokens without relying on the higher-level authenticator.
- The authenticator keeps its explicit expiration check as defense in depth and for fake/test verifiers.
- Regression coverage verifies expired JWTs are rejected by the codec itself.

Remaining verification:
- Re-test direct codec use with expired tokens during final hostile review.

### P6.3 — OTP notification consistency — L-2

Status: **Closed**

Completed:
- A newly created OTP challenge is not committed until notification dispatch has been accepted successfully.
- Notification dispatch failure exits the unit of work with an exception, so the pending challenge is rolled back and does not create a cooldown for an OTP the user never received.
- Regression coverage verifies that a failed first dispatch can be retried immediately and causes a second notification attempt rather than reusing an undelivered challenge.
- A future transactional outbox remains the preferred architecture if identity and notification persistence are later coordinated in one durable transaction.

Remaining verification:
- Re-test notification failure and immediate retry behavior during final hostile review.

### P6.4 — Dead or misleading model/public members — L-4

Status: **Closed**

Completed:
- Removed the unused `AuthenticatedPrincipal.permissions` member so the public principal no longer implies authorization behavior the package does not implement.
- Removed the extra `SqlAlchemyIdentityUnitOfWork.transaction()` helper because it was outside the unit-of-work contract and created a second transaction API with unclear semantics.
- Aligned package metadata with the implemented authentication/session scope rather than claiming authorization support.
- Retained persisted compatibility fields (`UserIdentity.value`, `OtpChallenge.destination_snapshot`, `User.updated_at`, and `Session.last_used_at`) without destructive schema changes and documented their current non-authoritative semantics.

Remaining verification:
- Confirm retained compatibility fields are not accidentally used as authoritative security state in current production paths.

### P6.5 — Authenticated-request database lookup — L-5

Status: **Accepted tradeoff / optional optimization**

- Database-backed session validation intentionally gives immediate revocation semantics.
- Consider an optional short-TTL `SessionReader` cache only when throughput measurements justify it.
- No remediation work is required for audit closure unless performance measurements change this decision.

### P6.6 — HMAC key rotation — L-7

Status: **Closed**

Completed:
- New OTP and refresh-token hashes are versioned with a key identifier and are written only with the current HMAC key.
- Verification accepts explicitly configured active previous keys during an overlap window.
- Legacy unversioned hashes remain verifiable during migration using the active key set.
- Refresh-token lookup is rotation-aware by querying all active versioned and legacy hash candidates, so pre-rotation sessions remain usable during the configured overlap period.
- Operational normal-rotation and compromised-key procedures are documented in `HMAC_KEY_ROTATION.md`.
- Regression coverage includes previous-key verification, legacy hashes, unknown/retired keys, and refresh-session continuity across a key rotation.
- HMAC digest calculation, hash formatting, key validation, and keyring responsibilities are separated into dedicated components; the hasher remains a focused orchestrator.

Remaining deployment/operations review:
- Review production key identifiers and active/previous key configuration.
- Validate the documented normal-rotation procedure.
- Validate the documented compromised-key procedure, including retirement behavior and expected session impact.
- Confirm key material never appears in logs or security events.

## Remaining remediation and final verification sequence

The original audit remediation table contained 13 priority groups. Production fixes for those groups are now implemented or intentionally resolved by an accepted scope decision. The following work remains before the August 2026 audit can be considered fully remediated.

### R1 — PostgreSQL concurrency validation for C-1

Priority: **Critical**

- Build focused PostgreSQL integration-test infrastructure without weakening production architecture.
- Prove parallel valid verification of one challenge creates at most one valid session.
- Prove parallel invalid verification cannot lose failed-attempt increments.
- Prove the configured attempt ceiling remains effective under concurrency.
- Run `make check` and close C-1 only after these tests pass.

### R2 — PostgreSQL concurrency validation for H-2

Priority: **High**

- Prove parallel refresh requests using the same refresh token cannot create multiple valid rotated sessions.
- Verify reuse detection and active-family revocation under real PostgreSQL concurrency.
- Verify family absolute expiration remains fixed across rotation.
- Run `make check` and close H-2 only after these tests pass.

### R3 — Close M-3 validation and deployment assumptions

Priority: **High**

- Run the full quality suite against the merged trusted requester/IP rate-limiting flow.
- Add or complete any missing regression/integration coverage discovered by that validation.
- Verify multi-worker/multi-instance deployments use a shared/distributed limiter such as Redis where required.
- Verify nginx/API-gateway coarse throttling and trusted-proxy configuration.
- Close M-3 after package validation passes; keep edge throttling as an explicit deployment responsibility.

### R4 — Deployment and operations security review

Priority: **Medium**

Review the security controls that cannot be proven by package unit tests alone:

- distributed rate limiting / Redis expectations;
- nginx/API-gateway trusted proxy and forwarding-header configuration;
- security-event routing and alerting;
- sensitive-data logging rules;
- retention cleanup scheduling;
- existing-database migrations and indexes;
- production secret quality and storage;
- HMAC normal rotation and compromised-key procedures.

Document any concrete host requirements that are still implicit.

### R5 — Finding-by-finding hostile regression review

Priority: **High**

Re-run every original audit finding against the updated `main` branch rather than assuming a finding remains closed because its implementation PR was merged:

- C-1;
- H-1 through H-3;
- M-1 through M-9;
- L-1 through L-7.

For every finding:

- reproduce the original attack preconditions where applicable;
- trace the current endpoint-to-persistence behavior;
- verify the intended security invariant;
- verify regression tests cover the invariant;
- record whether the original exploit is blocked, mitigated by an accepted design decision, or still reproducible.

### R6 — Final hostile security review

Priority: **High**

After the original 20 findings have been re-verified:

- perform a fresh hostile review of the current package without restricting the analysis to the old findings;
- inspect interactions between fixes, especially rate limiting, normalization, request metadata, refresh rotation, session revocation, and security events;
- look for new race conditions, authorization/authentication boundary mistakes, fail-open behavior, information disclosure, secret/PII leakage, and deployment footguns;
- run the full test/quality suite;
- update this roadmap with final closure state and any newly discovered findings.

## Audit closure checklist

The August 2026 security audit is not fully closed until all of the following are true:

1. C-1 PostgreSQL concurrency tests pass.
2. H-2 PostgreSQL concurrency tests pass.
3. M-3 full-quality validation passes.
4. Required distributed/edge rate limiting and trusted-proxy responsibilities are explicitly documented and reviewed.
5. Security events are wired for production observability/alerting where appropriate and contain no sensitive secrets/tokens/OTP values or unnecessary PII.
6. Retention cleanup scheduling is confirmed for the host deployment.
7. Existing-database migrations/index rollout is confirmed.
8. Production secret and HMAC key-rotation procedures are reviewed.
9. All 20 original findings are re-verified against current `main`.
10. A fresh hostile security review finds no unresolved Critical/High issue, or any new issue is added to this roadmap before declaring completion.
11. The full project quality suite passes.

## Definition of Done

A security finding is closed only when:

1. the invariant is enforced in production code;
2. the behavior has regression tests;
3. concurrency-sensitive findings have PostgreSQL integration tests before the audit is considered fully complete;
4. public/deployment responsibilities are documented;
5. no clean-architecture boundary is weakened to implement the fix.

The audit as a whole is closed only when the finding-level Definition of Done and the Audit closure checklist are both satisfied.
