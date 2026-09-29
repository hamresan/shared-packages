# shared-packages

A collection of reusable Python packages shared across Hamresan applications.

The repository keeps common capabilities in independent, application-agnostic packages with clear public contracts. Each package owns a focused responsibility and can be composed by a host application without depending on application-specific business logic.

## Packages

| Package | Distribution | Purpose |
| --- | --- | --- |
| [identity](./identity) | `hamresan-identity` | Passwordless identity and session management for FastAPI/Python applications, including OTP flows, session persistence, token rotation, revocation, rate limiting, and identity normalization. |
| [instagram_auth](./instagram_auth) | `hamresan-instagram-auth` | Instagram Professional account OAuth/authorization, permission handling, connection lifecycle, token management, and account identity resolution. |
| [instagram_api](./instagram_api) | `hamresan-instagram-api` | Application-facing Instagram API integration for authorized accounts, including profiles, media, conversations, messages, comments, replies, webhooks, and provider error normalization. |
| [integration_auth](./integration_auth) | `hamresan-integration-auth` | Machine-to-machine authentication and authorization for services, plugins, connectors, workers, and partner applications, with signed requests, replay protection, scopes, permissions, and credential lifecycle management. |
| [notification](./notification) | `hamresan-notification` | Application-agnostic notification infrastructure with queue-first orchestration, templates, and replaceable SMS, email, and console providers. |
| [store](./store) | `hamresan-store` | Reusable Store domain and application package with async SQLAlchemy persistence, FastAPI integration, ownership rules, validation, and host-owned Alembic composition. |
| [subscription](./subscription) | `hamresan-subscription` | Subscription, plan, entitlement, trial, and usage-management capabilities that can be attached to generic host-owned subjects such as users, stores, organizations, or workspaces. |
| [persona_engine](./persona_engine) | `hamresan-persona-engine` | Persona/style initialization from account-authored text, focused on measurable writing characteristics while keeping persona separate from authoritative knowledge. |
| [letta_agent](./letta_agent) | `hamresan-letta-agent` | Reusable Letta integration that encapsulates SDK/provider details for agent creation, memory blocks, conversations, interactions, and normalized provider failures. |

## Examples

The [examples](./examples) directory contains runnable host-integration examples showing how the packages can be composed in real applications, including Identity + Notification, Identity + Store, Subscription, multi-auth, and Instagram sales-host scenarios.

## Design principles

These packages are intended to remain reusable and loosely coupled:

- host applications own composition, deployment, configuration, and application-specific business rules;
- packages communicate through narrow public contracts rather than concrete implementations;
- persistence and framework adapters are kept separate from domain/application logic where appropriate;
- external providers and infrastructure remain replaceable;
- packages should not depend on Sellora or other consuming applications unless explicitly designed as an application-specific package.

For installation instructions, public APIs, architecture details, examples, and package-specific constraints, see the README inside each package directory.
