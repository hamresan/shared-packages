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

Foundation, package structure, quality gates, README and terminology boundaries.

## Stage 1 — Core domain: integration identity and authorization model

**Status: COMPLETE**

Implemented domain concepts:

- `IntegrationClient`;
- `IntegrationCredential`;
- credential lifecycle/status;
- `IntegrationPrincipal`;
- `Permission`;
- `IntegrationScope`;
- `IntegrationResource`;
- typed client/credential identifiers;
- inbound/outbound credential direction;
- credential snapshot invariants and lifecycle transitions.

## Stage 2 — Canonical request and cryptographic contracts

**Status: COMPLETE**

Implemented:

- `CanonicalRequest`;
- deterministic RFC3986 canonical query rules;
- exact canonical request serialization;
- `BodyHasher`, `RequestSigner`, `RequestVerifier` contracts;
- SHA-256 body hashing;
- HMAC-SHA256 signer/verifier;
- constant-time signature comparison;
- timestamp tolerance policy;
- fixed known-answer vectors for future PHP interoperability.

Canonical representation:

```text
HTTP_METHOD
PATH_AND_QUERY
TIMESTAMP
NONCE
BODY_SHA256
```

## Stage 3 — Replay protection

**Status: IN REVIEW**

Current implementation scope:

- atomic `NonceStore` contract;
- `ReplayWindowPolicy` with explicit retention configuration;
- `ReplayProtector` application service;
- stale/future timestamp rejection;
- nonce uniqueness scoped by integration client;
- explicit replay/timestamp errors;
- concurrent duplicate-request behavior verified with an atomic test fake.

Rules:

- timestamp validation happens before nonce consumption;
- first `(client_id, nonce)` consumption succeeds;
- repeated consumption must fail while protected;
- nonce expiry must be at least long enough for the request to age outside the accepted timestamp window;
- storage implementations must provide atomic check-and-consume semantics;
- no SQLAlchemy/persistent nonce adapter is added in this stage.

Tests:

- first-use success;
- duplicate rejection;
- client-scoped uniqueness;
- stale/future timestamp rejection without nonce consumption;
- replay-window expiry calculations;
- concurrent duplicate requests do not both succeed.

## Stage 4 — Application authentication services

**Status: NOT STARTED**

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

Rules:

- orchestration only;
- no SQLAlchemy/FastAPI in application layer;
- no crypto helper logic hidden inside services.

## Stage 5 — Authorization: permissions and scopes

**Status: NOT STARTED**

Implement authorization independently from HTTP:

- `IntegrationAuthorizer`;
- permission requirement policy;
- resource/scope policy;
- authorization result/errors.

Support:

1. route/action-level permission checks;
2. resource-level permission + scope checks.

No implicit privilege escalation or wildcard semantics unless explicitly designed and tested.

## Stage 6 — Credential lifecycle and provisioning

**Status: NOT STARTED**

Planned services:

- register integration client;
- issue credential;
- rotate credential;
- revoke credential;
- expire credential;
- update permissions/scopes where appropriate.

Security:

- strong secret entropy;
- raw secret returned only at issuance/rotation boundary when necessary;
- no plaintext persistence;
- explicit overlap/rotation window;
- incoming/outgoing credentials independently manageable.

## Stage 7 — Async SQLAlchemy persistence

**Status: NOT STARTED**

Tables use the `integration_auth_` prefix.

Requirements:

- host-provided async session infrastructure;
- explicit repositories;
- dedicated mappers/hydrators;
- atomic nonce consumption at persistence boundary;
- indexes for authentication hot paths;
- no FK to Identity/Store/Organization tables.

Tests include real async SQLAlchemy transactions and concurrent nonce consumption.

## Stage 8 — Host-owned Alembic integration

**Status: NOT STARTED**

Expose metadata/filter helpers while keeping revision history in the host application.

No package-owned Alembic revision graph.

## Stage 9 — FastAPI adapter

**Status: NOT STARTED**

Presentation/integration responsibilities only:

- signed-request headers/dependencies;
- authenticated integration dependency;
- permission dependency/factory;
- presentation mappers;
- HTTP error mapping.

Expected HTTP behavior:

```text
failed authentication -> 401
authenticated but unauthorized -> 403
```

Routes remain thin.

## Stage 10 — External protocol interoperability example

**Status: NOT STARTED**

Deliver executable Python backend ↔ WordPress/PHP interoperability examples using the Stage 2 known-answer vectors.

Include both directions, credential rotation and permission/scope examples.

## Stage 11 — Multi-auth host composition example

**Status: NOT STARTED**

Demonstrate a host using both:

```text
hamresan-identity
hamresan-integration-auth
```

Show host-owned Actor mapping without introducing dependency between the packages.

## Stage 12 — Security hardening and release readiness

**Status: NOT STARTED**

Required review areas:

- canonicalization ambiguity;
- constant-time verification;
- replay/concurrency;
- rotation/revocation;
- secret/log exposure;
- permission/scope escalation;
- body/path/query tampering;
- clock-skew edge cases;
- DB hot paths/indexes;
- built-wheel smoke tests;
- deployment/release checklist.

Future work such as Ed25519, Redis replay stores, multiple key identifiers, audit hooks, or caching remains demand-driven and must not be added prematurely.
