# Identity final hostile security review

This document records R6 of the August 2026 Identity security-remediation program. Unlike R5, which re-verified the original 20 audit findings, R6 reviewed the current package without limiting the analysis to previously known issues.

## Scope

The review covered authentication and OTP flows, refresh rotation, session revocation, rate limiting, trusted request metadata, token input handling, security events, persistence/concurrency behavior, retention, and deployment-sensitive defaults.

The review specifically looked for:

- race conditions and transaction-ordering failures;
- fail-open authentication or authorization boundaries;
- bypasses created by interactions between previous remediations;
- abuse-control gaps and rate-limit key manipulation;
- unbounded or attacker-controlled expensive inputs;
- information, token, secret, or PII leakage;
- deployment footguns that could invalidate package-level guarantees.

## New findings discovered during R6

### R6-1 — Concurrent refresh vs session revoke race

Severity: **High**

Status: **Closed**

Before remediation, `RevokeSessionService` read the refresh-token session without acquiring the same row lock used by refresh rotation. A concurrent refresh could create a replacement session while revoke invalidated only the old session, leaving an active replacement behind.

Remediation:

- revoke now reads the refresh-token session through `get_for_update_by_refresh_token_hashes()`;
- when the presented token has already been replaced, revocation invalidates the full session family;
- the concurrency guarantee remains at the persistence boundary rather than leaking SQLAlchemy details into the service;
- PostgreSQL integration coverage proves concurrent refresh and revoke leave no active session in the family.

### R6-2 — OTP cooldown reuse could consume destination send quota

Severity: **Medium**

Status: **Closed**

Before remediation, destination burst/daily rate-limit buckets were consumed before the service checked whether an active challenge was still inside its resend cooldown. Repeated requests could therefore exhaust a victim destination's quota without causing a new OTP delivery, partially reintroducing the lockout pressure addressed by H-1.

Remediation:

- requester/IP abuse control is evaluated for every request;
- destination burst/daily send quota is consumed only when a new OTP challenge is actually about to be created and delivered;
- regression coverage proves repeated cooldown reuse returns the existing challenge without consuming additional destination send quota;
- normalization-based destination bucket sharing remains enforced for real OTP sends.

### R6-3 — OTP verify requester-rate-limit bypass using varying challenge IDs

Severity: **Medium**

Status: **Closed**

Before remediation, OTP verification rate limiting was keyed only by `challenge_id`. An attacker could repeatedly submit different UUIDs and continuously obtain fresh per-challenge buckets, allowing application-level verification traffic to bypass the intended requester abuse limit and unnecessarily exercise database/authentication paths.

Remediation:

- verification now has an additional requester/IP burst limit;
- the existing per-challenge verification limit remains in place;
- the requester key comes from trusted/canonicalized request metadata;
- policy and service regression coverage prove varying challenge IDs do not bypass the requester-level verification limit.

### R6-4 — Unbounded refresh/revoke token input

Severity: **Low**

Status: **Closed**

Refresh and revoke request schemas previously enforced only a minimum refresh-token length. Very large attacker-controlled strings could therefore enter hash-candidate/HMAC processing before rejection.

Remediation:

- refresh and revoke HTTP request schemas now enforce a maximum refresh-token length of 256 characters;
- the limit comfortably exceeds the package-generated token size while bounding attacker-controlled work;
- HTTP regression tests verify oversized tokens are rejected with validation errors before reaching application services.

## Review conclusion

No unresolved Critical or High package-level issue remains after remediation of the R6 findings.

The final full quality suite, including PostgreSQL integration coverage, passed with:

`108 passed`

The review did not identify a reason to weaken any clean-architecture boundary. Concurrency guarantees remain behind repository contracts, rate-limit semantics remain in policy components, presentation validation remains at the HTTP boundary, and application services remain focused workflow orchestrators.

## Deployment-dependent security responsibilities

Package-level closure does not prove the production environment is configured securely. Operational closure still requires the host deployment to confirm:

- a shared/distributed rate limiter is used for multi-process or multi-instance deployments;
- nginx/API-gateway/WAF trusted-proxy and edge-throttling configuration matches the documented assumptions;
- a production `SecurityEventSink` is wired to appropriate logging/metrics/SIEM and alerting;
- logging pipelines do not add OTP codes, raw access/refresh tokens, signing secrets, or unnecessary destination PII;
- retention cleanup is scheduled;
- required schema/index migrations are applied to the deployed database;
- production JWT/HMAC secrets satisfy documented requirements and are stored securely;
- HMAC rotation and compromised-key procedures are operationally tested.

## Final package-level verdict

**Package-level security remediation is complete.**

The original 20 audit findings have been re-verified, the fresh R6 hostile review found four additional issues which are now remediated with regression/integration coverage, and the final quality suite passes. Production deployment verification remains a separate operational responsibility.