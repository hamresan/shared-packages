# Production and Meta App Review

This is the production checklist for `hamresan-instagram-api`. Provider requirements can change
independently of this package, so release owners must verify current Meta documentation and the App
Dashboard before every production launch or API-version upgrade.

## Access model

Meta permissions can have Standard or Advanced Access depending on the app, permission, and use
case. Development/test access to app-role accounts is not evidence that third-party professional
accounts will work in production.

Before onboarding professional accounts that are not owned by app roles, the host must verify the
required app mode, access level, App Review approval, business verification or other prerequisites,
privacy/data-deletion requirements, and reviewer instructions in the current Meta dashboard.

Do not request a permission merely because the provider supports it.

## Permission-to-feature justification

| Permission | Implemented feature |
| --- | --- |
| `instagram_business_basic` | selected professional-account profile and owned media reads; prerequisite used by messaging/comment policies |
| `instagram_business_manage_messages` | conversation/message reads and eligible reply-oriented outbound messaging |
| `instagram_business_manage_comments` | comment reads, public replies, eligible private replies, and supported comment webhook workflows |

`instagram_business_manage_insights` and `instagram_business_content_publish` are not required by
the current package feature set and must not be requested for this package alone.

The host authorization layer remains responsible for requesting permissions. This package fails
closed when a selected connection does not contain permissions required by a use case.

## API-version compatibility policy

Meta API versions are a host-controlled production setting, not a hidden package default.

- Pin one explicit Graph API version in production configuration.
- Do not use an unversioned production Graph API base URL.
- Treat a provider-version change as a compatibility change requiring CI and sandbox verification.
- Review the provider changelog before upgrading.
- Re-run account, media, messaging, comments, webhook, and consumer acceptance tests.
- Verify response fields and webhook payloads used by package mappers.
- Keep the previous supported version until the new version passes the release gate.
- Do not claim support for a version that has not passed the package test matrix.

## Rate limits, retries, and backoff

Rate-limit behavior is provider-controlled and can vary by endpoint, app, account, and current Meta
policy. The package must not invent a fixed quota.

When Meta returns a retryable throttling or transient failure:

- honor a provider retry delay when one is supplied and safe to use;
- otherwise use bounded exponential backoff with jitter for idempotent reads;
- cap retries and surface persistent failure to the host;
- coordinate retries at the host/provider-client boundary to avoid retry storms;
- never automatically retry non-idempotent message/comment reply POSTs unless Meta documents a safe
  idempotency mechanism for that operation;
- preserve connection identity in rate-limit metrics so one account cannot silently fail over to
  another authorized account.

## Observability and masked structured logging

Useful structured fields include operation, provider API version, HTTP status, normalized error
category, safe provider error code, connection ID, provider account ID, retry count, latency, webhook
event ID, and dispatch outcome.

Never log access tokens, app secrets, authorization headers, OAuth codes, webhook signing secrets,
raw webhook bodies, or URLs containing credentials. Message/comment text should also be excluded
unless the host has an explicit privacy-safe logging policy.

Use package observer contracts for sanitized provider/webhook signals. Redaction belongs at the
logging/telemetry boundary and must fail closed for known secret fields.

## Cross-account isolation

Every account-scoped operation requires an explicit connection. Production authorization must
confirm that the host principal is allowed to use that connection before invoking this package.

The package must never select another connection because the requested connection is unavailable,
infer a global active account, reuse a token for another connection, or route webhook automation
through a connection other than the provider-account mapping resolved for that event.

## Release checklist

1. Verify current Meta access/App Review requirements.
2. Verify the permission-to-feature table still matches implementation.
3. Verify the configured provider API version is supported.
4. Run Ruff and format checks.
5. Run strict Pyright.
6. Run unit/integration tests with branch coverage >= 85%.
7. Run cross-account isolation tests.
8. Build the wheel and install it into a clean environment.
9. Run public-import smoke checks against the installed wheel.
10. Run the Stage 14 reference consumer acceptance scenario.
