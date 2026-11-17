# Customer security model and Stage 0 acceptance scenarios

> **Status:** Acceptance inventory backed by staged unit, HTTP and PostgreSQL CI tests through Stage 8. See [ROADMAP.md](../ROADMAP.md) for the individual stage gates; operational duties remain host-owned.

## Trust boundaries and threats

| Boundary / threat | Rule | Acceptance scenario |
| --- | --- | --- |
| Untrusted caller supplies another `business_id` | Host resolves scope; Customer authorizes; SQL repository filters; RLS enforces scope | Cross-business read/write and guessed UUID yield no disclosure or mutation. |
| Stale pooled PostgreSQL session leaks tenant context | Tenant context is transaction-local (`SET LOCAL` or equivalent), set on the same connection before any tenant-scoped statement; no global `SET` | Reused connection for Business B cannot access Business A rows; missing context fails closed. |
| SQL query accidentally omits tenant predicate | PostgreSQL RLS `USING`/`WITH CHECK` on each customer-owned table, non-bypass runtime role | Deliberately unscoped SELECT/INSERT/UPDATE/DELETE cannot cross tenant under runtime role. |
| Child entity points to wrong business | Composite `(customer_id, business_id)` database foreign key | Mismatched child insert/update fails even if application checks are omitted. |
| Inbound provider identifier is forged | Host validates authenticity and namespace; Customer accepts only trusted verification context | Raw sender-provided identifier cannot link a prior private customer. |
| Name/phone similarity misidentifies a person | Suggestions do not assert ownership or cause merge | Two people with same name or shared/unverified number remain distinct. |
| Verification becomes stale | Customer stores evidence method/time; host/resource owner enforces purpose-specific freshness | Active but old link resolves identity while a sensitive host operation still requires re-verification. |
| External identity is revoked/reassigned | Only active link resolves; unique active key; relink requires fresh trusted evidence | Revoked mapping is never treated as active and concurrent relinks cannot fork ownership. |
| AI/service principal exceeds permission | Typed actor and host-supplied action authorizer; minimal projections | Service actor can resolve a permitted customer but cannot read internal notes or erase by default. |
| Agent/API retries guest creation after timeout | Optional durable idempotency key, canonical keyed fingerprint, atomic result | Same-key concurrent creates produce one record; mismatched payload gets typed conflict; no-key creates may remain separate. |
| Multi-table sensitive mutation commits without audit | Customer audit repository shares same UoW transaction | Injected audit failure rolls back profile/link/erasure mutation. |
| Audit or retention preserves erased personal data | Minimize record contents, no raw PII/OTP; erasure policy and retention | Erased profile cannot be reconstructed from customer-owned audit or child tables. |
| Stale profile update overwrites another edit | Atomic expected-version check | Concurrent different-version updates yield a conflict, not lost updates. |
| Future consuming system assumes Customer lookup authorizes its resources | `CustomerResolution` is identification evidence only | Resource owner rejects access without separate authorization despite valid Customer ID. |

## PostgreSQL RLS specification for implementation

1. All customer-owned tenant-scoped tables include `business_id`, even child tables. Customer parent has unique `(id, business_id)` used by composite child foreign keys.
2. The runtime app role does not own tables and lacks `BYPASSRLS`; use `FORCE ROW LEVEL SECURITY` where appropriate, and test with the **real deployment role**, not a superuser or table owner.
3. Each RLS policy checks an application-specific transaction-local tenant setting and denies missing/invalid settings. Strict parsing and default failure are required; never fall back to unrestricted scope.
4. `USING` protects row visibility and modification targets; `WITH CHECK` protects inserted/updated tenant ownership. Privileged maintenance/erasure workflows must have explicitly authorized scope and must not disable tenant controls implicitly.
5. The trusted host or UoW integration sets the business context inside each transaction on the exact connection, before reads/writes. Rollback and pool reuse clear it. Do not accept SQL fragments or user-controlled raw `SET` commands.
6. Verify explicit tenant-scoped SQL predicates **and** RLS together. RLS is defense in depth, not a substitute for application authorization or proper reference binding.

## External-identity verification and freshness

The host or provider adapter authenticates the incoming assertion and checks actual proof-of-control; a displayed phone number or username alone is not proof. Verification evidence carries its method, accepted time, provider/account scope and a safe reference or reason, not the challenge secret. New cross-channel linkage requires authorization and established proof. The host decides if stored proof remains sufficiently fresh for a given sensitive action; no universal lifetime can be inferred from `ACTIVE`.

## Audit and erasure transaction boundary

Within a Customer transaction, the UoW provides ordinary repositories plus the audit repository. A mutation must not commit if its mandatory audit record cannot be written. A third-party library is eligible only if it participates in the injected AsyncSession/transaction, respects privacy/retention, and does not independently auto-commit. Evaluate the library under real PostgreSQL failure injection; do not treat best-effort logs as equivalent to mandatory transactional audit.

Customer erasure leaves only non-identifying tombstone fields and safe audit metadata; other independently owned historical records remain the responsibility of their respective owners. The host evaluates legal holds and retention requirements before granting erasure. The package does not try to implement cross-package distributed transactions.

## Minimum Stage 1–9 test suite requirements

- **Unit:** domain lifecycle, validation/normalization, permissions, typed actor, optimistic versioning, duplicate suggestions, verification evidence, projection minimization and deterministic fake idempotency.
- **SQLAlchemy integration:** repository mapping, transaction boundaries, scoped queries, staged migration loading, composite constraints and error mapping.
- **Real PostgreSQL acceptance:** cross-business SELECT/INSERT/UPDATE/DELETE for every table; missing tenant context; pooled-connection isolation; runtime role bypass checks; races around active identities, create idempotency, version updates, contact/address uniqueness; audit failure rollback; erasure integrity; migration upgrade against mixed package metadata.
- **HTTP/host integration:** trusted actor injection, denied accesses with indistinguishable safe errors, minimal projection and no accidental ORM/PII serialization.
- **Packaging/CI:** mirrored test folders, narrowly scoped fakes/builders, Ruff, strict Pyright, coverage gate, wheel/sdist clean installation and PostgreSQL GitHub Actions service.

Each release must rerun these checks, review newly introduced contracts and link CI evidence to the relevant stage gate. For operational review, see [Operations and release](OPERATIONS_AND_RELEASE.md).
