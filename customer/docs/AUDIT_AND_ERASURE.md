# Transactional audit and privacy erasure

## Design and dependency selection

The Customer package writes **minimal domain audit events**, not full ORM object versions.
We considered SQLAlchemy-History (supports async versioning) and SQLAlchemy-Continuum.
Their historical-version use case can retain previous personal names, addresses, contacts and
notes even after the operational rows are erased. For this privacy-sensitive package, an
explicit, small `CustomerAuditRepository` using the same injected `AsyncSession` is easier to
audit, test and erase correctly. It does not open another transaction or emit best-effort logs.

## Invariants

- Every mutating application use case calls `commit_audited` with a trusted actor, a stable
  action code and a customer UUID. The audit insert and mutation use one transaction;
  an audit write failure rolls the mutation back.
- Audit rows contain only business ID, customer ID, actor UUID/type, action and timestamp.
  They **never** contain previous or new field values, free text, addresses, phone/email,
  provider subjects, OTPs, evidence references or request fingerprints.
- The tenant-scoped audit table inherits the same `USING` and `WITH CHECK` PostgreSQL RLS
  policy as other Customer tables. The host controls database migrations and retention.
- Erasure requires both the `customer.erase` permission and a host-injected
  `CustomerErasurePolicy` that checks legal holds and retention obligations. Without a
  configured policy, the operation fails closed.
- Erasure changes Customer to terminal `ERASED`, removes its display name and deletes
  Customer-owned contacts, addresses, preferences, internal notes, internal identity links,
  external messaging identities and customer-creation receipts. Only ID, business scope,
  version and lifecycle timestamps remain on the Customer tombstone.
- Customer does not delete or rewrite externally owned records or historical snapshots.
  The host must coordinate relevant downstream retention and privacy obligations.
- Audit actor and subject UUIDs are potentially linkable metadata. Hosts must restrict
  read access, define a bounded retention policy and delete expired audit records under
  explicit administrative authorization. The package does not run a background job.

## Public behavior

`CustomerModuleConfig.erasure_policy` is optional for ordinary customer operations.
Calling `module.customers.erase.execute(CustomerMutationCommand(...))` requires the policy,
an authorized actor and the expected Customer version. It returns the erased tombstone
projection. Repeated erasure, reactivation or linking to an erased Customer is rejected.

## Acceptance

PostgreSQL CI exercises same-transaction audit rollback and terminal erasure with RLS.
Tests also verify that retained audit records contain no erased field values. Independently
owned historical records are outside the package and require host integration acceptance.
Integration owners must verify their own regulatory retention rules.
