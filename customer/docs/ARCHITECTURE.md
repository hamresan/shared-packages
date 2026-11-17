# Customer architecture and data ownership — Stage 0

> **Status:** Stage 0 review draft. This is a design contract, not an implemented schema. The package is framework-independent at its domain/application core. See [PUBLIC_CONTRACTS.md](PUBLIC_CONTRACTS.md) and [SECURITY_AND_ACCEPTANCE.md](SECURITY_AND_ACCEPTANCE.md).

## Boundary

Customer owns business-scoped customer records, profile details, optional internal-user links, externally verified provider-identity links and customer-local erasure. The host authenticates humans/services, validates business scope, supplies authorization and identity-verification adapters, manages database sessions, coordinates other packages, verifies provider assertions and owns deployment-time migration execution. No dependency on messaging, booking, AI frameworks, provider SDKs or other business packages is allowed in the Customer core.

`Business` is the external tenant authority. A customer references its trusted `business_id` by UUID, without importing a Business entity or requiring cross-package ORM foreign keys. One business has many customers; each customer has one immutable business owner. A person may have separate customers in several businesses, including several guest profiles without a registered internal account. Branch identity never participates in customer ownership.

## Entity ownership and lifecycle matrix

All customer-owned tables use prefix `customer_` and include `business_id`. `created_at`/`updated_at` are timezone-aware UTC timestamps where applicable. No customer data is assumed to be globally unique by name, contact value or inferred real-world person.

| Logical entity | Purpose | Identity / scope | Invariants and deletion |
| --- | --- | --- | --- |
| `Customer` | Business-specific profile | UUID `id`; immutable `business_id`; display name (optional where provider-first onboarding is permitted) | Status `ACTIVE`, `ARCHIVED`, `ERASED`; optimistic integer `version`; erasure terminal; retain minimal tombstone. |
| `CustomerContact` | Phone/email | UUID `id`, `business_id`, `customer_id`, `type`, normalized value | Multiple values; at most one primary per type/customer; verification status must come from a trusted process; erasure removes contact PII. |
| `CustomerAddress` | Optional postal addresses | UUID `id`, `business_id`, `customer_id` | Multiple; at most one default/customer; no external geocoding; erasure removes address PII. |
| `CustomerPreference` | Lightweight structured preferences | UUID `id`, `business_id`, `customer_id`, `key`, simple typed value | Unique `(business_id, customer_id, key)`; no secrets or arbitrary executable policy content; erase with customer. |
| `CustomerNote` | Restricted internal text | UUID `id`, `business_id`, `customer_id`, author actor reference | Immutable provenance of creation; separate read/write permission; erase note content with customer. |
| `CustomerIdentityLink` | Optional link to a trusted internal user | UUID `id`, `business_id`, `customer_id`, `identity_user_id` | At most one active link per customer and `(business_id, identity_user_id)`; unlink/relink require evidence and audit. |
| `CustomerExternalIdentity` | Verified provider account identity | UUID `id`, `business_id`, `customer_id`, provider, provider-scoped account identifier, external subject identifier | `ACTIVE`/`REVOKED`; only active links resolve; verification provenance/time; at most one active customer per canonical provider key and business; erase PII under retention policy. |
| `CustomerIdempotencyRecord` | Deduplicate optional creation retries | `business_id`, operation name, opaque host key | Canonical request fingerprint, outcome/customer reference, limited expiry; unique key per business/operation; commit atomically with creation; purge after bounded retention. |
| `CustomerAuditRecord` (adapter-owned storage) | Minimal security audit | Business, actor type/id, action, subject, event time | Stored through audit repository in same UoW as sensitive change; no raw contact values, note text, address or OTP; retention and erasure reviewed independently. |

The precise physical table shapes, lengths, enums, nullable fields and index names are Stage 5 schema work. Stage 0 fixes semantic ownership and uniqueness rules, not prematurely every storage column.

## Tenant integrity and indexes

- Every child table has a database foreign key on `(customer_id, business_id)` to a unique parent key `(id, business_id)`. This prevents a child carrying Business A's ID from referencing Business B's customer even if the application mistakenly builds a mismatched association.
- Foreign keys do not implicitly grant access. Each customer-owned table has a separately enforced RLS policy with both visibility (`USING`) and write (`WITH CHECK`) rules based on trusted transaction-local business scope. Repositories additionally scope every lookup and mutation by business.
- Partial unique indexes cover active internal links and active external links. The canonical external key is `(business_id, provider, channel_account_id, external_user_id)` **after provider-specific canonicalization**; a provider adapter must define the identifier namespace and not invent a universal phone/username identity.
- Partial uniqueness covers the one-primary-per-contact-type and one-default-address invariants. Preference keys use a scoped unique constraint. The Customer version is checked atomically during update.
- Exact contact lookup uses normalized value indexes within business; partial-name search uses bounded pagination and deterministic ordering. No fuzzy matching in the initial release.

## Verification, identity resolution and safe reads

The host validates inbound provider events and implements proof-of-control challenges, including cross-channel confirmation when needed. It supplies trusted verification evidence for new links and re-verification. Customer validates scope, authorization, link status and conflicts, and stores method/time/provenance. A provider-supplied phone number is not proof unless the provider explicitly attests verified control and the host has evaluated the evidence.

An active external identity can be looked up exactly through a `CustomerResolution` projection. This provides a stable customer/business reference and available verification evidence; it **does not** authorize access to external records, prove current message authenticity, or guarantee adequate freshness for a sensitive operation. The host and resource owner apply purpose-specific verification freshness and authorization. The package does not automatically expire active links due only to elapsed time.

Unverified names, usernames and phones may produce *suggestions* but never automatically link or merge records. A lookup does not create data. Explicit get-or-create creates a new guest only if no active external identity exists, subject to provider authenticity, authorization and atomic database uniqueness.

## Lifecycle and deletion

- `ACTIVE`: normal permitted operations. `ARCHIVED`: profile retained, can be reactivated by an authorized actor. `ERASED`: terminal; no reactivation or new identity links.
- Erasure atomically removes or anonymizes all Customer-owned identifying details and links, writes minimal transactional audit, and retains the stable UUID/business key only as a non-identifying tombstone needed for referential integrity.
- The host must evaluate legal holds/retention before authorizing erasure and coordinate deletion of independent copies owned elsewhere. Historical snapshots owned by other systems are not modified by Customer.
- Revoked external identity records can support limited forensic history where retention permits, but erasure cannot preserve a recoverable personal identifier merely for convenience.

## Dependency and composition rules

- Domain: entities, value objects, lifecycle invariants; **no** FastAPI, SQLAlchemy, business/identity package, LLM or provider imports.
- Application: commands, queries, typed projections/errors, small use cases, repository/UoW/authorization/verification contracts, policies and validators.
- Infrastructure: SQLAlchemy async mapping/repositories/UoW, RLS transaction context, audit adapter and migration metadata.
- Presentation (optional): FastAPI schemas, request/response mappers, trusted actor dependency and typed exception-to-HTTP mapping.
- Bootstrap: explicit composition root and stable public capability facade; external adapters are injected; no service locator or automatic provider registry.
- Tests mirror production responsibilities under `tests/`; dedicated fakes and builders must be narrowly named, not gathered in a giant generic file.

## Deliberately deferred

No universal CRM, cross-business person graph, automatic merge, provider SDK, OTP service, message receiver, rich preferences engine, domain events/outbox, distributed transaction framework, LLM adapter or multi-database abstraction is introduced. Interfaces are added only where independently useful for testing or isolating real external boundaries.
