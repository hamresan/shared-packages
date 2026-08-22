# hamresan-subscription Release Checklist

Use this checklist before publishing a new `hamresan-subscription` version.

## 1. Scope and compatibility

- Confirm the release contains only intended package changes.
- Confirm domain/application layers still have no dependency on FastAPI, SQLAlchemy, Identity, Store, WordPress, or payment providers.
- Confirm external subject references remain generic `subject_type + subject_id` values with no external foreign keys.
- Confirm payment verification/provider SDK behavior remains outside the package.
- Confirm authentication and authorization implementations remain host-owned.

## 2. Version and public API

- Update `[project].version` in `pyproject.toml` according to the release policy.
- Review exports from:
  - `subscription`
  - `subscription.application`
  - `subscription.infrastructure.persistence`
  - `subscription.migrations`
  - `subscription.presentation`
- Avoid exposing internal implementation modules accidentally.
- Review breaking changes to commands, DTOs, contracts, routes, table names, enum values, or persistence representation.
- Document any intentional breaking change before publishing.

## 3. Persistence and migrations

- Confirm all package-owned tables still use the `subscription_` prefix.
- Confirm package foreign keys target only Subscription-owned tables.
- Confirm timestamp columns use the package UTC-aware persistence type where domain timestamps require timezone awareness.
- Confirm the package exposes metadata/filter helpers only; Alembic revision history remains host-owned.
- If persistence schema changed, create and test the required revision in the consuming host application.
- Verify Alembic autogenerate does not treat unrelated host tables as Subscription-owned.

## 4. Quality gates

From `subscription/` run:

```bash
make install-dev
make check
```

`make check` must pass all of:

```text
Ruff
Ruff format --check
Pyright strict
pytest
branch coverage >= 85%
wheel + sdist build
built-wheel import smoke test
```

The wheel smoke test installs the built wheel into an isolated target directory and verifies controlled public imports from the artifact rather than from `src/`.

## 5. Consumer integration

From `examples/subscription_consumer/` run:

```bash
python -m pip install -e "../../subscription"
python -m pip install -e ".[test]"
make check
```

The real consumer integration must continue to cover:

- host-owned SQLAlchemy engine/sessionmaker;
- host-owned Alembic environment/revision graph;
- host authentication and authorization adapters;
- BASE and ADDON plan creation;
- combined time/usage trial;
- generic usage recording;
- manual add-on grant;
- paid activation and renewal after a verified external event;
- typed entitlement resolution.

## 6. Distribution artifact inspection

After `make check`:

```bash
ls -lh dist/
```

Confirm both artifacts exist:

```text
hamresan_subscription-<version>-py3-none-any.whl
hamresan_subscription-<version>.tar.gz
```

Confirm the README renders correctly as package metadata and the artifact contains the `subscription` package.

Do not commit `dist/` artifacts to the repository.

## 7. GitHub checks

Before merge/release, require green status for relevant workflows:

```text
Subscription CI / check
Subscription Consumer Integration CI / check
```

Branch protection/rulesets should mark required checks as mandatory for `main`.

## 8. Publish

Publishing credentials, package registry configuration, signing, provenance, and release automation belong to repository/organization operations, not to the runtime package.

Before publishing:

- confirm the target registry and package name;
- confirm the version does not already exist;
- publish from a clean commit on `main` or an approved release tag;
- retain immutable release artifacts/provenance according to repository policy.

## 9. Post-release verification

Install the released version in a clean environment:

```bash
python -m pip install hamresan-subscription==<version>
python -c "import subscription"
```

Then verify at least one real consuming application can compose its SQLAlchemy, Alembic, authentication/authorization, and Subscription application services against the released distribution.
