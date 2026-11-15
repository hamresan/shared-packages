# hamresan-business — staged implementation roadmap

> **Status:** Stages 1–6 are merged. Stage 7 hardening is underway on a separate branch. PostgreSQL concurrency verification remains outstanding until a real PostgreSQL run completes.
>
> **Goal:** A generic, reusable Python package for business and branch organization, with multi-business ownership, independent of any specific consuming application.

Each stage ends with focused tests and a review gate. Do not advance to the next stage before its code, tests and architectural boundaries are verified. Introduce abstractions only for concrete responsibilities; do not build a general enterprise/HR platform.

## Stage overview

| Stage | Focus | Demonstrable result |
| --- | --- | --- |
| **0** | Scope, package boundaries, reuse review | Agreed data ownership and minimal contract inventory |
| **1** | Python package foundation and domain primitives | Installable skeleton, type-safe core, quality checks |
| **2** | Business lifecycle | One user can create and own several businesses |
| **3** | Branch lifecycle | Single- and multi-branch structures work consistently |
| **4** | Membership and authorization | Multi-user, multi-business and branch-scoped permissions |
| **5** | Async persistence and migrations | Host-composed SQLAlchemy and Alembic integration |
| **6** | FastAPI and Identity/Notification composition | Secure OTP-authenticated consumer example |
| **7** | Integration hardening and packaging | Verified public contracts and release-ready distribution |

## Stage 0 — Domain boundaries and reuse assessment

### Work

1. Confirm that `Business` is an organization root, `Branch` is a location or operating unit, and `BusinessMembership` links external user identities to organizations.
2. Use the same business/branch model for single- and multi-branch organizations. A business may have zero branches during onboarding.
3. Do **not** place `owner_user_id` uniqueness on a user, and do not treat the branch as a separate business. Multiple owner memberships across businesses must be supported.
4. Review public contracts and relevant value objects in existing `identity`, `notification`, and `store` packages. Reuse published capabilities rather than duplicating OTP, tokens, notifications, or generic validation logic.
5. Finalize the employee boundary: membership and branch access here; staffing, payroll, attendance, qualifications, and schedules outside this package.
6. Record the minimum Business/Branch fields, lifecycle states, membership roles and safe archival semantics. Avoid speculative billing, organizational hierarchies, and universal RBAC.

### Gate

- [ ] Core entities, lifecycle invariants, and ownership/branch boundaries reviewed.
- [ ] Shared-package compatibility and explicit host responsibilities confirmed.
- [ ] Initial public API and test scenarios approved before coding.

## Stage 1 — Package foundation

### Work

1. Add `business/pyproject.toml`, `src/business/` layout, controlled public `__init__.py` exports and package typing marker.
2. Use Python 3.12+, `uv`, a reproducible lockfile, Ruff, strict Pyright, pytest, build verification and CI.
3. Add framework-independent domain identifiers/value objects, validators and application contracts only as needed.
4. Mirror the production package structure under `tests/`, with independent fake/factory helpers in separate files.

### Gate

- [ ] Wheel/sdist builds and installs in a clean environment.
- [ ] Unit tests, Ruff, formatter, Pyright and CI pass.
- [ ] Domain layer has no FastAPI, SQLAlchemy or authentication-provider imports.

## Stage 2 — Business creation, reading and lifecycle

### Work

1. Implement `Business` creation, scoped read/list and safe profile update/archival.
2. Capture only reusable organizational fields (name, type/category, country, default locale/currency, status and timestamps).
3. Use a dedicated business factory, command validators, policies, repository contract and small use cases.
4. Make creation authorization depend on a trusted external actor; never accept an arbitrary owner ID as proof of ownership.
5. Introduce the minimum `BusinessMembership` owner relationship alongside business creation, so the creator receives an owner membership atomically once persistence exists. A user can own multiple businesses from the first usable implementation; Stage 4 expands membership operations and permissions.

### Gate

- [x] The same actor creates two businesses and can read both independently.
- [x] A different actor cannot read or modify either business without an authorized membership.
- [x] Invalid fields and unsafe archival transitions fail deterministically.

## Stage 3 — Branch management

### Work

1. Add `Branch` create/read/update/archive with an immutable `business_id` association.
2. Support zero branches during setup, one branch, and multiple branches using the same API and data model.
3. Model branch-specific address/contact, timezone and lifecycle fields; apply organization defaults only where explicitly defined.
4. Prevent cross-business branch references and reject invalid association changes.
5. Preserve archived branch identities and their references; avoid destructive cascade deletion by default.

### Gate

- [x] One business manages two independent branches; another manages a single branch.
- [x] Cross-business branch updates and access are rejected.
- [x] Archive/reactivation policies preserve referential integrity.

## Stage 4 — Business memberships and branch access

### Work

1. Extend the initial owner `BusinessMembership` with external `user_id`, `business_id`, role, active/invited/revoked state and timestamps.
2. Enforce unique active membership per `(business_id, user_id)` while allowing the same user across multiple businesses.
3. Provide `Owner`, `Manager`, and `Member` roles; one active Owner per business and multiple Managers. Consuming applications retain ownership of domain-specific permissions. Avoid a general role-policy DSL.
4. Implement controlled add/invite, accept, list, Manager/Member role changes, removal, and an explicit atomic ownership transfer; never ordinarily demote or revoke the Owner.
5. Add a narrow branch-access association for members restricted to selected branches; validate every branch belongs to the same business.
6. Make authorization explicit and independently testable, including owner-only actions and a member's authorized branch scope.

### Gate

- [x] One user owns multiple businesses and can hold a non-owner role in another (existing multi-business tests plus membership scenarios).
- [x] Business and branch membership changes are authorization-checked and auditable under the injected unit of work.
- [x] The active Owner cannot be removed or demoted by ordinary membership operations; ownership transfers atomically to an active member.
- [x] Members cannot gain access to a branch in another business by submitting its ID.

## Stage 5 — Async SQLAlchemy persistence and host-owned Alembic

### Work

1. Build SQLAlchemy 2 async models, repositories, mappers and Unit of Work adapters implementing the application contracts.
2. Use package-prefixed tables (`business_*`) and host-injected async session factory; do not create a global engine.
3. Expose package metadata/name-filter helpers for a host-owned Alembic history, compatible with other shared packages.
4. Apply appropriate uniqueness (including at most one active Owner per business), foreign-key and branch-to-business invariants. Use transactional protection for membership/ownership mutations.
5. Define safe transaction boundaries and document host-side tenant isolation and optional PostgreSQL RLS integration; no implicit trust in `business_id` alone.

### Gate

- [ ] PostgreSQL concurrent ownership-transfer test passes in CI (test and service configured; local PostgreSQL unavailable).
- [x] Host-owned metadata naming and Alembic autogeneration check show no schema drift; host migration upgrade across multiple packages remains to be exercised at Stage 7.
- [x] Tenant-scoped repositories and composite foreign keys reject cross-business membership-to-branch references.

## Stage 6 — FastAPI adapter and authentication integration

### Work

1. Add an optional FastAPI router for the supported use cases, with strict request schemas and well-defined authorization dependencies.
2. Compose `hamresan-identity` with `hamresan-notification` in a small consumer example: OTP registration/login, session/JWT validation, then trusted `AuthenticatedActor` mapping.
3. Keep Identity responsible for OTP codes, sessions and tokens. Keep Notification responsible for provider-neutral message delivery.
4. If invitations need delivery, inject a notification contract or let the host coordinate it. Do not implement OTP, SMTP, queues or workers inside Business.
5. Test cross-business authorization at the HTTP boundary. Derive the acting user's identity from trusted authentication only; authorize requested invitees and role changes through business policies, never through the request body alone.

### Gate

- [x] Example authenticates through Identity OTP and signed JWT/session APIs; Notification queues OTP delivery.
- [x] Authenticated users can access their authorized businesses and branches, and Manager branch operations are enforced.
- [x] Unauthorized, foreign-business and revoked members receive safe, deterministic HTTP failures.
- [x] OTP/session/token code remains inside Identity; the Business adapter accepts a trusted actor dependency.

## Stage 7 — Hardening and distribution

### Work

1. Run deterministic unit/integration tests, quality checks, clean-install/build tests, and representative PostgreSQL concurrency tests in CI.
2. Review business/branch archival, membership ownership safety, tenant isolation, transactional consistency, and privacy of personally identifiable contact data.
3. Finalize concise public exports, versioned package contracts, SemVer boundaries and examples.
4. Publish a release candidate or tagged distribution only after a consuming host can compose Identity, Notification and Business without internal imports or bespoke patches.

### Gate

- [x] Public use cases support branchless, single-branch, multi-branch and multi-business-per-owner examples; HTTP tests exercise selected branch visibility and archival safeguards.
- [ ] CI passes lint, format, strict typing, tests, migration checks and package build.
- [ ] No application-specific terms, dependencies, or staff-management functionality slipped into the package.
- [ ] README examples match the implemented API; no documentation-only API is presented as released.

### Stage 7 verification progress

- [x] Identity and Business metadata compose into one host schema; an initial Alembic DDL upgrade produces the expected tables and no autogenerate drift.
- [x] HTTP tests cover restricted members, attempted mutations and archived-business safety.
- [x] CI includes an isolated wheel installation and optional FastAPI/SQLAlchemy import smoke test.
- [ ] Execute PostgreSQL ownership-transfer concurrency test against a live server; GitHub Actions runs have not yet been observed for this repository.
- [ ] Verify the full release gate in CI before tagging or publishing a distribution.

## Deliberately deferred

- Employee HR records, payroll, leave, staffing calendars and scheduling.
- Arbitrary organizational hierarchies, franchise accounting and cross-business parent companies.
- Universal RBAC/ABAC policy engines, custom scripting and general workflow builders.
- Billing/subscription enforcement; the host may impose branch-count limits through its own entitlements.
- Built-in HTTP service, message broker, notification queue or background worker; the package remains independently installable.

These are separate decisions driven by actual consumers, not prerequisites for a usable business-management core.
