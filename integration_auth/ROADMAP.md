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
- dedicated mappers, validators, policies, crypto/security components, repositories and adapters;
- no provider-specific logic in domain/application layers;
- controlled public APIs through package `__init__.py` files;
- test tree mirroring source responsibility/layer structure;
- independent Fake/Builder/Factory/Test Helper files under `tests/support`;
- Ruff, Ruff format, Pyright strict, pytest and branch coverage >= 85%;
- host-owned SQLAlchemy engine/sessionmaker and Alembic revision graph;
- no logging of raw credentials, secrets, signatures or canonical secret material.

## Stage 0 — Package foundation and architecture contract

**Status: COMPLETE**

Foundation, packaging, docs, test structure and quality gates are established.

## Stage 1 — Core domain: integration identity and authorization model

**Status: COMPLETE**

Implemented integration clients, credential metadata/lifecycle, principals, permissions, scopes,
resources, typed IDs, and inbound/outbound credential direction.

## Stage 2 — Canonical request and cryptographic contracts

**Status: COMPLETE**

Implemented canonical request/query rules, SHA-256 hashing, HMAC-SHA256 signing/verification,
constant-time comparison, timestamp tolerance, and known-answer vectors.

## Stage 3 — Replay protection

**Status: COMPLETE**

Implemented atomic `NonceStore` contract, replay window policy, replay protector, timestamp checks,
and concurrency behavior against an atomic fake. Real persistence atomicity was added in Stage 7.

## Stage 4 — Application authentication services

**Status: COMPLETE**

Implemented client/credential readers, transient secret-provider boundary, clock contract,
credential eligibility policy, signed-request authentication service, and principal mapping.

## Stage 5 — Authorization: permissions and scopes

**Status: COMPLETE**

Implemented exact permission checks, exact resource-scope checks, framework-neutral authorization
results, stable decision reasons, and `IntegrationAuthorizer`.

Authorization remains independent of HTTP/FastAPI and has no wildcard or implicit inheritance.

## Stage 6 — Credential lifecycle and provisioning

**Status: COMPLETE**

Implemented services:

- register/create integration client;
- issue credential;
- rotate credential;
- revoke credential;
- expire credential;
- update permissions/scopes.

Implemented security/architecture boundaries:

- explicit client/credential ID generator contracts;
- UUID4 standard-library generator adapters;
- `CredentialSecretGenerator` contract;
- `SecretsCredentialSecretGenerator` producing 256-bit secrets;
- `CredentialSecretProtector` contract;
- `ProtectedCredentialSecret` type for persistence boundaries;
- raw secrets excluded from object `repr`;
- protected secret material excluded from object `repr`;
- raw secret returned only by issuance/rotation result;
- credential entities still contain no secret material;
- provisioning repositories accept protected secret material, never raw secret bytes;
- explicit `overlap_seconds` rotation window;
- direction-specific rotation so inbound/outbound credentials remain independent;
- rotation repository operation is explicitly atomic;
- lifecycle snapshot construction is handled by a dedicated domain service;
- Unix timestamp conversion is handled by a dedicated application mapper.

Rotation behavior:

```text
same client + same direction + currently usable ACTIVE credentials
    -> expiry shortened to overlap deadline
opposite direction
    -> untouched
new credential
    -> ACTIVE and independently managed
```

A zero-second overlap is supported while preserving domain timestamp invariants.

Tests mirror:

- `domain/services`;
- `domain/policies`;
- `application/dto/provisioning`;
- `application/mappers/time`;
- `application/security`;
- `application/services/provisioning`;
- `infrastructure/security`;
- dedicated provisioning fakes/builders/factories under `tests/support/application/provisioning`.

The host provides the `CredentialSecretProtector` implementation appropriate for its key-management
system. Persistence stores only `ProtectedCredentialSecret`.

## Stage 7 — Async SQLAlchemy persistence

**Status: COMPLETE**

Implemented repository adapters using a host-provided async session factory.

Requirements delivered:

- table prefix `integration_auth_`;
- no global Engine/SessionMaker;
- repository contracts remain in application layer;
- dedicated persistence mappers;
- real atomic nonce consumption under concurrency;
- real atomic credential rotation transaction;
- protected secret persistence only; never raw plaintext secrets;
- transient verification-secret recovery through a host-provided unprotector;
- indexes for authentication hot paths;
- no FK to Identity/Store/Organization tables;
- real async SQLite integration/concurrency tests.

## Stage 8 — Host-owned Alembic integration

**Status: COMPLETE**

Implemented public migration helpers:

- `INTEGRATION_AUTH_TABLE_PREFIX`;
- `integration_auth_metadata()`;
- `include_integration_auth_name(...)`.

The package exposes SQLAlchemy metadata plus an Alembic-compatible name filter while keeping
`alembic.ini`, `env.py`, revision IDs, revision files, ordering, version directories, and the full
revision graph in the consuming host application.

Real Alembic autogenerate tests verify discovery of all integration-auth tables and verify that
unrelated host-owned tables are ignored by the package filter.

## Stage 9 — FastAPI adapter

**Status: COMPLETE**

Implemented presentation-layer integration:

- fixed signed-request header parsing for client ID, timestamp, nonce, and signature;
- dedicated required-header validation;
- FastAPI request -> `AuthenticateIntegrationRequest` mapping;
- raw URL path preservation when ASGI supplies `raw_path`;
- canonical duplicate-query handling through the existing canonical query encoder;
- request-body hashing through the `BodyHasher` contract;
- authentication dependency returning `IntegrationPrincipal`;
- permission dependency factory with optional host-provided resource resolver;
- explicit application contracts for request authentication and authorization;
- generic 401 mapping for malformed/failed machine authentication and replay rejection;
- generic 403 mapping for authenticated integrations lacking permission/scope;
- signature values excluded from presentation/application DTO `repr`;
- optional `fastapi` package extra rather than a mandatory core dependency;
- real FastAPI `Depends(...)` route tests using `TestClient`.

Required semantics are enforced:

```text
failed authentication -> 401
authenticated principal lacking authorization -> 403
```

Routes remain host-owned and thin. The adapter does not add persistence, crypto, replay, or
authorization logic to route handlers.

## Stage 10 — External protocol interoperability example

**Status: IN REVIEW**

Implemented executable interoperability examples:

- one shared deterministic `vectors.json` fixture;
- Python HMAC-SHA256 signing and verification using the package implementations;
- PHP canonicalization and HMAC-SHA256 verification against the same vectors;
- separate inbound and outbound credentials/secrets to demonstrate bidirectional isolation;
- duplicate-query and RFC3986 encoding coverage;
- executable Python rotation example showing same-direction overlap behavior;
- executable exact permission and resource-scope allow/deny examples;
- subprocess tests for Python examples;
- real PHP CLI execution when PHP is available, with an explicit skip otherwise.

Example fixture credentials are documentation/test-only and must never be reused in real integrations.

## Stage 11 — Multi-auth host composition example

**Status: PLANNED**

Demonstrate a host using both `hamresan-identity` and `hamresan-integration-auth` without package
coupling.

## Stage 12 — Security hardening and release readiness

**Status: PLANNED**

Review:

- canonicalization ambiguity;
- timing-safe verification;
- replay/concurrency;
- rotation/revocation;
- secret exposure/logging;
- permission/scope escalation;
- clock-skew edge cases;
- persistence indexes/hot paths;
- wheel/build smoke tests;
- deployment and release checklist.

Optional future work remains demand-driven: Ed25519, Redis replay stores, key identifiers, audit
hooks and caching.
