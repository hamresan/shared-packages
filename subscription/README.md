# hamresan-subscription

Reusable subscription, plan, entitlement, trial, and usage-management package for Python applications.

The repository folder is `subscription`, the Python import package will be `subscription`, and the installable distribution will be `hamresan-subscription`.

The package is intentionally application-agnostic. It does not depend on WordPress, Sellora, Store, Identity, payment providers, or any other concrete application. Consumers define their own plans and connect subscriptions to their own subjects through public contracts and composition-root wiring.

## Intended installation

Once released:

```bash
pip install hamresan-subscription
```

For local development:

```bash
make install-dev
make check
```

## Core concepts

The package is designed around:

```text
Plan
Subscription
Entitlement
TrialPolicy
UsageMetric / Usage
SubjectReference
```

A consuming application stores and manages its own plans through the package. Different applications can define different plan sets without changing package source code.

Example:

```text
Application A
- free
- pro
- business

Application B
- starter
- growth
- enterprise
```

## Subscription types

A subject may have one active base-plan subscription at a time.

```text
Subject
  ↓
Active BASE subscription
```

Additional capabilities are modeled as independent add-on subscriptions:

```text
Subject
├── BASE: pro
├── ADDON: whatsapp
└── ADDON: advanced_analytics
```

The package distinguishes at least:

```text
BASE
ADDON
```

The one-active-base-plan rule is a domain policy. Multiple add-on subscriptions may be active concurrently.

## Subject references

The package remains independent of User, Store, Organization, Workspace, Tenant, or any other owning domain.

A consumer supplies a generic subject reference, conceptually:

```text
subject_type
subject_id
```

Examples:

```text
("user", user_id)
("store", store_id)
("organization", organization_id)
("workspace", workspace_id)
```

No foreign key to another package's tables is required. Cross-package relationships are application-level references owned by the host.

## Defining plans in a project

Plans are database-backed entities owned by this package. A consumer creates and manages the plans it needs through package application services or HTTP adapters.

Conceptually:

```python
plan = await plan_creator.create(
    code="pro",
    name="Pro",
    subscription_type="BASE",
    entitlements=[
        BooleanEntitlement("analytics.advanced", True),
        IntegerEntitlement("team.members.max", 5),
        IntegerEntitlement("conversations.monthly", 1000),
    ],
)
```

The exact public API will be finalized during implementation, but defining plans must never require editing package code.

## Typed entitlements

Entitlements represent what a plan or subscription grants.

Planned value types:

```text
BOOLEAN
INTEGER
DECIMAL
STRING
UNLIMITED
```

Examples:

```text
analytics.advanced = true
team.members.max = 5
conversations.monthly = 1000
storage.gb = 20
model.default = "premium"
products.max = unlimited
```

Typical consumer usage:

```python
if await entitlement_checker.can_use(subject, "analytics.advanced"):
    ...

member_limit = await entitlement_checker.get_limit(subject, "team.members.max")
model_name = await entitlement_checker.get_value(subject, "model.default")
```

Consumers should depend on entitlement-checking contracts, not on Subscription persistence.

## Usage metering

Entitlement and actual usage are separate concepts.

```text
Entitlement:
conversations.monthly = 1000

Current usage:
conversations.monthly = 427

Remaining:
573
```

The package does not know what a conversation, AI message, order, or API request is. The consumer reports usage using generic metric keys.

Examples:

```text
conversations
ai_messages
orders
api_calls
storage_bytes
```

Conceptually:

```python
await usage_recorder.record(
    subject=subject,
    metric="conversations",
    amount=1,
)
```

## Trial subscriptions

Trials are first-class and may be time-based, usage-based, or both.

Time-only example:

```text
14 days
```

Usage-only example:

```text
100 conversations
```

Combined example:

```text
14 days OR 100 conversations
whichever happens first
```

Recurring usage trial example:

```text
50 conversations per week
```

Trial completion rules must be modeled as dedicated policies/conditions rather than scattered fields on `Subscription`.

Conceptually:

```text
TrialPolicy
├── TimeCondition
├── UsageCondition
└── CompletionMode: ANY | ALL
```

The package remains metric-agnostic. The host records usage; the trial evaluator determines whether the trial remains valid.

## Subscription source

A subscription does not need to come from a payment.

Planned source types include:

```text
PAID
TRIAL
MANUAL
PROMOTIONAL
MIGRATED
```

Examples:

```text
Payment succeeded
→ activate subscription with source=PAID
```

```text
Admin grants Pro for three months
→ activate subscription with source=MANUAL
```

```text
Marketing promotion
→ activate subscription with source=PROMOTIONAL
```

Payment processing is intentionally outside this package. Stripe or any other payment provider may call Subscription application services after successful payment, but payment-provider code does not belong in the Subscription core.

## Working with other Hamresan packages

`hamresan-subscription` should not hard-depend on `hamresan-identity`, `hamresan-store`, or `hamresan-notification`.

A consuming application may connect them in its composition root.

Example with Store:

```text
Authenticated user
      ↓
Store
      ↓
SubjectReference("store", store.id)
      ↓
EntitlementChecker
```

Example capability check:

```python
subject = SubjectReference(type="store", id=store.id)

if not await entitlement_checker.can_use(subject, "analytics.advanced"):
    raise FeatureNotAvailableError()
```

Other reusable packages should depend only on narrow Subscription contracts when integration is genuinely required.

## Planned public responsibilities

The package is expected to expose stable contracts around four responsibilities:

```text
Plan Management
Subscription Lifecycle
Entitlement Evaluation
Usage Metering
```

Likely use-case contracts include:

```text
PlanCreator
PlanReader
PlanUpdater

SubscriptionCreator
SubscriptionActivator
SubscriptionReader
SubscriptionCanceller
SubscriptionRenewer

SubscriptionValidityChecker
EntitlementChecker

UsageRecorder
UsageReader
TrialEvaluator
```

Names may evolve while the domain is implemented, but these responsibilities should remain separated.

## Package structure

The package follows Clean Architecture and keeps responsibilities explicit:

```text
subscription/
├── src/
│   └── subscription/
│       ├── domain/
│       │   ├── entities/
│       │   ├── enums/
│       │   ├── value_objects/
│       │   ├── policies/
│       │   └── services/
│       ├── application/
│       │   ├── contracts/
│       │   ├── dto/
│       │   ├── services/
│       │   ├── validators/
│       │   └── mappers/
│       ├── infrastructure/
│       │   └── persistence/
│       │       └── sqlalchemy/
│       ├── presentation/
│       │   ├── dependencies/
│       │   ├── errors/
│       │   ├── mappers/
│       │   ├── routes/
│       │   └── schemas/
│       └── migrations/
├── tests/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   ├── presentation/
│   ├── migrations/
│   └── support/
├── pyproject.toml
├── Makefile
├── README.md
└── ROADMAP.md
```

Test folders mirror package responsibilities. Independent Fakes, Builders, Factories, fixtures, and test helpers belong in dedicated support files rather than inside test methods.

## Architecture rules

- Clean Architecture and SOLID are mandatory.
- Domain and application layers are framework-independent.
- Services are thin workflow/use-case orchestrators.
- Mapping, validation, policies, calculations, persistence, and provider integration live in dedicated components.
- No service-locator pattern.
- Dependencies are injected through explicit contracts/interfaces.
- No direct dependency on payment providers or other Hamresan packages.
- Persistence is async and host-provided session infrastructure is preferred.
- Alembic revision history remains host-owned.
- Package-owned tables will use the `subscription_` prefix.
- Public imports should come from controlled package APIs rather than deep internal module paths.

## Quality expectations

The package foundation is expected to preserve the repository quality standard:

```text
Ruff
Ruff format --check
Pyright strict
pytest
branch coverage >= 85%
```

The implementation roadmap is tracked in `ROADMAP.md`.
