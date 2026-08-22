# hamresan-subscription

Reusable subscription, plan, entitlement, trial, and usage-management package for Python applications.

```text
Distribution: hamresan-subscription
Import:       subscription
Python:       >= 3.12
```

The package is application-agnostic. It does not depend on Identity, Store, WordPress, payment providers, or application-specific user/organization models. Consumers connect those concerns at their composition root through narrow public contracts.

## Install

After publishing the distribution:

```bash
pip install hamresan-subscription
```

For repository development:

```bash
cd subscription
make install-dev
make check
```

A complete runnable host integration is available in:

```text
examples/subscription_consumer
```

It demonstrates SQLAlchemy, Alembic, FastAPI authentication/authorization composition, trials, usage, BASE/ADDON subscriptions, paid activation/renewal, and entitlement resolution.

## Using the package in a project

A consuming project normally integrates the package in five steps:

```text
1. Install hamresan-subscription
2. Configure persistence at the composition root
3. Include subscription metadata in the host Alembic setup
4. Define the application's plans and entitlements through package APIs
5. Use application services from business workflows, jobs, payment handlers, or HTTP adapters
```

The package owns subscription rules. The host application owns authentication, authorization, billing-provider verification, database lifecycle, and the meaning of product-specific entitlement and usage keys.

### 1. Create a subject

Every subscription belongs to a generic `SubjectReference`. The subject can represent a user, store, organization, workspace, tenant, or another host-owned resource.

```python
from subscription import SubjectReference

subject = SubjectReference(
    subject_type="store",
    subject_id="store-123",
)
```

There is intentionally no foreign key from the package to the host application's Store/User/Organization tables.

### 2. Configure SQLAlchemy once at the composition root

The host owns the engine and session factory. Pass the host session factory to the package adapter instead of creating database dependencies inside business services.

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from subscription.infrastructure.persistence import (
    build_sqlalchemy_subscription_unit_of_work_factory,
)

engine = create_async_engine(DATABASE_URL)
session_factory = async_sessionmaker(engine, expire_on_commit=False)

subscription_uow_factory = build_sqlalchemy_subscription_unit_of_work_factory(
    session_factory,
)
```

Inject `subscription_uow_factory` into the subscription application services that your project uses. Keep this wiring in the application composition root/container.

### 3. Add package tables to the host Alembic configuration

The host owns Alembic revisions. The package only exposes its metadata and object-name filter.

```python
from subscription.migrations import (
    include_subscription_name,
    subscription_metadata,
)
```

Combine `subscription_metadata` with the host application's metadata in `migrations/env.py`, and use `include_subscription_name` when the host needs to filter Subscription-owned database objects. Generate and commit the actual revision in the host project.

See `examples/subscription_consumer/migrations` for the complete integration.

### 4. Define plans from the consuming project

The package does not ship fixed Free/Pro/Enterprise plans. Your project defines them through `CreatePlanService`.

A typical project defines stable plan codes and entitlement keys in its own module, then creates or synchronizes those plans during provisioning, an admin workflow, or an explicit bootstrap command.

Conceptually:

```text
Plan: starter
Type: BASE
Entitlements:
    conversations.monthly = 100
    analytics.advanced = false

Plan: pro
Type: BASE
Entitlements:
    conversations.monthly = 5000
    analytics.advanced = true

Plan: extra-conversations
Type: ADDON
Entitlements:
    conversations.monthly = 1000
```

Use typed entitlement values from the package rather than raw untyped values:

```python
from subscription import (
    BooleanEntitlementValue,
    IntegerEntitlementValue,
)

conversation_limit = IntegerEntitlementValue(5000)
advanced_analytics = BooleanEntitlementValue(True)
```

The exact `CreatePlanCommand` construction is application-specific. Use the public command and service exported by `subscription.application`; do not write directly to package tables.

### 5. Create a subscription

Use `CreateSubscriptionService` from the application layer. The host supplies the subject, selected plan, source, and other command data required by the public contract.

```python
from subscription.application import CreateSubscriptionService

create_subscription = CreateSubscriptionService(...)

# Build CreateSubscriptionCommand from your application's validated input,
# then execute it through the service.
subscription = await create_subscription.execute(command)
```

Do not instantiate repositories or SQLAlchemy sessions inside request handlers. Construct the service through dependency injection and reuse the configured package dependencies.

### 6. Start and evaluate a trial

Trials may be time-based, usage-based, recurring-usage-based, or a combination.

```python
from datetime import timedelta

from subscription import (
    TimeCondition,
    TrialCompletionMode,
    TrialPolicy,
    UsageCondition,
    UsageMetric,
    UsagePeriod,
)

trial_policy = TrialPolicy(
    completion_mode=TrialCompletionMode.ANY,
    time_condition=TimeCondition(timedelta(days=14)),
    usage_conditions=(
        UsageCondition(
            metric=UsageMetric("conversations"),
            limit=100,
            period=UsagePeriod.TRIAL,
        ),
    ),
)
```

With `ANY`, the trial finishes when the first configured condition is reached. In this example the trial ends after 14 days or after 100 conversations, whichever happens first.

Use `StartTrialService` to start the trial and `EvaluateTrialService` when the application needs to evaluate whether the configured trial conditions have been completed.

### 7. Record product usage

The package does not know what a conversation, API call, order, generated image, or another billable unit means. The consuming application reports those events.

```python
from subscription.application import RecordUsageService

record_usage = RecordUsageService(...)

# Map the host event to RecordUsageCommand and execute it.
await record_usage.execute(command)
```

For example, after a conversation is successfully created, the host can record one unit for the `conversations` metric. The host should record usage at the point where the product event is considered successful; do not couple the package directly to the feature that produced the event.

Use `GetUsageCounterService` when the application needs the current counter for a metric/window.

### 8. Resolve entitlements before enabling a feature

Use `ResolveEntitlementsService` to retrieve the grants that apply to a subject.

```python
from subscription.application import ResolveEntitlementsService

resolve_entitlements = ResolveEntitlementsService(...)

# Build the public entitlement query for the subject/key.
grants = await resolve_entitlements.execute(query)
```

A host feature can then make a product-specific decision such as:

```text
analytics.advanced == true      -> enable advanced analytics
conversations.monthly == 5000   -> enforce the project's usage policy
products.max == unlimited       -> do not apply a product-count ceiling
```

The package deliberately does not invent conflict precedence between BASE and ADDON grants with the same key. If your product allows overlapping grants, combine or prioritize them in a host-owned policy.

### 9. Handle paid subscriptions

Payment-provider code stays outside this package.

```text
Stripe / another provider
        ↓
host verifies webhook/event authenticity
        ↓
host maps the verified event to subscription identifiers
        ↓
ActivateSubscriptionService / RenewSubscriptionService
```

Only call activation or renewal after the host has successfully verified the provider event. Do not pass unverified webhook payloads directly into Subscription services.

Typical flow:

```python
from subscription.application import (
    ActivateSubscriptionService,
    RenewSubscriptionService,
)

activate_subscription = ActivateSubscriptionService(...)
renew_subscription = RenewSubscriptionService(...)

# Payment succeeded for a new subscription.
await activate_subscription.execute(activation_command)

# A later recurring payment succeeded.
await renew_subscription.execute(renewal_command)
```

The consumer example includes a `PaidSubscriptionEventHandler` showing this boundary.

### 10. Grant a subscription without payment

Subscriptions may also come from `MANUAL`, `PROMOTIONAL`, or `MIGRATED` sources. Create the subscription with the appropriate source and activate it through the normal lifecycle service.

Typical use cases:

```text
admin grants Pro for three months
marketing grants a temporary analytics add-on
an existing customer is migrated from another billing system
```

Payment is therefore one possible source of authorization to activate a subscription, not a dependency of the Subscription package.

### 11. Use BASE and ADDON subscriptions together

A subject may have at most one active/trialing BASE subscription. ADDON plans are separate subscriptions and multiple add-ons may be active concurrently.

```text
store-123
├── BASE: pro
├── ADDON: extra-conversations
└── ADDON: advanced-ai
```

This keeps add-ons independent: they can have their own lifecycle, source, expiration, and entitlements instead of being embedded into the BASE subscription.

### 12. Add the FastAPI adapter when the project needs HTTP endpoints

The FastAPI adapter is optional. The host provides authentication and authorization implementations.

```python
from subscription.presentation import (
    AuthenticatedActor,
    AuthenticatedActorDependency,
    SubscriptionAuthorizer,
    build_fastapi_subscription_adapter,
)
```

Implement `AuthenticatedActorDependency` using the host authentication package and implement `SubscriptionAuthorizer` using host-owned authorization rules. Then build the adapter at the composition root and include its router in the FastAPI application.

Do not treat a `subject_id` supplied by an HTTP client as authorization. The host authorizer must decide whether the authenticated actor may operate on that subject.

### Recommended host-project structure

The package does not require a specific application architecture, but a clean integration can look like this:

```text
app/
├── bootstrap/
│   └── subscription.py        # package wiring / DI
├── billing/
│   └── handlers/              # verified payment events -> subscription services
├── subscription_access/
│   ├── policies/              # host entitlement/precedence rules
│   └── mappers/               # host DTO/event -> package command/query
└── features/
    └── ...                    # product features consume stable host abstractions
```

Keep provider-specific billing, host authentication, and product-specific entitlement rules outside `hamresan-subscription`.

### Minimal integration checklist

Before using the package in production, verify that the host project has:

- installed `hamresan-subscription`;
- configured the SQLAlchemy UoW factory at the composition root;
- included Subscription metadata in host-owned Alembic migrations;
- defined plans and typed entitlements through package APIs;
- chosen canonical `subject_type` and `subject_id` values;
- wired authentication and authorization if the FastAPI adapter is used;
- verified payment-provider events before activation/renewal;
- mapped successful product events to usage metrics;
- defined host rules for overlapping BASE/ADDON entitlement grants;
- added integration tests for the project's real subscription flows.

For a complete executable reference, start with `examples/subscription_consumer` rather than copying internal package implementations.

## Core model

```text
SubjectReference
    │
    ├── BASE subscription (maximum one active/trialing)
    └── ADDON subscriptions (multiple allowed)
             │
             └── Plan
                  └── typed entitlements
```

Plans are database-backed and defined by the consuming application through package APIs. The package does not ship a fixed Free/Pro/Enterprise plan catalog.

## Subject references

Subscriptions belong to a generic subject:

```python
from subscription import SubjectReference

subject = SubjectReference(
    subject_type="store",
    subject_id="store-123",
)
```

`subject_type` is a canonical lowercase identifier. `subject_id` is a string and does not need to be a UUID.

Examples:

```text
("user", "123")
("store", "store-123")
("organization", "org_42")
("workspace", "workspace-a")
```

There is no FK from Subscription tables to consumer-owned User, Store, or Organization tables.

## Subscription types and sources

Supported subscription types:

```text
BASE
ADDON
```

A subject may have at most one active or trialing BASE subscription. Multiple ADDON subscriptions can be active concurrently.

Supported sources:

```text
PAID
TRIAL
MANUAL
PROMOTIONAL
MIGRATED
```

Payment processing is intentionally outside the package. A host verifies its payment-provider event and then calls Subscription application services.

## Typed entitlements

Entitlements are strongly typed:

```text
BOOLEAN
INTEGER
DECIMAL
STRING
UNLIMITED
```

Example domain values:

```python
from subscription import (
    BooleanEntitlementValue,
    IntegerEntitlementValue,
    StringEntitlementValue,
    UnlimitedEntitlementValue,
)

analytics = BooleanEntitlementValue(True)
conversation_limit = IntegerEntitlementValue(1000)
model_name = StringEntitlementValue("premium")
unlimited_products = UnlimitedEntitlementValue()
```

Typical entitlement keys are consumer-defined:

```text
analytics.advanced
conversations.monthly
team.members.max
model.default
products.max
```

The package does not invent precedence between BASE and ADDON grants with the same key. `ResolveEntitlementsService` returns matching grants and the consuming application can apply its own product rule when needed.

## Trial policies

Trials can be time-based, usage-based, recurring-usage-based, or combined.

Examples:

```text
14 days
100 conversations
14 days OR 100 conversations
50 conversations per week
```

`ANY` means the trial finishes when the first configured condition is reached. `ALL` means every configured condition must be reached.

The package does not know what `conversations`, `orders`, or `api_calls` mean. The host defines metric keys and reports usage.

## Application API

Stable application entry points are exported from `subscription.application`.

Main services:

```text
CreatePlanService
GetPlanService
ChangePlanStatusService
CreateSubscriptionService
GetSubscriptionService
StartTrialService
ActivateSubscriptionService
CancelSubscriptionService
RenewSubscriptionService
RecordUsageService
GetUsageCounterService
EvaluateTrialService
ResolveEntitlementsService
```

Consumer code should import from controlled package APIs such as:

```python
from subscription import SubjectReference
from subscription.application import CreateSubscriptionService
from subscription.infrastructure.persistence import (
    build_sqlalchemy_subscription_unit_of_work_factory,
)
from subscription.presentation import build_fastapi_subscription_adapter
```

Avoid importing internal implementation modules unless you are extending the package itself.

## SQLAlchemy integration

The host owns the SQLAlchemy engine and sessionmaker lifecycle. The package receives a host-provided async session factory.

The package never creates a global engine or global sessionmaker.

Package-owned tables:

```text
subscription_plan
subscription_plan_entitlement
subscription_subscription
subscription_trial_policy
subscription_trial_usage_condition
subscription_usage_record
```

All package tables use the `subscription_` prefix. Foreign keys are limited to Subscription-owned tables.

## Alembic integration

Alembic revision history belongs to the host application. The package exposes `subscription_metadata` and `include_subscription_name`; the host owns revision files and ordering.

See `examples/subscription_consumer/migrations` for a real host-owned setup.

## FastAPI integration

The FastAPI adapter does not import an Identity implementation. Authentication and authorization are supplied by the host.

HTTP responsibilities include:

```text
POST   /subscription/plans
GET    /subscription/plans/{plan_id}
PATCH  /subscription/plans/{plan_id}/status
POST   /subscription/subscriptions
GET    /subscription/subscriptions/{subscription_id}
POST   /subscription/subscriptions/{subscription_id}/trial
POST   /subscription/subscriptions/{subscription_id}/activate
POST   /subscription/subscriptions/{subscription_id}/cancel
POST   /subscription/subscriptions/{subscription_id}/renew
POST   /subscription/usage
GET    /subscription/usage
GET    /subscription/entitlements
```

A target subject from an HTTP request is never considered authorized merely because the caller supplied it. Host authorization is evaluated through `SubscriptionAuthorizer`.

## Paid subscription integration

Provider-specific billing remains host code. A host verifies the provider event and then calls `ActivateSubscriptionService` or `RenewSubscriptionService`.

## Manual and promotional grants

A subscription does not require a payment event. Hosts may create subscriptions with sources such as `MANUAL` or `PROMOTIONAL` and then activate them through the same lifecycle application API.

## Usage metering

Usage and entitlement limits are separate concepts.

```text
Entitlement: conversations.monthly = 1000
Usage:       conversations = 427
```

A host records generic usage events through `RecordUsageService`. The metric vocabulary remains application-owned.

## Full consumer example

Run the real integration example from repository root:

```bash
cd examples/subscription_consumer
python -m pip install -e "../../subscription"
python -m pip install -e ".[test]"
make check
```

The integration test covers BASE/ADDON plans, combined trials, usage recording, manual grants, paid activation, renewal, entitlement resolution, host authentication/authorization, and host SQLAlchemy/Alembic ownership.

## Architecture boundaries

`hamresan-subscription` owns:

- Plan, Subscription, Trial and Usage domain rules;
- typed entitlement model;
- application use cases and contracts;
- optional SQLAlchemy persistence adapter;
- migration metadata/filter helpers;
- FastAPI presentation adapter.

The consuming application owns:

- User/Store/Organization models;
- authentication implementation;
- authorization rules;
- SQLAlchemy engine/sessionmaker lifecycle;
- Alembic revision graph;
- payment provider integration and payment verification;
- product-specific metric meanings;
- product-specific entitlement conflict/precedence rules.

## Quality gate

```bash
make check
```

Runs Ruff, Ruff format check, Pyright strict, pytest with branch coverage >= 85%, and package build verification.

GitHub Actions also runs the package quality gate and the real consumer integration gate for relevant pull requests.

## Release checklist

See `RELEASE.md` before publishing a version.

## Current status

Stages 0–10 of the initial package roadmap are complete. Future work should be driven by concrete consumer requirements rather than adding provider-specific behavior to the core package.
