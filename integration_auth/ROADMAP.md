# hamresan-integration-auth — Roadmap

This roadmap builds a reusable machine-to-machine authentication and authorization package incrementally.

The package must remain generic: WordPress is a consumer, not a domain concept.

## Global constraints

Every stage must preserve:

- Clean Architecture and SOLID;
- explicit dependency injection;
- no Service Locator;
- no direct dependency on `hamresan-identity`, Store, Subscription, WordPress, WooCommerce, or payment providers;
- thin services/routes;
- dedicated mappers, validators, policies, crypto components, repositories and adapters;
- no provider-specific logic in domain/application layers;
- controlled public APIs through package `__init__.py` files;
- test tree mirroring source responsibility/layer structure;
- independent Fake/Builder/Factory/Test Helper files under `tests/support`;
- Ruff, Ruff format, Pyright strict, pytest and branch coverage >= 85%;
- host-owned SQLAlchemy engine/sessionmaker and Alembic revision graph;
- no logging of raw credentials, secrets, signatures or canonical secret material.

## Stage 0 — Package foundation and architecture contract

**Status: COMPLETE**

Goals:

- create installable `hamresan-integration-auth` package;
- establish clean source/test folder structure;
- add `README.md`, `ROADMAP.md`, `Makefile`, `pyproject.toml`;
- add package import smoke test;
- add GitHub Actions quality gate;
- freeze initial terminology and ownership boundaries.

Exit criteria completed:

- package installs editable;
- `make check` passes;
- source/test structures support incremental implementation;
- README explains internal-project and external-integration usage.

## Stage 1 — Core domain: integration identity and authorization model

**Status: COMPLETE**

Implemented domain concepts:

- `IntegrationClient`;
- `IntegrationCredential` metadata without raw secret material;
- `IntegrationPrincipal`;
- credential status/lifecycle enums;
- `Permission`;
- `IntegrationScope`;
- `IntegrationResource`;
- typed client/credential identifiers;
- host-perspective inbound/outbound credential direction;
- active/revoked/expired credential invariants;
- permission and scope validation;
- credential lifecycle transition policy.

Key rules:

- machine identity remains independent from user identity;
- permissions and scopes remain generic value objects;
- no WordPress-specific entities;
- no cryptographic implementation in domain entities.

## Stage 2 — Canonical request and cryptographic contracts

**Status: IN REVIEW**

Implemented in this stage:

- `CanonicalRequest`;
- exact canonical request validation;
- deterministic RFC3986 query canonicalization;
- exact canonical serialization of:

```text
HTTP_METHOD
PATH_AND_QUERY
TIMESTAMP
NONCE
BODY_SHA256
```

- `BodyHasher` contract;
- `RequestSigner` contract;
- `RequestVerifier` contract;
- SHA-256 body hasher;
- HMAC-SHA256 signer;
- HMAC-SHA256 verifier using constant-time comparison;
- configurable timestamp-tolerance policy;
- fixed known-answer SHA-256/HMAC vectors suitable for future PHP interoperability tests.

Canonicalization rules are documented in `README.md`. Stage 2 intentionally does not consume/store nonces and does not authenticate complete incoming requests.

Tests cover:

- canonical query ordering/encoding and duplicate parameters;
- canonical serialization with and without query parameters;
- invalid method/path/query/timestamp/nonce/body-hash inputs;
- timestamp skew boundaries;
- fixed body-hash/signature vectors;
- changed path/query/timestamp/body hash;
- invalid signature;
- empty HMAC secret.

## Stage 3 — Replay protection

**Status: PLANNED**

Implement replay defense as a first-class application boundary.

Planned contracts/components:

- `NonceRepository` / replay store contract;
- nonce uniqueness policy;
- `ReplayProtector` service or equivalent focused component;
- explicit replay window configuration;
- reuse the Stage 2 timestamp-tolerance policy where appropriate.

Requirements:

- reject stale/future timestamps outside configured tolerance;
- reject repeated nonce per integration client within replay window;
- nonce consumption must be atomic at the persistence boundary;
- concurrent duplicate requests must not both succeed.

Tests:

- unit policy tests;
- concurrent replay tests at persistence/integration stage once SQLAlchemy exists.

## Stage 4 — Application authentication services

**Status: PLANNED**

Implement machine-request authentication use cases.

Planned contracts:

- `IntegrationClientRepository`;
- `IntegrationCredentialRepository`;
- `Clock`;
- identifier/secret generation abstractions where required;
- Unit of Work contracts.

Planned services:

- authenticate signed request;
- resolve active credential;
- verify canonical request/signature;
- apply timestamp/replay checks;
- build `IntegrationPrincipal`.

Service rules:

- orchestration only;
- no SQLAlchemy/FastAPI in application layer;
- no cryptographic private helper logic inside services.

## Stage 5 — Authorization: permissions and scopes

**Status: PLANNED**

Implement authorization independent of HTTP framework.

Planned API:

- `IntegrationAuthorizer`;
- permission requirement policy;
- resource/scope authorization policy;
- authorization result/errors.

Support:

1. route/action-level permission checks;
2. resource-level permission + scope checks.

Examples:

```text
catalog.write
orders.read + store:store-123
```

The package must not know what Catalog, Order or Store objects are.

## Stage 6 — Credential lifecycle and provisioning

**Status: PLANNED**

Planned services:

- register/create integration client;
- issue credential;
- rotate credential;
- revoke credential;
- expire credential;
- update permissions/scopes where appropriate.

Security requirements:

- secrets generated with strong entropy;
- raw secret returned only at issuance/rotation boundary if required;
- stored representation must follow the chosen verification design safely;
- overlap/rotation window explicitly modeled;
- incoming and outgoing credentials managed independently;
- no raw secret in logs or ordinary response DTOs after issuance.

## Stage 7 — Async SQLAlchemy persistence

**Status: PLANNED**

Implement persistence adapters with host-provided `AsyncSessionFactory`.

Planned tables use prefix:

```text
integration_auth_
```

Likely persistence areas:

- integration clients;
- credentials;
- permissions;
- scopes;
- consumed nonces/replay records.

Requirements:

- no global engine/sessionmaker;
- explicit repository implementations;
- mapper/hydrator components separated from repositories;
- atomic nonce/replay protection;
- indexes for authentication hot paths;
- no FK to Identity/Store/Organization tables.

## Stage 8 — Host-owned Alembic integration

**Status: PLANNED**

Expose migration metadata/filter helpers while keeping revision history in the host.

Requirements:

- `integration_auth_metadata()`;
- `include_integration_auth_name()` or equivalent;
- package table prefix ownership tests;
- real Alembic autogenerate integration test;
- no `alembic.ini`, package revision graph, or package-owned migration ordering.

## Stage 9 — FastAPI adapter

**Status: PLANNED**

Planned responsibilities:

- signed-request header schemas/dependencies;
- `AuthenticatedIntegrationDependency`;
- permission dependency/factory for route-level authorization;
- presentation mappers;
- HTTP error mapping;
- credential-management routes only if package ownership justifies them;
- router installer/factory.

Requirements:

- 401 for failed authentication;
- 403 for authenticated principal lacking authorization;
- routes remain thin;
- resource authorization stays outside simplistic route conditionals;
- no Identity implementation dependency.

## Stage 10 — External protocol interoperability example

**Status: PLANNED**

Create a real consumer example for Python backend ↔ WordPress-style external plugin.

Deliverables:

- Python host consumer app;
- exact canonical request specification;
- PHP signing reference snippet or fixture;
- known-answer signature vectors shared between Python and PHP tests;
- plugin → backend signed request example;
- backend → plugin signed request example;
- credential rotation example;
- permission/scope example.

At minimum, interoperability must be proven with deterministic vectors rather than documentation-only pseudocode.

## Stage 11 — Multi-auth host composition example

**Status: PLANNED**

Demonstrate a project using both:

```text
hamresan-identity
hamresan-integration-auth
```

Show:

- user Bearer authentication;
- integration signed-request authentication;
- host-owned canonical Actor mapping;
- same business use case callable through different actor types without coupling business modules to either auth package.

This is an example/composition concern, not a dependency between the packages.

## Stage 12 — Security hardening and release readiness

**Status: PLANNED**

Required checks:

- canonicalization ambiguity review;
- signature timing/constant-time verification review;
- replay/concurrency review;
- credential rotation/revocation review;
- secret exposure/logging review;
- permission/scope escalation review;
- request body/path/query tamper tests;
- clock-skew edge cases;
- DB index/hot-path review;
- package build and built-wheel smoke test;
- README production deployment checklist;
- release checklist.

Optional future work remains demand-driven:

- Ed25519 signer/verifier;
- alternative replay stores such as Redis;
- key identifiers and multiple simultaneous verification keys;
- audit/event hooks;
- caching of non-secret client metadata.

Do not add these abstractions prematurely unless a concrete consumer needs them.
