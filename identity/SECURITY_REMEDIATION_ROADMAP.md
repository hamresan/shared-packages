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
| C-1 Atomic OTP verification/consumption | **Closed** | Re-verify during final hostile audit |
| H-1 OTP cooldown abuse / login lockout | **Closed** | Re-verify during final hostile audit |
| H-2 Refresh rotation / reuse detection | **Closed** | Re-verify during final hostile audit |
| H-3 OTP purpose misuse | **Closed** | Re-verify during final hostile audit |
| M-1 User status enforcement | **Closed** | Re-verify during final hostile audit |
| M-2 Account enumeration | **Closed** | Re-verify during final hostile audit |
| M-3 Rate limiting | **Closed** | Re-verify during final hostile audit; deployment-specific controls remain host responsibilities |
| M-4 Secret requirements | **Closed** | Confirm production secret configuration in the host deployment |
| M-5 Identity normalization/validation | **Closed** | Re-verify during final hostile audit |
| M-6 Trusted request metadata | **Closed** | Confirm production trusted-proxy/nginx configuration |
| M-7 Security event logging | **Closed** | Confirm production sink/alerting wiring and sensitive-data policy |
| M-8 Session recovery / revoke-all | **Closed** | Session listing remains an optional product/operations enhancement |
| M-9 Data retention/cleanup | **Closed** | Confirm host cleanup scheduling |
| L-1 JWT expiry safety | **Closed** | Re-verify during final hostile audit |
| L-2 OTP notification consistency | **Closed** | Re-verify during final hostile audit |
| L-3 Access-token error isolation | **Closed** | Re-verify during final hostile audit |
| L-4 Dead/misleading model and public API members | **Closed** | Re-verify retained compatibility-field semantics |
| L-5 Authenticated-request DB lookup | **Accepted tradeoff** | Optional performance optimization only if measurements justify it |
| L-6 Hot-query indexes | **Closed** | Confirm existing-database migration/index rollout |
| L-7 HMAC key rotation | **Closed** | Confirm production rotation configuration/procedure |

## Phase 1 — Authentication correctness and account-takeover blockers

### P1.1 — Atomic OTP verification and consumption — C-1

Status: **Closed**

Completed:
- OTP challenges are read under a row lock during verification.
- Failed-attempt counters are incremented atomically in persistence.
- Validation, attempt accounting, successful consumption, and session creation remain inside one transaction.
- Regression tests enforce the configured attempt ceiling.
- PostgreSQL concurrency integration coverage proves concurrent valid verification of one challenge creates only one session.
- PostgreSQL concurrency integration coverage proves parallel invalid verification preserves all failed-attempt increments and the configured attempt ceiling.
- PostgreSQL validation exposed an insert-ordering issue on registration; `SqlAlchemyUserRepository.add()` now flushes the inserted user at the persistence boundary before dependent identity/session writes, without leaking SQLAlchemy concerns into the application service.
- The full quality suite passes with PostgreSQL integration tests enabled (`86 passed`).

Remaining verification:
- Re-run the original C-1 hostile scenario during the final finding-by-finding audit review.

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

Status: **Closed**

Completed:
- Refresh rotation locks the current session.
- Refresh-token reuse is detected and revokes the active family.
- Refresh families have a fixed absolute expiration.
- PostgreSQL concurrency integration coverage proves concurrent use of the same refresh token produces exactly one successful rotation.
- The competing refresh is detected as reuse and revokes the active session family.
- PostgreSQL state inspection confirms no active session remains in the family after reuse detection.
- PostgreSQL integration coverage confirms `family_expires_at` remains unchanged across subsequent rotations.
- The full quality suite passes with all PostgreSQL integration tests enabled (`88 passed`).

Remaining verification:
- Re-run the original H-2 hostile scenarios during the final finding-by-finding audit review.

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

Status: **Closed**

Completed:
- Application-level `RateLimiter` abstraction exists.
- OTP request limits apply by canonical destination.
- OTP verification limits apply by challenge.
- Daily destination limits are supported.
- In-memory baseline implementation exists and distributed implementations can be injected.
- OTP request limits also apply by trusted requester/IP across different destinations.
- FastAPI resolves requester IP server-side through `RequestMetadataResolver`; the default resolver ignores forwarding headers.
- Requester IP values are validated and canonicalized before use as rate-limit keys, including equivalent IPv6 textual forms.
- Malformed forwarded addresses are not accepted as requester identities.
- Regression coverage verifies canonical destination limits, daily limits, requester limits across destinations, requester IP canonicalization, and malformed forwarded metadata handling.
- Trusted proxy deployment requirements and distributed/edge throttling guidance are documented in `RATE_LIMITING.md` and `DEPLOYMENT_SECURITY.md`.
- The full quality suite passes after M-3 validation with PostgreSQL integration enabled (`88 passed` during R3; `95 passed` after R4 documentation review).

Remaining verification:
- Re-run the original SMS-pumping and high-rate brute-force amplification scenarios during the final hostile audit.
- Confirm the host deployment uses a distributed limiter for multi-process/multi-instance operation and edge throttling where required.

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

Deployment responsibility:
- Confirm production HMAC/JWT secrets meet documented entropy and length requirements.
- Confirm secrets are provided through an appropriate secrets-management mechanism and are not committed or logged.

### P4.3 — Trusted request metadata — M-6

Status: **Closed**

Deployment responsibility:
- Confirm production nginx/API-gateway trusted-proxy behavior matches `RequestMetadataResolver` assumptions.
- Confirm forwarding headers are accepted only from explicitly trusted proxies.
- Confirm untrusted clients cannot directly reach the application around the trusted proxy path.

## Phase 5 — Detection, recovery, operations, and cleanup

### P5.1 — Security event logging — M-7

Status: **Closed**

Completed:
- A host-facing `SecurityEventSink` contract exists.
- Structured events cover OTP failures/exhaustion, rate-limit rejection, refresh reuse, and session revocation.
- Events avoid OTP codes, raw tokens, signing secrets, and raw destination PII.
- Hosts can route events to logging, metrics, or SIEM providers.
- `DEPLOYMENT_SECURITY.md` explicitly documents that the default no-op sink is not sufficient for production observability and that hosts must wire a real sink where audit/alerting is required.

Deployment responsibility:
- Confirm the host actually wires security events to logging, metrics, or SIEM in production.
- Confirm alerting exists for suspicious failed-verify rates, attempts exhaustion, repeated rate-limit rejection, and refresh-token reuse where operationally appropriate.
- Confirm host logging pipelines do not add OTP codes, raw access/refresh tokens, secrets, or unnecessary destination PII.

### P5.2 — Data retention and cleanup — M-9

Status: **Closed**

Completed:
- OTP and session retention windows are configurable.
- Cleanup runs in bounded batches.
- The package exposes a host-invoked cleanup use case and does not own scheduling.
- Host scheduling guidance is documented in `RETENTION_CLEANUP.md` and consolidated in `DEPLOYMENT_SECURITY.md`.

Deployment responsibility:
- Confirm the host schedules cleanup jobs at an appropriate cadence.
- Confirm retention values match operational/security requirements.

### P5.3 — Hot-query indexes — L-6

Status: **Closed**

Completed:
- The OTP latest-active lookup has a composite index on `(normalized_destination, purpose, created_at)`.
- Metadata regression coverage verifies index shape and column order.
- Existing-database migration requirements are documented in `INDEX_MIGRATION_NOTES.md`, `SECURITY_MIGRATION_NOTES.md`, and the consolidated deployment checklist.

Deployment responsibility:
- Confirm existing installations apply the required index/schema migrations rather than relying only on fresh metadata creation.
- Verify the production migration path is reviewed through the host application's migration process.

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

Deployment responsibility:
- Review production key identifiers and active/previous key configuration.
- Validate the documented normal-rotation procedure.
- Validate the documented compromised-key procedure, including retirement behavior and expected session impact.
- Confirm key material never appears in logs or security events.

## Remaining remediation and final verification sequence

The original audit remediation table contained 13 priority groups. Production fixes for those groups are implemented or intentionally resolved by an accepted scope decision. Package-level validation and deployment documentation are now complete through R4. Environment-specific production verification remains a host deployment responsibility and must be confirmed before declaring the audit operationally closed.

### R1 — PostgreSQL concurrency validation for C-1

Status: **Complete**

Priority: **Critical**

Completed:
- Added focused PostgreSQL integration-test infrastructure without weakening production architecture.
- Proved parallel valid verification of one challenge creates only one valid session.
- Proved parallel invalid verification cannot lose failed-attempt increments.
- Proved the configured attempt ceiling remains effective under concurrency.
- Fixed the PostgreSQL registration insert-ordering issue at the persistence boundary and added mirrored repository coverage.
- Ran the full quality suite with PostgreSQL integration enabled: `86 passed`.

### R2 — PostgreSQL concurrency validation for H-2

Status: **Complete**

Priority: **High**

Completed:
- Proved parallel refresh requests using the same refresh token produce exactly one successful rotated session.
- Verified the competing request is treated as refresh-token reuse under real PostgreSQL row locking.
- Verified reuse detection revokes the active family and leaves no active session in that family.
- Verified the family's absolute expiration remains fixed across multiple rotations.
- Ran the full quality suite with all PostgreSQL integration tests enabled: `88 passed`.

### R3 — Close M-3 validation and deployment assumptions

Status: **Complete**

Priority: **High**

Completed:
- Validated trusted requester/IP rate limiting against the full quality suite.
- Added regression coverage for daily destination limits and normalization-based bypass resistance.
- Added requester IP validation/canonicalization so equivalent IPv6 forms share one requester bucket.
- Added coverage for malformed trusted forwarded metadata.
- Documented that multi-worker/multi-instance deployments require a shared/distributed limiter such as Redis.
- Documented that nginx/API-gateway/WAF throttling is an additional deployment layer, not a replacement for application-level limits.
- Full quality suite passed with PostgreSQL integration enabled: `88 passed`.

### R4 — Deployment and operations security review

Status: **Complete (package/documentation scope)**

Priority: **Medium**

Completed:
- Reviewed distributed rate limiting and documented shared-backend requirements.
- Reviewed trusted proxy assumptions and consolidated nginx/API-gateway forwarding-header requirements.
- Reviewed security-event behavior and documented that production hosts must replace the default no-op sink when observability/alerting is required.
- Consolidated sensitive-data logging requirements.
- Reviewed retention cleanup scheduling responsibilities.
- Reviewed existing-database migration/index rollout requirements.
- Reviewed secret quality/storage requirements.
- Reviewed normal and compromised HMAC rotation procedures.
- Added `DEPLOYMENT_SECURITY.md` as the consolidated production security checklist.
- Updated stale `SECURITY_RATE_LIMITING.md` guidance to reflect the implemented trusted requester/IP rate limiting.
- Full quality suite passed after the documentation review: `95 passed`.

Environment-specific checks still required before production audit closure:
- confirm the deployed limiter is distributed when multiple processes/instances are used;
- confirm nginx/API-gateway/WAF trusted-proxy and edge-throttling configuration;
- confirm production `SecurityEventSink`, SIEM/log routing, and alerting;
- confirm retention cleanup scheduler;
- confirm migrations/indexes are applied to the deployed database;
- confirm production secrets and HMAC rotation configuration.

### R5 — Finding-by-finding hostile regression review

Status: **Next**

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

Status: **Pending R5**

Priority: **High**

After the original 20 findings have been re-verified:

- perform a fresh hostile review of the current package without restricting the analysis to the old findings;
- inspect interactions between fixes, especially rate limiting, normalization, request metadata, refresh rotation, session revocation, and security events;
- look for new race conditions, authorization/authentication boundary mistakes, fail-open behavior, information disclosure, secret/PII leakage, and deployment footguns;
- run the full test/quality suite;
- update this roadmap with final closure state and any newly discovered findings.

## Audit closure checklist

The August 2026 security audit is not fully closed until all of the following are true:

1. C-1 PostgreSQL concurrency tests pass. **Done.**
2. H-2 PostgreSQL concurrency tests pass. **Done.**
3. M-3 full-quality validation passes. **Done.**
4. Distributed/edge rate limiting and trusted-proxy responsibilities are explicitly documented and reviewed. **Done at package/documentation level; production configuration confirmation remains.**
5. Security-event sensitive-data requirements are documented and package event payloads contain no OTP codes, raw tokens, or signing secrets. **Done at package level; production sink/alerting confirmation remains.**
6. Retention cleanup scheduling responsibility is documented. **Done at package level; production scheduler confirmation remains.**
7. Existing-database migration/index rollout responsibility is documented. **Done at package level; deployed-database confirmation remains.**
8. Secret and HMAC key-rotation procedures are documented and reviewed. **Done at package level; production configuration confirmation remains.**
9. All 20 original findings are re-verified against current `main`.
10. A fresh hostile security review finds no unresolved Critical/High issue, or any new issue is added to this roadmap before declaring completion.
11. The full project quality suite passes. **Latest validated result: 95 passed.**

## Definition of Done

A security finding is closed only when:

1. the invariant is enforced in production code;
2. the behavior has regression tests;
3. concurrency-sensitive findings have PostgreSQL integration tests before the audit is considered fully complete;
4. public/deployment responsibilities are documented;
5. no clean-architecture boundary is weakened to implement the fix.

The audit as a whole is closed only when the finding-level Definition of Done and the Audit closure checklist are both satisfied.
