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

Foundation, packaging, docs, test structure and quality gates are established.

## Stage 1 — Core domain: integration identity and authorization model

**Status: COMPLETE**

Implemented:

- `IntegrationClient`;
- `IntegrationCredential` metadata without raw secret material;
- `IntegrationPrincipal`;
- credential lifecycle/direction enums;
- `Permission`, `IntegrationScope`, `IntegrationResource`;
- typed identifiers;
- lifecycle, permission and scope validation policies.

## Stage 2 — Canonical request and cryptographic contracts

**Status: COMPLETE**

Implemented:

- `CanonicalRequest`;
- deterministic RFC3986 query canonicalization;
- exact request serialization;
- `BodyHasher`, `RequestSigner`, `RequestVerifier` contracts;
- SHA-256 body hasher;
- HMAC-SHA256 signer/verifier;
- constant-time signature comparison;
- timestamp-tolerance policy;
- fixed known-answer vectors for later cross-language interoperability tests.

## Stage 3 — Replay protection

**Status: COMPLETE**

Implemented:

- atomic `NonceStore` contract;
- `ReplayWindowPolicy`;
- focused `ReplayProtector` service;
- stale/future timestamp rejection before nonce consumption;
- client-scoped replay detection;
- replay/timestamp application errors;
- concurrent duplicate-request behavior proven against an atomic test fake.

A real persistent atomic implementation remains part of Stage 7.

## Stage 4 — Application authentication services

**Status: COMPLETE**

Implemented:

- `IntegrationClientRepository` contract;
- `IntegrationCredentialRepository` contract;
- `CredentialSecretProvider` contract for transient verification material;
- `Clock` contract;
- `AuthenticateIntegrationRequest` DTO;
- `CredentialAuthenticationPolicy`;
- `IntegrationPrincipalMapper`;
- `AuthenticateIntegrationRequestService`;
- explicit authentication errors.

Authentication flow:

```text
resolve client
-> load credential candidates
-> filter usable inbound credentials
-> resolve transient verification material
-> verify signature
-> apply replay protection
-> map IntegrationPrincipal
```

Security/architecture decisions:

- credential metadata remains separate from raw secret material;
- service depends on crypto/repository/replay abstractions and stays orchestration-only;
- invalid client, unusable credential, unavailable secret, invalid signature and replay/timestamp failures fail closed;
- multiple usable credential candidates are supported for future rotation overlap;
- no SQLAlchemy or FastAPI in the application layer;
- no Unit of Work is introduced yet because Stage 4 has no concrete multi-repository transaction boundary; atomic nonce consumption remains owned by `NonceStore`.

## Stage 5 — Authorization: permissions and scopes

**Status: IN REVIEW**

Implemented:

- exact `PermissionRequirementPolicy`;
- exact `ResourceScopeAuthorizationPolicy`;
- framework-neutral `AuthorizationResult`;
- stable authorization decision reasons;
- `IntegrationAuthorizer`;
- `IntegrationAuthorizationError` for require-style enforcement.

Supported forms:

1. route/action-level permission checks;
2. resource-level permission + exact resource-scope checks.

Examples:

```text
catalog.write
orders.read + store:store-123
```

Authorization rules:

- permission matching is exact;
- resource type and resource ID must both match an explicit scope grant;
- no wildcard permission/scope behavior;
- no implicit permission inheritance;
- permission denial happens before scope evaluation;
- authorization is independent of HTTP/FastAPI;
- the package does not know what Catalog, Order, Store, or Organization objects are.

Tests mirror domain policies, application DTOs and authorization services, with reusable builders/factories under `tests/support/application/authorization`.

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

- strong secret entropy;
- raw secret returned only at issuance/rotation boundary when required;
- no plaintext secret persistence;
- explicit overlap/rotation window;
- independent inbound/outbound credential lifecycle.

## Stage 7 — Async SQLAlchemy persistence

**Status: PLANNED**

Implement repository adapters using a host-provided async session factory.

Requirements:

- table prefix `integration_auth_`;
- no global Engine/SessionMaker;
- repository contracts remain in application layer;
- dedicated persistence mappers/hydrators;
- real atomic nonce consumption under concurrency;
- indexes for authentication hot paths;
- no FK to Identity/Store/Organization tables.

## Stage 8 — Host-owned Alembic integration

**Status: PLANNED**

Expose metadata/filter helpers while keeping revision history in the host application.

## Stage 9 — FastAPI adapter

**Status: PLANNED**

Planned responsibilities:

- signed-request header parsing;
- authentication dependency;
- permission dependency/factory;
- presentation mappers;
- HTTP error mapping;
- thin routes.

Required semantics:

```text
failed authentication -> 401
missing authorization -> 403
```

## Stage 10 — External protocol interoperability example

**Status: PLANNED**

Deliver executable Python/PHP known-answer interoperability examples for both directions.

## Stage 11 — Multi-auth host composition example

**Status: PLANNED**

Demonstrate a host using both `hamresan-identity` and `hamresan-integration-auth` without package coupling.

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

Optional future work remains demand-driven: Ed25519, Redis replay stores, key identifiers, audit hooks and caching.
