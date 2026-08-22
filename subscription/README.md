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

Example domain policy:

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

Infrastructure-facing contracts:

```text
Clock
IdentifierGenerator
PlanRepository
SubscriptionRepository
UsageRepository
SubscriptionUnitOfWork
SubscriptionUnitOfWorkFactory
```

Commands/queries include:

```text
CreatePlanCommand
CreateSubscriptionCommand
ActivateSubscriptionCommand
RenewSubscriptionCommand
RecordUsageCommand
GetUsageCounterQuery
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

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from subscription.infrastructure.persistence import (
    build_sqlalchemy_subscription_unit_of_work_factory,
)

engine = create_async_engine(DATABASE_URL)
session_factory = async_sessionmaker(engine, expire_on_commit=False)

unit_of_work_factory = build_sqlalchemy_subscription_unit_of_work_factory(
    session_factory,
)
```

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

Subscription and usage timestamps use a dedicated UTC SQLAlchemy type. Naive datetime writes are rejected and hydrated values remain timezone-aware across supported dialect behavior.

## Alembic integration

Alembic revision history belongs to the host application.

The package exposes:

```python
from subscription.migrations import (
    include_subscription_name,
    subscription_metadata,
)
```

A host can include Subscription metadata in its own Alembic environment and use `include_subscription_name()` when filtering package-owned objects.

The package does **not** own:

```text
alembic.ini
migrations/env.py
revision files
revision ordering
revision graph
```

See `examples/subscription_consumer/migrations` for a real host-owned setup.

## FastAPI integration

The FastAPI adapter does not import an Identity implementation. Authentication and authorization are supplied by the host.

Public presentation contracts:

```python
from subscription.presentation import (
    AuthenticatedActor,
    AuthenticatedActorDependency,
    SubscriptionAuthorizer,
    build_fastapi_subscription_adapter,
)
```

The host implements `AuthenticatedActorDependency` and `SubscriptionAuthorizer`, composes the adapter, and installs its router into the host FastAPI application.

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

Provider-specific billing remains host code:

```text
Stripe / payment provider
        ↓
host verifies event
        ↓
host maps verified event
        ↓
ActivateSubscriptionService / RenewSubscriptionService
```

The consumer example contains `PaidSubscriptionEventHandler` to demonstrate this boundary. It is intentionally not part of `hamresan-subscription`.

## Manual and promotional grants

A subscription does not require a payment event. Hosts may create subscriptions with sources such as `MANUAL` or `PROMOTIONAL` and then activate them through the same lifecycle application API.

This supports scenarios such as:

```text
admin grants Pro for three months
marketing grants temporary analytics add-on
migration imports an existing entitlement
```

## Usage metering

Usage and entitlement limits are separate concepts.

```text
Entitlement: conversations.monthly = 1000
Usage:       conversations = 427
```

A host records generic usage events through `RecordUsageService`. Period-specific counters are resolved by the package's usage repository/window components.

The metric vocabulary remains application-owned.

## Full consumer example

Run the real integration example from repository root:

```bash
cd examples/subscription_consumer
python -m pip install -e "../../subscription"
python -m pip install -e ".[test]"
make check
```

The integration test covers:

```text
BASE plan
ADDON plan
combined time + usage trial
usage recording
manual add-on grant
external paid activation
renewal
entitlement resolution
host authentication/authorization
host SQLAlchemy/Alembic ownership
```

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

Runs:

```text
Ruff
Ruff format --check
Pyright strict
pytest with branch coverage >= 85%
package build (wheel + sdist)
```

GitHub Actions also runs the package quality gate and the real consumer integration gate for relevant pull requests.

## Release checklist

See `RELEASE.md` before publishing a version.

The checklist includes versioning, package build verification, consumer integration validation, public API review, migration ownership verification, and release artifact checks.

## Current status

Stages 0–10 of the initial package roadmap are complete once the release-readiness changes in this stage are merged. Future work should be driven by concrete consumer requirements rather than adding provider-specific behavior to the core package.
