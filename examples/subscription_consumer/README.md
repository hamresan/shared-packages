# Subscription Consumer Example

This example shows how a host application composes `hamresan-subscription` without coupling the package to the host's authentication, authorization, payment provider, SQLAlchemy engine, or Alembic revision graph.

## What it demonstrates

- host-owned async SQLAlchemy engine/sessionmaker;
- host-owned Alembic environment using `subscription_metadata()` and `include_subscription_name()`;
- host-provided `AuthenticatedActorDependency`;
- host-provided `SubscriptionAuthorizer`;
- FastAPI adapter installation;
- database-backed BASE and ADDON plans;
- combined time + usage trial;
- generic usage recording;
- manual add-on grant;
- paid subscription activation and renewal after an external payment event;
- typed entitlement query.

## Run

From this directory:

```bash
python -m pip install -e "../../subscription"
python -m pip install -e ".[test]"
make check
```

## Composition flow

```text
Host application
├── owns SQLAlchemy engine/sessionmaker
├── owns Alembic env/revision graph
├── implements authentication
├── implements authorization
├── receives payment-provider events
└── composes hamresan-subscription
    ├── application use cases
    ├── SQLAlchemy UoW
    └── FastAPI adapter
```

The package never imports the host's user/store models or payment provider.

## Authentication and authorization

`StaticAuthenticatedActorDependency` is intentionally simple for the example. A real host can adapt JWT/session/Identity authentication to the same narrow contract.

`StoreSubscriptionAuthorizer` demonstrates host ownership of authorization rules. Subscription only asks whether an actor can manage plans or access a `SubjectReference`; it does not know host roles or ownership tables.

## Paid subscription flow

Payment processing stays outside the package:

```text
Payment provider
→ host verifies payment event
→ PaidSubscriptionEventHandler
→ ActivateSubscriptionService / RenewSubscriptionService
```

`PaidSubscriptionEventHandler` is host code. It translates a verified external payment event into Subscription application commands.

## Trial flow

The integration test creates a trial with:

```text
14 days OR 100 conversations
```

and records usage with the generic `conversations` metric. The package does not know what a conversation means.

## Base and add-on plans

The example creates:

```text
BASE: pro
ADDON: analytics-addon
```

The BASE plan grants `conversations.monthly = 1000`; the ADDON grants `analytics.advanced = true`.

## Alembic ownership

The host owns `alembic.ini`, `migrations/env.py`, and future revision files. The package only provides metadata/filter helpers. This keeps migration ordering and the revision graph under application control.
