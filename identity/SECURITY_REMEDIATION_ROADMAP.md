# Identity Security Remediation Roadmap

This roadmap tracks remediation of the August 2026 security audit for the passwordless OTP authentication flow.

The roadmap distinguishes between:

- **finding closure**: vulnerable package behavior has been corrected and regression coverage exists;
- **validation work**: concurrency/full-suite validation required before closure;
- **deployment follow-up**: the package exposes or documents the required control, while the host deployment must configure or operate it;
- **accepted scope decisions**: an audit recommendation is intentionally not implemented exactly as suggested because the security invariant is satisfied by a narrower design decision.

## Principles

- Preserve clean architecture boundaries: application services must not depend on SQLAlchemy or HTTP details.
- Put concurrency guarantees at the persistence boundary behind repository contracts.
- Prefer default-deny security policies.
- Keep provider- and deployment-specific controls behind explicit abstractions.
- Add regression tests for every security invariant before considering a finding closed.
- Keep responsibilities explicit and testable; avoid hidden service helpers and unnecessary abstractions.

## Status legend

- **Closed**: production behavior and regression tests are implemented.
- **Accepted tradeoff**: documented behavior that is not currently treated as a security defect.
- **Deployment confirmation pending**: package-level control is complete, but production configuration still requires host verification.

## Original audit coverage summary

| Audit finding | Final package status | Remaining work |
| --- | --- | --- |
| C-1 Atomic OTP verification/consumption | **Closed** | None at package level |
| H-1 OTP cooldown abuse / login lockout | **Closed** | None at package level |
| H-2 Refresh rotation / reuse detection | **Closed** | None at package level |
| H-3 OTP purpose misuse | **Closed** | None at package level |
| M-1 User status enforcement | **Closed** | None at package level |
| M-2 Account enumeration | **Closed** | None at package level |
| M-3 Rate limiting | **Closed** | Production distributed/edge configuration confirmation |
| M-4 Secret requirements | **Closed** | Production secret configuration confirmation |
| M-5 Identity normalization/validation | **Closed** | None at package level |
| M-6 Trusted request metadata | **Closed** | Production trusted-proxy/nginx confirmation |
| M-7 Security event logging | **Closed** | Production sink/alerting confirmation |
| M-8 Session recovery / revoke-all | **Closed** | Session listing remains optional product functionality |
| M-9 Data retention/cleanup | **Closed** | Production cleanup scheduling confirmation |
| L-1 JWT expiry safety | **Closed** | None at package level |
| L-2 OTP notification consistency | **Closed** | None at package level |
| L-3 Access-token error isolation | **Closed** | None at package level |
| L-4 Dead/misleading model and public API members | **Closed** | None at package level |
| L-5 Authenticated-request DB lookup | **Accepted tradeoff** | Optional performance optimization only if measurements justify it |
| L-6 Hot-query indexes | **Closed** | Production migration/index rollout confirmation |
| L-7 HMAC key rotation | **Closed** | Production rotation configuration/procedure confirmation |

## Validation and remediation sequence

### R1 — PostgreSQL concurrency validation for C-1

Status: **Complete**

Completed:
- proved parallel valid verification of one challenge creates only one valid session;
- proved parallel invalid verification cannot lose failed-attempt increments;
- proved the configured attempt ceiling remains effective under concurrency;
- fixed PostgreSQL registration insert ordering at the persistence boundary;
- final R1 quality result: `86 passed`.

### R2 — PostgreSQL concurrency validation for H-2

Status: **Complete**

Completed:
- proved concurrent refresh of one token produces exactly one rotation;
- proved the competing refresh is detected as reuse;
- proved reuse revokes the active family;
- proved `family_expires_at` remains fixed across rotations;
- final R2 quality result: `88 passed`.

### R3 — M-3 rate-limit validation and bypass resistance

Status: **Complete**

Completed:
- validated trusted requester/IP rate limiting;
- added daily destination-limit coverage;
- added normalization-based bypass resistance;
- canonicalized equivalent IPv6 representations;
- rejected malformed trusted forwarded metadata;
- documented distributed limiter and edge-throttling responsibilities;
- final R3 quality result: `88 passed`.

### R4 — Deployment and operations security review

Status: **Complete (package/documentation scope)**

Completed:
- consolidated distributed rate limiting, trusted proxy, edge throttling, security-event wiring, sensitive logging, retention jobs, migration/index rollout, secret storage, and HMAC rotation requirements;
- added `DEPLOYMENT_SECURITY.md`;
- aligned stale rate-limiting documentation with implemented behavior;
- final R4 quality result: `95 passed`.

Deployment environment confirmation remains required.

### R5 — Finding-by-finding hostile regression review

Status: **Complete**

Completed:
- re-verified all 20 original findings against current production paths and regression coverage;
- confirmed no original Critical or High exploit is reproducible at package level;
- confirmed no original Medium or Low package-level exploit regressed;
- retained L-5 as the documented accepted tradeoff;
- added explicit direction-control-character regression coverage for M-5;
- corrected stale `Session.last_used_at` documentation;
- documented detailed evidence in `SECURITY_HOSTILE_REGRESSION_REVIEW.md`;
- final R5 quality result: `99 passed`.

### R6 — Fresh hostile security review

Status: **Complete**

The R6 review was not restricted to the original findings. It reviewed interactions between authentication, refresh rotation, session revocation, OTP rate limiting, request metadata, input validation, persistence locking, security events, and deployment-sensitive defaults.

New findings discovered and remediated:

#### R6-1 — Concurrent refresh vs revoke race

Severity: **High**

Status: **Closed**

- revoke now locks the refresh-token session through the existing repository locking contract;
- when an already-rotated token is revoked, the full family is invalidated;
- PostgreSQL concurrency coverage proves concurrent refresh and revoke leave no active session in the family.

#### R6-2 — Cooldown requests consuming destination send quota

Severity: **Medium**

Status: **Closed**

- requester/IP abuse control still applies to every OTP request;
- destination burst/daily quota is consumed only when a new OTP is actually created and sent;
- regression coverage proves cooldown reuse cannot exhaust destination send quota without new delivery.

#### R6-3 — OTP verify requester-rate-limit bypass with varying challenge IDs

Severity: **Medium**

Status: **Closed**

- per-challenge verification limiting remains in place;
- a separate trusted requester/IP verification burst limit now blocks bypass by changing challenge IDs;
- policy and service regression coverage protect the invariant.

#### R6-4 — Unbounded refresh/revoke token input

Severity: **Low**

Status: **Closed**

- refresh and revoke HTTP schemas now bound refresh-token length to a maximum of 256 characters;
- oversized values are rejected at the presentation boundary before HMAC/database processing;
- HTTP regression coverage verifies rejection.

Detailed R6 evidence is documented in `SECURITY_FINAL_HOSTILE_REVIEW.md`.

Final R6 quality result with PostgreSQL integration enabled: **`108 passed`**.

## Audit closure checklist

1. C-1 PostgreSQL concurrency validation — **Done**.
2. H-2 PostgreSQL concurrency validation — **Done**.
3. M-3 full-quality/bypass validation — **Done**.
4. Distributed/edge rate-limiting responsibilities documented — **Done at package level; production confirmation remains**.
5. Trusted-proxy requirements documented — **Done at package level; production confirmation remains**.
6. Security-event sensitive-data rules documented and package event payloads avoid OTP codes/raw tokens/signing secrets — **Done at package level; production sink/alerting confirmation remains**.
7. Retention scheduling responsibility documented — **Done at package level; production scheduler confirmation remains**.
8. Existing-database migration/index rollout responsibility documented — **Done at package level; deployed-database confirmation remains**.
9. Secret/HMAC rotation requirements documented and reviewed — **Done at package level; production configuration confirmation remains**.
10. All 20 original findings re-verified — **Done in R5**.
11. Fresh hostile review performed and all newly discovered package findings remediated — **Done in R6**.
12. Final full project quality suite passes with PostgreSQL integration enabled — **Done: `108 passed`**.

## Final package-level status

**Package-level security remediation is complete.**

No unresolved Critical or High package-level finding remains after R6. The original 20 findings have been re-verified, four additional R6 findings were discovered and remediated, and the final quality suite passes.

The audit is **not yet operationally closed for a specific production deployment** until the host confirms the deployment-dependent items below.

## Production deployment confirmation still required

Before declaring a deployed environment fully closed from an operational security perspective, confirm:

- shared/distributed rate limiting for multi-process or multi-instance deployments;
- nginx/API-gateway/WAF trusted-proxy and edge-throttling configuration;
- production `SecurityEventSink`, log/SIEM routing, and alerting;
- no OTP codes, raw access/refresh tokens, signing secrets, or unnecessary destination PII are added by host logging pipelines;
- retention cleanup scheduler and configured retention windows;
- required schema/index migrations are applied to the deployed database;
- production JWT/HMAC secret quality and secure storage;
- normal and compromised HMAC rotation procedures are tested operationally.

## Definition of Done

A security finding is closed only when:

1. the invariant is enforced in production code;
2. behavior has regression coverage;
3. concurrency-sensitive findings have PostgreSQL integration coverage;
4. public/deployment responsibilities are documented;
5. clean-architecture boundaries are not weakened to implement the fix.

The Identity package now satisfies this package-level Definition of Done.