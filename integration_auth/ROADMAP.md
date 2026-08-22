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

Implemented client registration, grant updates, credential issuance/rotation/revocation/expiration,
secure secret generation, protected-secret boundaries, direction-specific overlap rotation, and
atomic rotation persistence contracts.

## Stage 7 — Async SQLAlchemy persistence

**Status: COMPLETE**

Implemented host-session-owned repository adapters, dedicated mappers, protected-secret persistence,
atomic nonce consumption, atomic rotation transactions, authentication-path indexes, and async
integration/concurrency tests.

## Stage 8 — Host-owned Alembic integration

**Status: COMPLETE**

Implemented package metadata/filter helpers while keeping the Alembic revision graph owned by the
consuming host.

## Stage 9 — FastAPI adapter

**Status: COMPLETE**

Implemented signed-header parsing, request mapping, authentication/authorization dependencies,
generic 401/403 mapping, optional FastAPI dependency packaging, and real dependency-route tests.

## Stage 10 — External protocol interoperability example

**Status: COMPLETE**

Implemented shared Python/PHP known-answer vectors for inbound/outbound signing plus executable
rotation and exact permission/resource-scope examples.

## Stage 11 — Multi-auth host composition example

**Status: COMPLETE**

Implemented a host-owned `HostActor` composition example that maps `hamresan-identity` human
principals and `hamresan-integration-auth` machine principals without coupling the packages.

## Stage 12 — Security hardening and release readiness

**Status: IN REVIEW**

Hardening work includes:

- explicit canonicalization ambiguity regression tests for plus/space, percent literals, duplicate
  parameters, and UTF-8 input;
- retained constant-time HMAC verification and existing signature tampering tests;
- retained atomic replay/concurrency and rotation rollback tests;
- retained revocation/expiration, secret representation, exact permission/scope, clock-skew, and
  persistence-index tests;
- isolated built-wheel installation/public-import smoke check;
- `make release-check` release gate;
- explicit security/deployment checklist in `SECURITY_REVIEW.md`.

No new authentication protocol or storage provider is introduced in this stage.

Optional future work remains demand-driven: Ed25519, Redis replay stores, key identifiers, audit
hooks and caching.
