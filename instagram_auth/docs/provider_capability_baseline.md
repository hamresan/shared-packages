# Instagram Provider Capability Baseline

Verified against Meta's current Instagram API with Instagram Login documentation on 2026-09-03.

## Supported account types

The initial package contract supports Instagram Professional accounts only:

- Business
- Creator

Consumer/personal accounts are not eligible for this package contract.

## Login configuration

The package targets Instagram API with Instagram Login (Business Login for Instagram). The provider-facing base host for this configuration is `graph.instagram.com`.

This login configuration does not require the Instagram Professional account to be linked to a Facebook Page. Provider-specific request details remain outside the domain/application layers and will be introduced only in the roadmap stage that implements the Meta provider adapter.

## Permission baseline

The required core permission set is:

```text
instagram_business_basic
instagram_business_manage_messages
instagram_business_manage_comments
```

The optional permission registry is:

```text
instagram_business_manage_insights
instagram_business_content_publish
```

Optional permissions are never requested by default. A consuming application must explicitly select an optional permission because its feature requires that capability.

Legacy Instagram Login scope names such as `business_basic`, `business_manage_messages`, `business_manage_comments`, and `business_content_publish` are outside this package contract. Meta deprecated those legacy scope values on January 27, 2025 in favor of the `instagram_business_*` names.

## Standard Access and Advanced Access

Host applications must account for Meta access levels and App Review requirements:

- Standard Access is for professional accounts the app owner owns or manages and has added to the app in the Meta App Dashboard.
- Advanced Access is required when the application serves Instagram Professional accounts the app owner does not own or manage.
- A production host serving third-party businesses or creators must complete the relevant Meta App Review/Advanced Access requirements for the permissions it needs.

This package does not attempt to bypass or infer Meta App Review status. The host is responsible for provider application configuration and approval status.

## Normalized connection states

The initial package vocabulary is:

```text
authorizing
connected
reauthorization_required
disconnected
```

These values describe package-level authorization state and do not expose Meta-specific status payloads.

## Normalized provider error kinds

The provider-independent error vocabulary is:

```text
access_denied
invalid_request
invalid_authorization_code
invalid_token
insufficient_permissions
rate_limited
timeout
provider_unavailable
unexpected_provider_error
```

Provider adapters added in later roadmap stages must map Meta-specific failures into these categories without leaking authorization codes, access tokens, or app secrets.

## Multi-account identity and uniqueness semantics

Each Instagram authorization is an independent connection owned by a host-supplied owner identifier.

Provider account IDs are opaque strings. The persistence design must eventually enforce uniqueness for the pair:

```text
(owner_user_id, instagram_account_id)
```

This allows one local user to own multiple independent Instagram connections while preventing accidental duplicate records for the same Instagram account under the same owner.

The same Instagram account identifier under a different host owner is not treated as the same package-owned connection. Host ownership authorization remains the consuming application's responsibility.

The package has no global or implicit active Instagram connection. Operations that require a connection must remain connection-scoped once those contracts are introduced in later stages.

## Stage 0 boundaries

Stage 0 fixes provider capability semantics and public vocabulary only. It intentionally does not introduce:

- OAuth state storage or validation;
- authorization URL builders;
- Meta HTTP clients;
- authorization-code exchange;
- connection entities or repositories;
- SQLAlchemy persistence;
- FastAPI routes;
- token protection implementations.

Those concerns belong to later roadmap stages.
