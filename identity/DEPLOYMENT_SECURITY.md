# Identity production security checklist

This document defines the host-application and infrastructure responsibilities that must be satisfied when deploying `hamresan-identity` in production. The package enforces authentication and session invariants, but it intentionally does not own Redis, nginx, schedulers, secret managers, SIEM providers, or the host application's Alembic revision graph.

Use this checklist together with `RATE_LIMITING.md`, `TRUSTED_REQUEST_METADATA.md`, `RETENTION_CLEANUP.md`, `INDEX_MIGRATION_NOTES.md`, `SECURITY_MIGRATION_NOTES.md`, and `HMAC_KEY_ROTATION.md`.

## 1. Distributed application rate limiting

`InMemoryRateLimiter` is process-local and is suitable only for tests, development, or a deliberately single-process deployment.

For any production topology with multiple workers, processes, containers, or hosts:

- inject one shared `RateLimiter` implementation through `IdentityModuleConfig.rate_limiter`;
- use an atomic shared backend such as Redis or an equivalent datastore;
- ensure all Identity instances use the same rate-limit namespace and backend for the same environment;
- preserve the package scopes for destination burst, destination daily, requester/IP burst, and challenge verification limits;
- do not silently fall back to per-process in-memory counters when the distributed backend is unavailable, because that would weaken abuse protection differently on each instance;
- monitor limiter errors and capacity so operational failures are visible.

Application-level rate limiting must remain enabled even when nginx, an API gateway, or a WAF performs edge throttling. Edge controls handle volumetric abuse; Identity limits enforce semantic destination/requester/challenge abuse controls.

## 2. nginx / trusted proxy boundary

`DirectRequestMetadataResolver` is the safe default because it uses the socket peer and ignores forwarding headers.

Use `TrustedProxyRequestMetadataResolver` only when the application is reachable exclusively through known trusted proxies and the exact trusted proxy hop count is known.

For a single nginx hop, the safer pattern is to overwrite client-supplied forwarding state rather than blindly preserve it:

```nginx
location / {
    proxy_pass http://identity_app;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Then configure:

```python
TrustedProxyRequestMetadataResolver(trusted_proxy_hops=1)
```

Deployment requirements:

- the application port must not be directly reachable from untrusted networks;
- nginx/upstream gateways must overwrite or correctly construct `X-Forwarded-For`;
- configure the exact proxy-hop count instead of guessing;
- do not trust forwarding headers merely because they are present;
- keep requester IP canonicalization enabled so equivalent IPv4/IPv6 representations share one rate-limit identity.

If the topology contains multiple trusted proxies, document the hop order and test it before enabling forwarded-header trust.

## 3. Edge throttling

Configure coarse request throttling at nginx, the API gateway, or the WAF for Identity endpoints, especially OTP request and OTP verification routes.

The edge limit should protect the application from volumetric floods. It must not replace Identity's application-level limits and should not be so permissive that a single source can saturate application workers before semantic limits are evaluated.

Exact edge thresholds are host-specific and should be tuned using observed traffic rather than hard-coded by this reusable package.

## 4. Security events, observability, and alerting

Identity exposes `SecurityEventSink`, but the default sink is intentionally a no-op. Production hosts should inject a real implementation through `IdentityModuleConfig.security_event_sink` and route events to structured logs, metrics, a SIEM, or another monitored security pipeline.

At minimum, production observability should cover:

- `otp.request_rate_limited`;
- `otp.verify_rate_limited`;
- `otp.attempt_failed`;
- `otp.attempts_exceeded`;
- `refresh.reuse_detected`;
- `session.revoked`;
- `session.revoked_all`.

Recommended alert candidates include:

- unusual spikes in failed OTP verification;
- repeated OTP attempt exhaustion;
- repeated requester/destination rate-limit rejection;
- refresh-token reuse detection;
- unexpected mass session revocation.

Alert thresholds are deployment-specific. Avoid paging on every individual failed OTP; aggregate and correlate events where appropriate.

## 5. Sensitive-data logging rules

Do not log or attach the following values to security events, application logs, exception context, traces, or metrics labels:

- OTP codes;
- raw access tokens;
- raw refresh tokens;
- HMAC/JWT signing secrets;
- secret-manager payloads;
- full normalized email addresses or mobile numbers when a non-reversible fingerprint is sufficient.

The package `SecurityEvent` contract intentionally carries identifiers and `subject_fingerprint` instead of raw credentials or raw destination PII. Host implementations of `SecurityEventSink` must preserve that boundary.

HTTP middleware and reverse-proxy access logging must also avoid request-body capture for OTP and session endpoints.

## 6. Retention cleanup scheduling

Identity does not own a scheduler. The host must schedule `identity_module.data_retention_cleaner.execute()`.

A daily execution is a reasonable baseline. Higher-volume deployments may need a shorter interval because each run is intentionally batch-limited.

Production operations should verify:

- the cleanup job is actually scheduled and monitored;
- failures are retried or surfaced operationally;
- configured OTP/session retention windows match security and compliance requirements;
- the cleanup batch size and cadence prevent unbounded table growth;
- active OTP challenges and active sessions remain excluded from cleanup.

## 7. Database migrations and indexes

Never rely on SQLAlchemy metadata creation to upgrade an existing production database.

The host application's migration graph must include all Identity schema changes required by the deployed package version, including:

- the refresh-family `family_expires_at` migration and conservative backfill described in `SECURITY_MIGRATION_NOTES.md`;
- the OTP lookup composite index described in `INDEX_MIGRATION_NOTES.md`;
- any later package-owned model changes visible through `identity.migrations.identity_metadata()`.

Before production rollout:

- generate/review the host Alembic migration;
- test upgrade on a production-like database;
- verify indexes exist after deployment;
- define rollback/incident procedures for migrations that cannot be trivially reversed;
- avoid destructive autogeneration against unrelated host tables by using the documented metadata/filter integration.

## 8. Secret quality and storage

Both Identity HMAC secrets and HS256 JWT secrets must be at least 32 bytes and generated from a cryptographically secure source.

Production requirements:

- load secrets from the host secret-management layer or protected runtime configuration;
- never commit secrets to the repository;
- do not embed secrets in container images;
- restrict secret access to the application identity that needs it;
- keep Identity HMAC and JWT signing keys separate where practical;
- do not expose secrets through logs, metrics, traces, debug endpoints, or exception reporting.

Secret identifiers may be logged when operationally useful; secret material must not be logged.

## 9. HMAC key rotation

Follow `HMAC_KEY_ROTATION.md` for normal and compromised-key procedures.

For normal rotation:

- deploy a new current key with a new key id;
- keep the previous key verification-only for the required overlap period;
- remove retired keys after all dependent credentials have expired.

For a compromised key:

- replace it immediately;
- do not preserve the compromised key merely for session continuity;
- revoke affected sessions;
- handle active OTP challenges according to incident-response policy;
- inspect relevant security events for activity during the exposure window.

The host should rehearse both normal rotation and compromised-key response before production incidents require them.

## 10. Production acceptance record

Before declaring Identity deployment-security review complete for a specific environment, record evidence for each item below in the host application or infrastructure repository:

- distributed limiter configured when more than one process/instance exists;
- nginx/API-gateway edge throttling enabled;
- trusted proxy topology and hop count reviewed;
- application cannot bypass the trusted proxy from untrusted networks;
- real `SecurityEventSink` configured;
- security alerts/metrics reviewed;
- sensitive-data logging policy checked at application and proxy layers;
- retention cleanup schedule enabled and monitored;
- Identity migrations and indexes applied;
- production secrets meet minimum requirements and come from secret management;
- normal HMAC rotation procedure tested;
- compromised-key response procedure reviewed.

This package repository can document and test the contracts, but final environment-specific confirmation belongs to the host deployment.