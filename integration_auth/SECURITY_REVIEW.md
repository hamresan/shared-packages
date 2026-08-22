# Security review and release checklist

This document records the Stage 12 security-hardening review for `hamresan-integration-auth`.

## Security invariants

Before release, verify all of the following:

- canonical query encoding is deterministic, preserves duplicates, encodes spaces as `%20`, preserves literal `+` as `%2B`, and UTF-8 percent-encodes non-ASCII input;
- canonical request serialization has no trailing newline and signs method, path/query, timestamp, nonce, and body hash;
- HMAC verification uses constant-time comparison;
- invalid timestamps fail before nonce consumption;
- nonce consumption is atomic for a `(client_id, nonce)` pair under concurrency;
- credential rotation is atomic and direction-specific;
- revoked/expired credentials cannot authenticate;
- raw secrets, protected secret material, and request signatures are excluded from object representations and must not be logged;
- permissions and resource scopes are exact-match and do not imply wildcard/inherited privileges;
- authentication failures map to generic 401 responses and authorization failures map to generic 403 responses;
- persistence retains the authentication-path indexes and uniqueness constraint used for replay protection;
- Identity remains a host-composition concern; `integration_auth` has no direct dependency on `hamresan-identity`.

## Release gates

Run:

```bash
make release-check
```

The release check must pass:

1. Ruff lint.
2. Ruff format check.
3. Pyright strict.
4. pytest with branch coverage >= 85%.
5. package sdist/wheel build.
6. clean-virtual-environment installation of the built wheel without dependency resolution.
7. public-package import smoke check from the installed wheel.

Also run the repository host examples when changing public composition boundaries:

```bash
cd ../examples
make check
```

## Deployment checklist

The consuming host must provide:

- secret protection/unprotection backed by its own key-management policy;
- host-owned async SQLAlchemy Engine/SessionMaker;
- host-owned Alembic revision graph;
- configured clock-skew and replay-window values appropriate to the integration environment;
- TLS at the transport boundary;
- log redaction rules that do not record signed-request headers, raw credentials, protected secret material, or canonical secret material;
- operational procedures for credential rotation and immediate revocation.

## Explicit non-goals

Stage 12 does not add new authentication protocols or storage providers. Ed25519, Redis replay stores, key identifiers, audit hooks, and caching remain demand-driven future work.
