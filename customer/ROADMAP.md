# hamresan-customer — staged implementation roadmap

> **Status: Stages 0–4 complete and merged. Stage 5 implemented and verified by PostgreSQL-backed CI; PR #164 awaits review/merge.** Each stage has a review gate; do not advance before its code, tests and dependency boundaries pass. Favor lean, responsibility-based design over speculative frameworks.

## Stage overview

| Stage | Focus | Demonstrable outcome |
| --- | --- | --- |
| **0** | Contract and security design freeze | Reviewed schemas, ownership rules, API version, audit/RLS approach |
| **1** | Installable Python foundation | Clean wheel/sdist, strict quality tooling, public API skeleton |
| **2** | Customer core and lifecycle | Scoped create/read/update/search, versions, archive/reactivate |
| **3** | Contacts, addresses, preferences and notes | Independently authorized, validated child entities |
| **4** | Trusted identity and external-identity linking | Verified linking, lookup, explicit get-or-create, revoke/relink |
| **5** | Async PostgreSQL persistence and migrations | Schema constraints, tenant-safe repositories, RLS |
| **6** | Transactional audit and erasure | Audit-coupled mutations, terminal privacy erasure |
| **7** | Optional HTTP adapter and host composition | Real, authenticated, tenant-scoped integration example |
| **8** | PostgreSQL security/concurrency acceptance | Verified isolation, races, failure recovery and migrations |
| **9** | Packaging, documentation and release hardening | Clean install, compatibility, stable public contracts |

The stages describe delivery order, not forced one-file-per-concept scaffolding. Where end-to-end verification depends on persistence (for example atomic uniqueness, RLS or transactional audit), earlier stages use fakes and Stage 5 onward provide the real guarantees. Never claim a security invariant is proven solely by an in-memory test.

## Stage 0 — Freeze contracts and threat model

**Progress:** Approved. Design reference artifacts:

- [Architecture and ownership matrix](docs/ARCHITECTURE.md)
- [Public API and contract draft](docs/PUBLIC_CONTRACTS.md)
- [Security threat model and acceptance inventory](docs/SECURITY_AND_ACCEPTANCE.md)

### Work

1. Confirm a Customer is **business-owned** (one business has many customers), branch-independent, and unrelated to any specific workflow. Guest customers are first-class.
2. Document the boundary of internal identity links versus provider-scoped external identities; authentication, OTP, messaging and provider verification stay outside Customer.
3. Define tenant ownership for every entity, deletion/retention rules, candidate duplicate semantics, active-link uniqueness, and minimum fields. Use composite foreign keys for tenant-consistent child relationships.
4. Define `CustomerActor` (`USER`/`SERVICE`), action permissions, minimum read projections, secure not-found behavior, and host-injected authorization and identity-verification contracts.
5. Specify stable DTOs, typed error categories, capability-oriented facade, expected-version updates and explicit lookup versus get-or-create. Include a minimal `CustomerResolution` (ID, business scope, link status, verification method/time and optionally authorized name), without downstream operation-authorization claims.
6. Design transaction-local PostgreSQL RLS context and deploy-role requirements, including fail-closed behavior. Define an audit repository sharing the mutation transaction; choose a third-party audit implementation **only after** proving current-session compatibility.
7. Define error and concurrency outcomes for idempotent identity linking, duplicate external-identity races, and erased-customer references. Define **optional create-customer idempotency** independently of external identities: host-supplied keys scoped by business/operation, canonical request fingerprint, same-key/same-payload replay, mismatched-payload conflict, atomic persistence and bounded retention.
8. Specify verification provenance and freshness semantics: the host/operation owner judges freshness for each action; Customer never treats `ACTIVE` or old verification alone as universal authorization, and never runs a verification challenge.
9. Review security and data-minimization requirements. Do not store raw provider tokens, OTP codes, sensitive values in audit records, idempotency fingerprints or LLM-specific types in the core.

### Gate

- [x] Entity/relationship and ownership matrix signed off, including constraints and retention decisions.
- [x] Public API v1 draft, typed error map and permission matrix reviewed.
- [x] Resolution projection, freshness policy boundary and create-idempotency contract reviewed.
- [x] RLS, audit atomicity, verification provenance and migration approach documented with test cases.
- [x] No unowned cross-package dependency or unnecessary abstraction.

## Stage 1 — Installable package foundation

**Progress:** Complete; Python 3.12, Ruff, format, strict Pyright, six foundation pytest tests, wheel/sdist build and clean core-only install verified locally. PR #160 merged; GitHub Actions run #44124900711 succeeded. Stage 2 adds domain use cases; persistence remains future work.

### Work

1. Add `pyproject.toml` with Python 3.12+, Hatchling, `src/customer`, `py.typed`, intentional optional extras (`sqlalchemy`, `postgres`, `fastapi`, `migrations`, `test`) and package metadata.
2. Establish controlled public package exports, a typed facade/configuration entry point, dependency injection and explicit contract locations; no accidental broad barrel exports.
3. Add Ruff, strict Pyright, pytest/pytest-asyncio, build checks and a reproducible development lockfile/Makefile consistent with the repository.
4. Mirror production module structure in `tests/`; place fakes, factories and builders in narrowly named support files.
5. Add CI jobs for package quality and clean wheel/sdist installation. Keep domain and application free of SQLAlchemy, FastAPI and external package imports.

### Gate

- [x] Wheel/sdist build; wheel installs and imports in a fresh local environment.
- [x] Ruff, format, strict Pyright, unit test and build **GitHub CI** jobs pass.
- [x] Optional dependencies are not loaded by core-only import.

## Stage 2 — Customer aggregate, lifecycle and search

**Progress:** Implemented locally with explicit domain, application and repository contracts, dependency-injected use cases, mirrored tests and in-memory fakes. Python 3.12 checks, 24 tests and 100% measured branch coverage passed; GitHub Actions Customer CI run #44138834947 succeeded. PR #161 awaits review/merge; real database atomicity, contact search and uniqueness remain in later stages.

### Work

1. Implement the Customer entity, creation factory, profile validators, `ACTIVE / ARCHIVED / ERASED` state rules and stable business ownership.
2. Add small use cases for create, tenant-scoped get/list/search, profile update, archive and reactivate; implement erasure policy contract now, but defer real multi-table erasure to Stage 6.
3. Require trusted actor and business scope; check operation permissions through `CustomerAuthorizer` with explicit adapters/fakes.
4. Require `expected_version` on stale-sensitive updates; implement deterministic version conflict behavior.
5. Search by exact ID, normalized contact values (when available), partial name, stable ordering and pagination. Candidate duplicate suggestions are advisory and cannot automatically merge or block on unverified matches.
6. Define minimal typed public projections and error codes independent of HTTP.
7. Add optional `idempotency_key` to create-customer commands and a typed mismatch error; fake-based tests check replay and request equivalence. Stage 5 supplies durable atomic storage and concurrency enforcement.

### Gate

- [x] Guest customer creation and tenant-scoped retrieval work with fake contracts.
- [x] Archive/reactivate state transitions and erased-customer rejection are deterministic.
- [x] Stale version, missing permission and other-business ID are covered. Similar-contact duplicate suggestions await Stage 3.
- [x] Same-key retry is semantically stable; conflicting payloads fail in use-case tests. Atomic concurrent-key enforcement awaits Stage 5/8.

## Stage 3 — Customer-owned profile details

**Progress:** Complete. Contact, address, preference and note use cases implemented using business/customer-scoped repository contracts, host-authorized access, explicit validators, immutable result projections and mirrored fake-based tests. GitHub Actions Customer CI run #44142895435 succeeded and PR #162 was merged. Database uniqueness, rollback and race guarantees will be verified in Stages 5 and 8.

### Work

1. Implement `CustomerContact` for normalized phone/email, primary selection and verified metadata that can only originate from trusted verification.
2. Implement `CustomerAddress` with country-aware minimal fields, labels and at most one default.
3. Implement simple keyed `CustomerPreference` values, deterministic validation and per-customer uniqueness.
4. Implement internal `CustomerNote` creation/list/removal with author provenance and independent read/write permissions; default customer/agent projections exclude notes.
5. Add dedicated validators, normalizers, mappers and repository interfaces only where justified; no generic dynamic-form framework or arbitrary JSON helper buckets.
6. Keep child modifications within the parent business and define version/concurrency behavior for conflicting edits.

### Gate

- [x] Multiple contact values/addresses and single primary/default policies behave correctly with fake repositories.
- [x] Contact values are unverified by default and cannot create an identity link; Stage 4 owns linking.
- [x] Internal notes require independent permissions and are absent from basic customer projections.
- [x] Business scope and child ownership violations produce typed errors in application tests.

## Stage 4 — Internal and provider identities

**Progress:** Implemented with host-injected trusted verification interfaces, internal and external link repositories, exact namespace lookup, explicit get-or-create, revoke/relink, verification provenance and minimal immutable resolution DTOs. Fake-based security tests cover business boundaries, namespace boundaries, invalid/mismatched evidence, retries, active-link uniqueness and revocation. Local Ruff, strict Pyright, 56 pytest tests (97.98% coverage) and build passed; GitHub Actions Customer CI run #44146469993 succeeded. PR #163 awaits review/merge. Concurrent database uniqueness and transaction recovery await Stage 5/8.

### Work

1. Implement `CustomerIdentityLink` with optional association to a host-verified internal user, uniqueness of active links per customer and per `(business_id, identity_user_id)`, and explicit link/unlink use cases.
2. Implement `CustomerExternalIdentity` with provider, channel/account scope, canonical external ID, optional mutable display metadata, verification provenance and `ACTIVE / REVOKED` lifecycle.
3. Add exact `find_by_external_identity` (read only) and explicitly authorized `get_or_create_by_external_identity` (may create a guest customer). No customer is created merely from a message being received.
4. Add guarded link/revoke/relink; a revoked identity is never used for lookup, and transfers require revocation plus trusted re-verification.
5. Keep verification/challenge transport in host adapters. Do not treat matching name, username, claimed number or unauthenticated provider metadata as ownership proof.
6. Describe and test concurrent duplicate link/get-or-create requests; real uniqueness enforcement lands in Stage 5.
7. Expose a minimal `CustomerResolution` from authorized active-link lookup, including verification method/time but excluding private contacts and internal notes. Record auditable re-verification updates without automatically expiring links; the host decides freshness for each operation.

### Gate

- [x] Same internal identity can link to separate business-owned customers without profile sharing.
- [x] Exact external identity lookup cannot cross business/account namespaces.
- [x] Unverified cross-channel matches never silently merge records.
- [x] Revoked links do not resolve; relinking requires fresh evidence after revocation.
- [x] Resolution does not grant downstream authorization; freshness decisions stay with the host.

## Stage 5 — Async persistence, tenant constraints and RLS

**Progress:** Implemented in PR #164. Ruff, Pyright, core tests and PostgreSQL-backed CI pass. All gates are implemented; the final review/merge is pending. The host must supply a migration revision, a non-owner runtime database role and a scheduled idempotency-retention cutoff.

### Work

1. Implement async SQLAlchemy models, dedicated mappers, repository adapters and Customer Unit of Work over a host-injected session factory. Package never creates a global engine.
2. Use package-owned `customer_*` tables and `business_id` on every tenant-scoped table; enforce parent consistency with composite foreign keys and suitable indexes.
3. Enforce at most one active external mapping per provider/account/external ID/business; active internal identity linking uniqueness; contact primary and address default invariants. Use partial indexes or constraints appropriate to PostgreSQL.
4. Expose SQLAlchemy metadata and Alembic integration helpers. Host manages migration revision history/deployments; no automatic startup migrations.
5. Implement PostgreSQL RLS `USING` and `WITH CHECK` policies with transaction-local tenant settings, fail-closed defaults and non-bypass database permissions. Ensure connection pool reuse cannot leak tenant scope.
6. Use database-safe optimistic version updates, bounded conflict handling and correctly scoped repository predicates even with RLS enabled.
7. Persist bounded, business/operation-scoped idempotency keys and canonical request fingerprints atomically with customer creation. Enforce unique concurrent keys and do not store raw personal-data payloads in the idempotency store.

### Gate

- [x] Customer-owned metadata and policy installation are repeatable; the host owns migration revisions.
- [x] Cross-business reads/writes are blocked by application scope checks and PostgreSQL RLS.
- [x] Composite child foreign keys and active uniqueness are exercised against PostgreSQL.
- [x] Runtime role lacks RLS bypass; missing tenant context fails closed and UoW uses transaction-local settings.
- [x] Concurrent same-key creations replay one customer; distinct fingerprints conflict and per-business receipt pruning is available.

## Stage 6 — Transactional audit and privacy erasure

### Work

1. Implement a dedicated `AuditRepository` contract inside the Customer UoW; ensure audit and sensitive mutations share the **same database transaction**.
2. Evaluate a maintained existing audit library against AsyncSession participation, privacy controls, fail-closed semantics and PostgreSQL behavior. Wrap it in a dedicated adapter if appropriate; do not introduce a second autonomous transaction.
3. Record minimal actor type/id, business scope, subject, action, timestamp and safe correlation metadata without raw contact details, addresses, internal note text or verification codes.
4. Implement atomic terminal `ERASED` transition: minimal tombstone, removal/sanitization of contacts, addresses, preferences, notes, internal and external links; no automatic changes to independently owned historical records.
5. Coordinate authorization and legal retention decisions through explicit host-facing policy contracts; document limits of package-local erasure.
6. Verify audit failure rolls back mutations, audit entries do not preserve erased values, and erased records cannot be reactivated or linked.

### Gate

- [ ] Every designated sensitive action has an audit record in the same committed transaction.
- [ ] Audit write failure leaves no partially committed business mutation.
- [ ] Erasure clears customer-owned identifying data, preserves only permitted tombstone metadata and blocks reactivation.
- [ ] Audit and retained identifiers comply with documented data-minimization and retention rules.

## Stage 7 — Optional HTTP adapter and integration example

### Work

1. Provide opt-in FastAPI router, DTO mappers and typed-error-to-HTTP mapping; no FastAPI types inside Domain/Application.
2. Supply a generic consumer example showing a host-owned async engine/session factory, trusted `USER`/`SERVICE` actors, authorization adapters, trusted internal identity resolution and externally verified provider assertions.
3. Demonstrate an authorized read projection, guest creation, exact external-identity lookup, verified linking and a version-conflict response.
4. Demonstrate stable idempotency keys across retries and show that `CustomerResolution` carries verification evidence but no permission to access a separate resource. Describe host-owned proof-freshness rules.
5. Document safe configuration of tenant context per transaction and migration composition with multiple packages; no real credentials or business-specific assumptions in examples.
6. Exercise least-privilege service actors and disallow note/erasure access by default.

### Gate

- [ ] Host can compose the module without importing internal services or implementing Customer persistence.
- [ ] API responses mask cross-tenant existence and sensitive details.
- [ ] No provider token, OTP, LLM framework or application workflow dependency enters the Customer core.

## Stage 8 — PostgreSQL acceptance and concurrency hardening

### Work

1. Run real PostgreSQL tests under the actual non-bypass application role with RLS enforced, including all child tables and transaction-local tenant context across pooled connections.
2. Test concurrent create/get-or-create/link/relink, active uniqueness, contact/address defaults, stale `version`, rollback behavior and isolation-level edge cases.
3. Test idempotent creation for guests without external identities: two concurrent requests with the same key, divergent payload reuse, retries after ambiguous timeout, rollback/retry, scope isolation and defined retention expiry.
4. Verify atomic audit/erasure and failure injection, including integrity under forced rollback and retry after conflict.
5. Run Alembic upgrade tests against a clean and an existing shared schema; confirm migrations do not alter unrelated package-owned tables.
6. Use deterministic fake-based unit tests, SQLAlchemy integration tests and PostgreSQL-specific acceptance tests in GitHub Actions with explicit matrix/configuration.

### Gate

- [ ] Cross-tenant leakage tests fail if any essential RLS policy or query scope is removed.
- [ ] Duplicate-provider races never result in multiple active mappings.
- [ ] Failed audit writes prevent committed sensitive changes.
- [ ] CI PostgreSQL acceptance, migrations, Ruff, Pyright and coverage gates pass.

## Stage 9 — Packaging and release readiness

### Work

1. Stabilize the versioned public facade, DTOs, documented errors, API compatibility rules and controlled `__init__.py` exports.
2. Replace all illustrative README snippets with passing executable examples and verify optional extras in isolated clean environments.
3. Build wheel and sdist with included typed marker and migration resources; test installation without editable source paths.
4. Review indexes, pagination, operational metrics, personal-data logging, default authorizations, migration rollback strategy and backup/retention documentation.
5. Publish release notes and a documented SemVer strategy. Package publication is separate and requires an explicit release decision.

### Gate

- [ ] Installation, import, documented examples and distribution contents pass in clean environments.
- [ ] Public API compatibility, security threat model and operational setup are reviewed.
- [ ] All prior stage gates are satisfied; no known cross-tenant or audit atomicity failures remain.

## Explicitly deferred

- Automatic customer merging or cross-business identity graphs.
- General CRM campaigns, tagging engines, rich activity timelines or attachments.
- Fuzzy name matching, external search infrastructure and ML-based identity decisions.
- Internal OTP/messaging transports, provider webhook handling, agent prompts and conversation state.
- Domain event infrastructure, event bus, transactional outbox, distributed transactions and a saga framework.
- A multi-provider database portability framework; PostgreSQL remains the production acceptance target.

## Implementation discipline

Use small, use-case-oriented application services. Keep mapping, validation, policy, persistence, cryptography and provider integration in explicitly named responsible components. Respect dependency direction and explicit contracts; implementations inherit their interface/Protocol where appropriate. Structure tests to mirror production modules. Do not add speculative interfaces or folders, and do not silently carry forward wrong structure only to minimize a diff. Pause at every stage gate for review before advancing.
