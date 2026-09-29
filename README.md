# Hamresan Shared Packages

A collection of reusable, production-oriented Python packages for building modern backend and SaaS applications.

This repository demonstrates how I design backend capabilities as focused, independently testable packages with explicit contracts, clean architectural boundaries, replaceable infrastructure, and production-focused quality gates.

> **Portfolio note:** This is a public engineering portfolio repository. Each package is intentionally separated from application-specific business logic so its architecture, API design, testing strategy, and integration boundaries can be reviewed independently.

## What this repository demonstrates

- **Python 3.12+** backend development
- **FastAPI** integration and transport boundaries
- **Async SQLAlchemy** persistence
- **Clean Architecture and SOLID** design
- Contract-driven **dependency injection**
- Provider-neutral integrations using adapters and replaceable implementations
- Authentication, authorization, sessions, OAuth, and machine-to-machine security
- External API and AI-agent integrations
- Host-owned database and migration composition
- Strict static typing with **Pyright**
- Automated testing with **Pytest**
- **Ruff** linting and formatting
- Branch coverage quality gates of **85% or higher** where configured

## Packages

| Package | Distribution | What it provides |
| --- | --- | --- |
| [Identity](./identity) | `hamresan-identity` | Passwordless authentication and session management, including OTP flows, token rotation, revocation, rate limiting, identity normalization, and FastAPI integration. |
| [Integration Auth](./integration_auth) | `hamresan-integration-auth` | Machine-to-machine authentication for services, plugins, workers, connectors, and partner applications, including signed requests, replay protection, scopes, permissions, and credential lifecycle management. |
| [Notification](./notification) | `hamresan-notification` | Application-agnostic notification infrastructure with queue-first orchestration, templates, and replaceable SMS, email, and console providers. |
| [Instagram Auth](./instagram_auth) | `hamresan-instagram-auth` | Instagram Professional account OAuth, authorization, permission handling, connection lifecycle, token management, and account identity resolution. |
| [Instagram API](./instagram_api) | `hamresan-instagram-api` | Application-facing Instagram integration for profiles, media, conversations, messages, comments, replies, webhooks, and normalized provider errors. |
| [Store](./store) | `hamresan-store` | Reusable store domain/application package with ownership rules, validation, async SQLAlchemy persistence, FastAPI integration, and host-owned Alembic composition. |
| [Subscription](./subscription) | `hamresan-subscription` | Plans, subscriptions, entitlements, trials, and usage-management capabilities for generic host-owned subjects. |
| [Persona Engine](./persona_engine) | `hamresan-persona-engine` | Provider-neutral persona/style initialization from account-authored text using measurable writing characteristics. |
| [Letta Agent](./letta_agent) | `hamresan-letta-agent` | Reusable Letta integration for agent creation, memory blocks, conversations, interactions, and normalized provider failures. |

Each package contains its own README with package-specific installation, architecture, API, configuration, and integration details.

## Architecture

The packages follow a consistent dependency direction:

```text
Host Application / FastAPI
          |
          v
  Presentation / Public API
          |
          v
   Application Use Cases
          |
          v
   Domain + Contracts
          ^
          |
Infrastructure / Providers
SQLAlchemy / External APIs
```

The important boundary is that business and application code depend on contracts rather than provider-specific implementations.

For example, authentication does not need to know which SMS provider delivers an OTP, a Store package does not need to know how the host authenticates a user, and application services do not need to know provider-specific API details.

## Design principles

The repository follows a few rules consistently:

- **Small, focused responsibilities** — packages and components own explicit capabilities.
- **Dependency inversion** — application logic depends on contracts/interfaces instead of concrete infrastructure.
- **Replaceable providers** — external services are isolated behind adapters or provider contracts.
- **Thin application services** — services orchestrate use cases instead of accumulating mapping, persistence, security, or provider logic.
- **Explicit composition** — host applications own dependency wiring, configuration, and deployment decisions.
- **Persistence isolation** — repositories and SQLAlchemy details stay outside domain/application logic.
- **Host-owned migrations** — reusable packages expose migration metadata without taking control of the consuming application's migration history.
- **Testability by design** — dependencies are injectable and package boundaries can be tested independently.
- **Controlled public APIs** — consumers use documented package APIs instead of depending on internal implementation modules.

## Engineering quality

Packages use a production-oriented quality workflow. Depending on the package, the quality gate includes:

```text
Ruff lint
Ruff format --check
Pyright strict
Pytest
Branch coverage >= 85%
```

Security-sensitive packages additionally include focused tests for authentication/session behavior and concurrency-sensitive flows.

The goal is not only to make the code work, but to keep architecture understandable, dependencies replaceable, and changes safe to review and test.

## Integration examples

The [examples](./examples) directory contains runnable host-application examples showing how independent packages can be composed without bypassing their public boundaries.

Examples include combinations such as:

- Identity + Notification
- Identity + Store
- Subscription integration
- Multi-auth composition
- Instagram-oriented host integrations

These examples demonstrate composition at the application boundary rather than coupling packages directly to one another.

## Repository structure

```text
shared-packages/
├── identity/
├── integration_auth/
├── notification/
├── instagram_auth/
├── instagram_api/
├── store/
├── subscription/
├── persona_engine/
├── letta_agent/
└── examples/
```

Each package owns its source code, tests, packaging configuration, and documentation.

## Exploring the code

If you are reviewing this repository as part of my engineering portfolio, useful starting points are:

1. **[Identity](./identity)** — security-sensitive backend design, authentication/session flows, FastAPI, async persistence, rate limiting, and dependency boundaries.
2. **[Integration Auth](./integration_auth)** — service-to-service security and integration architecture.
3. **[Instagram API](./instagram_api)** and **[Instagram Auth](./instagram_auth)** — third-party API/OAuth integration and provider isolation.
4. **[Store](./store)** — domain/application separation, persistence abstractions, ownership policies, and host integration.
5. **[Notification](./notification)** — provider abstraction and replaceable delivery infrastructure.
6. **[Examples](./examples)** — practical composition of multiple reusable packages.

## Technology

The repository primarily demonstrates experience with Python, FastAPI, Pydantic, async SQLAlchemy, Alembic integration, OAuth/API integrations, Pytest, Pyright, Ruff, dependency injection, provider/adaptor patterns, and clean backend architecture.

## Status

This repository is actively developed. Individual packages may evolve independently and have their own versions and package-specific stability considerations.

For detailed usage and constraints, refer to the README inside the relevant package directory.
