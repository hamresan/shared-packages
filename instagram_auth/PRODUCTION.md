# Production readiness

This document covers the production responsibilities that remain with a host application using `hamresan-instagram-auth`.

## Meta App Review and access level

Meta controls App Review, permission access levels, and eligibility for Instagram Professional accounts. Before serving Instagram accounts that are not owned by the Meta app's own test/development users, the host must verify the current requirements in the Meta developer dashboard and the current Instagram API with Instagram Login documentation.

For each permission requested by the host:

- confirm that the permission is supported by Instagram Login for the targeted Business or Creator account;
- request only permissions needed by an enabled host feature;
- complete any App Review or Advanced Access process required by Meta before serving third-party professional accounts;
- keep review evidence aligned with the exact user flow and feature that requires the permission;
- re-check Meta requirements before production rollout because access-level and review requirements are provider-controlled and may change.

The package does not assume that Standard Access is sufficient for third-party production use. The host is responsible for confirming the current access level for every requested permission.

Core package permissions are:

- `instagram_business_basic`;
- `instagram_business_manage_messages`;
- `instagram_business_manage_comments`.

Optional permissions such as insights or content publishing must remain disabled unless the consuming feature requires them.

## Secure production configuration checklist

Before deployment, verify all of the following:

- Meta app ID/client ID and app secret come from the host secret-management system and are never committed to source control.
- OAuth redirect URIs are explicit, HTTPS in production, and exactly match the configured Meta application values.
- OAuth state storage is short-lived, one-time-use, and shared across application instances when the host is horizontally scaled.
- Raw authorization codes and raw access tokens are never logged.
- Persisted access tokens use a host-provided production-grade `InstagramAccessTokenProtector`; plaintext/no-op protection must never be used in production.
- Encryption/protection keys support secure rotation outside domain/application code.
- HTTP clients use bounded connect/read/write/pool timeouts chosen by the host.
- Authorization-code exchange is not retried automatically.
- Retries remain limited to semantically safe provider reads and bounded attempts.
- Provider failures are exposed through normalized `InstagramProviderError` values rather than raw provider payloads.
- Ownership is resolved from authenticated host context and checked for every connection-scoped management operation.
- Every downstream API operation identifies a concrete `InstagramConnectionId`; there is no global active connection inside this package.
- Expired, revoked, disconnected, reauthorization-required, or insufficient-permission connections fail closed.
- Security events and provider failures are observable without including secrets in logs, traces, metrics, or event payloads.
- Database backups, retention, and deletion policies include protected Instagram credentials and connection records.
- Alembic/revision history remains owned by the host deployment.
- Package health/maintenance use cases are scheduled by the host only when required by the provider integration.
- Ruff, formatting, strict Pyright, tests, branch coverage, and wheel smoke checks pass in CI before release.

## Observability

Record normalized, non-secret fields such as connection ID, operation name, provider error kind, HTTP status code when safe, retry attempt count, and security-event kind. Do not record authorization codes, raw access tokens, protected credential contents, app secrets, or full provider request/response bodies.

A host may attach logging, tracing, metrics, or alerting at its composition boundary. The package deliberately does not require a specific observability vendor.

## Release verification

From `instagram_auth/` run:

```bash
python -m pip install -e ".[test]"
make check
```

The test suite includes a wheel smoke test so the built distribution is checked in addition to source-tree imports.
