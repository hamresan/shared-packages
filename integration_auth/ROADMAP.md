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

**Status: IN PROGRESS**

Goals:

- create installable `hamresan-integration-auth` package;
- establish clean source/test folder structure;
- add `README.md`, `ROADMAP.md`, `Makefile`, `pyproject.toml`;
- add package import smoke test;
- add GitHub Actions quality gate;
- freeze initial terminology and ownership boundaries.

No authentication logic is implemented in this stage.

Exit criteria:

- package installs editable;
- `make check` passes;
- source/test structures are ready for incremental implementation;
- README clearly explains internal-project and external-integration usage.

## Stage 1 — Core domain: integration identity and authorization model

Define domain concepts only.

Planned concepts:

- `IntegrationClient`;
- `IntegrationCredential`;
- credential status/lifecycle enums;
- `IntegrationPrincipal`;
- `Permission`;
- `IntegrationScope`;
- `IntegrationResource`;
- client/credential identifiers;
- credential direction/purpose if needed for two-way communication;
- invariants for active/revoked/expired credentials;
- permission and scope value validation.

Key rules:

- machine identity is independent from user identity;
- permissions and scopes are generic strings/value objects;
- no WordPress-specific entities;
- no cryptographic implementation in domain entities.

Tests:

- mirror `domain/entities`, `enums`, `policies`, `validators`, `value_objects`;
- cover invalid identifiers, permissions, scopes and lifecycle transitions.

## Stage 2 — Canonical request and cryptographic contracts

Define the signing protocol and abstraction boundaries.

Planned concepts:

- `CanonicalRequest`;
- request method/path/query/body hash representation;
- canonicalization rules;
- signature encoding;
- `RequestSigner` contract;
- `RequestVerifier` contract;
- body hasher contract/component where useful;
- timestamp tolerance policy;
- constant-time signature comparison requirements.

First implementation:

- HMAC-SHA256 signer/verifier.

Protocol must define exactly:

```text
HTTP_METHOD
PATH_AND_QUERY
TIMESTAMP
NONCE
BODY_SHA256
```

The canonicalization specification must be deterministic across Python and PHP.

Tests:

- canonical vectors;
- Python signing/verifying vectors;
- invalid body/path/query/timestamp/signature cases;
- fixed known-answer vectors suitable for a future PHP/WordPress interoperability test.

## Stage 3 — Replay protection

Implement replay defense as a first-class application boundary.

Planned contracts/components:

- `NonceRepository` / replay store contract;
- timestamp policy;
- nonce uniqueness policy;
- `ReplayProtector` service or equivalent focused component;
- explicit replay window configuration.

Requirements:

- reject stale/future timestamps outside configured tolerance;
- reject repeated nonce per integration client within replay window;
- nonce consumption must be atomic at the persistence boundary;
- concurrent duplicate requests must not both succeed.

Tests:

- unit policy tests;
- concurrent replay tests at persistence/integration stage once SQLAlchemy exists.

## Stage 4 — Application authentication services

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

Implement authorization independent of HTTP framework.

Planned API:

- `IntegrationAuthorizer`;
- permission requirement policy;
- resource/scope authorization policy;
- authorization result/errors.

Support two forms:

1. route/action-level permission checks;
2. resource-level permission + scope checks.

Examples:

```text
catalog.write
orders.read + store:store-123
```

The package must not know what Catalog, Order or Store objects are.

Tests:

- permission allow/deny;
- scope allow/deny;
- wildcard support only if explicitly designed and tested;
- no implicit privilege escalation.

## Stage 6 — Credential lifecycle and provisioning

Implement credential management use cases.

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
- stored representation must follow chosen verification design safely;
- overlap/rotation window explicitly modeled;
- incoming and outgoing credentials can be managed independently;
- no raw secret in logs or ordinary response DTOs after issuance.

## Stage 7 — Async SQLAlchemy persistence

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

Tests:

- real async SQLAlchemy integration tests;
- transaction/rollback behavior;
- concurrent nonce consumption test;
- credential rotation/revocation persistence.

## Stage 8 — Host-owned Alembic integration

Expose migration metadata/filter helpers while keeping revision history in the host.

Requirements:

- `integration_auth_metadata()`;
- `include_integration_auth_name()` or equivalent;
- package table prefix ownership tests;
- real Alembic autogenerate integration test;
- no `alembic.ini`, package revision graph, or package-owned migration ordering.

## Stage 9 — FastAPI adapter

Add optional framework adapter.

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

Tests:

- real ASGI/httpx adapter tests;
- tampered body/signature;
- missing headers;
- stale timestamp;
- replayed nonce;
- missing permission;
- wrong resource scope.

## Stage 10 — External protocol interoperability example

Create a real consumer example for Python backend ↔ WordPress-style external plugin.

The package remains generic; example code may demonstrate WordPress/PHP interoperability.

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

Perform adversarial review before first release.

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

Optional future work must be demand-driven:

- Ed25519 signer/verifier;
- alternative replay stores such as Redis;
- key identifiers and multiple simultaneous verification keys;
- audit/event hooks;
- caching of non-secret client metadata.

Do not add these abstractions prematurely unless a concrete consumer needs them.
