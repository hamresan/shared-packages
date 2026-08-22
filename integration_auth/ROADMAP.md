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

## Stage 1 — Core domain: integration identity and authorization model

**Status: COMPLETE**

## Stage 2 — Canonical request and cryptographic contracts

**Status: COMPLETE**

## Stage 3 — Replay protection

**Status: COMPLETE**

## Stage 4 — Application authentication services

**Status: COMPLETE**

## Stage 5 — Authorization: permissions and scopes

**Status: COMPLETE**

## Stage 6 — Credential lifecycle and provisioning

**Status: COMPLETE**

Implemented integration-client registration, grant updates, credential issuance, direction-specific
rotation with overlap, revocation, expiration, protected-secret boundaries, secure ID/secret
generation, and atomic rotation persistence contracts.

## Stage 7 — Async SQLAlchemy persistence

**Status: COMPLETE**

Implemented host-session-owned async SQLAlchemy adapters with:

- `integration_auth_` table prefix;
- dedicated ORM records and persistence mappers;
- authentication and provisioning repository implementations;
- protected secret persistence only;
- transient verification-secret recovery through a host-provided unprotector;
- atomic nonce consumption via database uniqueness;
- atomic credential rotation in one transaction;
- indexes for authentication hot paths;
- no FK to Identity/Store/Organization tables;
- real async SQLite integration/concurrency tests.

## Stage 8 — Host-owned Alembic integration

**Status: IN REVIEW**

Implemented public migration helpers:

- `INTEGRATION_AUTH_TABLE_PREFIX`;
- `integration_auth_metadata()`;
- `include_integration_auth_name(...)`.

The package exposes only its SQLAlchemy metadata and an Alembic-compatible name filter. The host
application owns `alembic.ini`, `env.py`, revision identifiers, ordering, version directories, and
the full revision graph.

Real Alembic autogenerate tests verify that integration-auth tables are discovered and unrelated
host tables are ignored by the package filter.

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
authenticated principal lacking authorization -> 403
```

## Stage 10 — External protocol interoperability example

**Status: PLANNED**

Deliver executable Python/PHP known-answer interoperability examples for both directions,
including credential rotation and permission/scope examples.

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
