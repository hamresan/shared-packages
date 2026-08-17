# Store Stage 0 Inventory

Source reviewed read-only:

```text
hamresan/sellora/backend/app/modules/store
```

## Classification

### REUSE conceptually

- `Store` aggregate and its separation of setup, availability and moderation state.
- `StoreAddress`, `StoreContact`, `StoreCurrency`, and weekly working schedule value objects.
- Store setup/availability/moderation/suspension enums as code-level strings.
- Section-oriented settings behavior rather than one large generic update operation.
- Dedicated application policies, factories, mappers and repositories as architectural responsibilities.

These components are reimplemented under the shared package namespace rather than copied with Sellora imports.

### ADAPT

- Store aggregate imports and naming: remove all `app.modules...` paths and Sellora-specific references.
- Administrative actor field: generalize `suspended_by_admin_key_id` to host-neutral actor information.
- Persistence model: Sellora uses table `stores`; shared package tables must use the `store_` prefix.
- Ownership persistence: Sellora has a direct foreign key to `identity_users.id`; shared Store must keep `owner_user_id` as an external UUID reference without a database foreign key to Identity.
- Composition: Sellora imports Identity FastAPI authorization dependencies directly. Shared Store must receive authenticated/admin actors through Store-owned contracts supplied by the host.
- SQLAlchemy base/session handling: replace Sellora global infrastructure dependencies with a host-provided async session factory.
- PostgreSQL JSONB usage: keep typed domain objects but isolate PostgreSQL-specific persistence and provide SQLite-compatible tests where practical.
- Identifiers and clock: depend on explicit contracts rather than project-global implementations.

### DEFER

- Cross-module readiness rules involving catalog or communication-channel readiness. These require stable reader/checker contracts and should follow the core package foundation.
- Administrative moderation HTTP API until core owner flows and authorization contracts are stable. The moderation domain state remains supported.
- Channel-specific infrastructure under Sellora Store; channel ownership does not belong inside this reusable package.
- Advanced store administration/listing behavior until the first consumer requirements are confirmed.

### OMIT

- Direct imports from Sellora Identity presentation dependencies.
- Direct database foreign keys to Identity-owned tables.
- Sellora-specific composition classes and module paths.
- Any direct access to catalog, messaging, channel, subscription or other module persistence.

## Source persistence observations

Sellora currently stores the aggregate in one `stores` table with JSONB-backed structured fields for supported languages, address, contacts, currencies and working schedule. It indexes owner, country, business type, setup status, availability, moderation and deletion state.

For the shared package, the first persistence version will retain the single-aggregate-table approach unless implementation testing reveals a concrete reason to split structures into separate tables. The table will be renamed with the package prefix and will not have a foreign key to Identity.

## Stage decisions

- Keep package name `hamresan-store` / Python package `store`.
- Core domain remains framework- and persistence-independent.
- Keep moderation state in the domain because it is intrinsic Store lifecycle behavior, but defer the admin API.
- Readiness is external-state-sensitive and is deferred behind future contracts.
- One-store-per-owner is not embedded as an irreversible domain invariant; enforcement belongs in a dedicated policy/repository check.
- Initial structured address/contact/currency/schedule data remains value-object based and may be JSON-backed in persistence.

## Next implementation stage

Stage 1/2 foundation and domain:

```text
store/
├── pyproject.toml
├── Makefile
├── README.md
├── src/store/domain/
└── tests/domain/
```

After domain quality gates pass, proceed to application contracts and the create/read core use cases.
