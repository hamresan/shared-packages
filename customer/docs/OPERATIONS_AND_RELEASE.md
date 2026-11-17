# Operations, compatibility and release checklist

This document describes host responsibilities for the reusable Customer package.
It is not a deployment guide for any specific consuming product.

## Operational security

1. Create customer tables using reviewed host-owned Alembic revisions; apply
   `install_customer_rls` after table creation. Never auto-migrate at application
   startup. A separate privileged migration role owns schema objects.
2. Run Customer application queries using a non-owner PostgreSQL role without
   `BYPASSRLS`. Scope each UoW with a verified business ID using the package's
   transaction-local tenant setting. Monitor connection reuse and isolation.
3. Map application permissions explicitly. A service actor granted exact
   identity lookup must **not** implicitly receive profile mutation, notes,
   identity management or erasure permissions.
4. Keep provider tokens, OTPs, untrusted identity claims and request bodies out
   of logs. Redact customer names, contacts, addresses and note content from
   exception reporting and tracing. Never log audit payloads as a PII backup.
5. Record aggregate-safe operational metrics: request counts, failures by
   stable error category, latency, idempotent replays, version conflicts and
   retention jobs. Avoid customer IDs and external identities as metric labels.

## Queries, indexes and concurrency

- Customer search accepts an offset of at least zero and a page size of 1–100.
  For large datasets, hosts must limit repeated deep offsets and plan a future
  cursor-based API separately rather than bypassing authorization.
- Tenant and parent foreign-key indexes are package-owned; partial unique
  indexes protect active external mappings, primary contacts and default
  addresses under concurrent writes. Review actual production query plans
  before adding speculative indexes.
- A stable business-scoped idempotency key and request fingerprint cover guest
  creation retries. Host retention must be long enough for realistic transport
  retries; after expiry, the same key may create a new customer.
- Only a successful customer transaction writes its mandatory audit event.
  Treat transient concurrency conflicts as expected; do not blindly retry
  conflicting writes with modified payloads.

## Retention, backup and restore

- The host injects `CustomerErasurePolicy` and authorizes terminal deletion only
  after its applicable retention/hold checks. Customer erasure does not rewrite
  independently owned booking, commerce or messaging histories.
- Schedule expiration of idempotency receipts and retention/archival of audit
  data using host infrastructure. Customer does not start background workers.
- Backups can contain erased PII until backup retention expires. Document legal
  retention and restore procedures; after restoring a backup, replay authorized
  erasure obligations before exposing restored data to users.
- Record migration rollback plans before deployment. A downgrade that drops
  customer tables or RLS is destructive; prefer forward-fix revisions and
  tested backups. Never run automatic destructive rollback in the package.

## Versioning and compatibility

- Distribution is `hamresan-customer`; Python import is `customer`.
- SemVer applies to documented public imports, command/query/result fields,
  error classes, behavior and optional integration entry points. Removing or
  reinterpreting a public contract requires a major version; backward-compatible
  additions use minor versions; fixes use patch versions.
- While `0.x` prereleases are used, compatibility may evolve before `1.0`;
  prerelease notes must identify any migration or code adjustment.
- Database migrations and RLS policy evolution require explicit host review
  even when the Python version change is nominally backward-compatible.
- Provider-specific or consuming-application API contracts are not part of
  Customer's public stability promise.

## Release gate

Before publishing a version, require:

- passing Ruff, strict Pyright, mirrored unit tests and real PostgreSQL CI;
- successful clean wheel/sdist installation, including optional extras;
- reviewed RLS/audit/erasure threat model and retention/backup procedures;
- reviewed license and package publishing policy;
- explicit user approval for version tagging and publication.

**Current publishing blockers:** a repository/package license has not been
selected and no package-index publication was authorized. Neither the package
build nor a green CI run constitutes approval to publish.
