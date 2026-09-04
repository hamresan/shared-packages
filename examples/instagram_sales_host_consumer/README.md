# Instagram sales host consumer example

This Stage 14 reference consumer demonstrates host composition across:

```text
hamresan-identity
hamresan-instagram-auth
hamresan-instagram-api
FastAPI
host-owned SQLAlchemy/Alembic
host-owned automation
```

It intentionally does not create dependencies between the reusable packages.

## Package boundaries

`hamresan-instagram-auth` owns Instagram authorization, connection state, permissions, and
credentials. The host consumes only its public `InstagramConnectionReader` and
`InstagramAccessTokenProvider` contracts.

`hamresan-instagram-api` owns connection-aware profile/media reads, messaging/comment actions, and
webhook contracts. The host adapters implement API-owned connection/token contracts by delegating
to the auth package's public contracts.

`hamresan-identity` remains independent. The reference host receives an
`AuthenticatedPrincipal` and stores only its user ID in host-owned association data.

The host owns this mapping:

```text
local user ID
    -> Instagram connection ID
    -> provider Instagram account ID
```

The host does not read auth persistence tables and does not share SQLAlchemy models with either
reusable package.

## Two-account scenario

The integration test represents the output of two successful Instagram authorization flows:

```text
one identity principal
  ├── connection A -> Instagram account A
  └── connection B -> Instagram account B
```

It verifies that both independent connections are linked to the same local user, selected account
and media reads stay isolated, token lookup is keyed by the selected connection, and webhook replies
use the same resolved connection for both DM and comment events.

The webhook path uses the real `InstagramWebhookProcessor`. Outbound DM and comment paths use the
real `InstagramMessageSendService` and `InstagramPublicCommentReplyService`. Only
provider/network boundaries are faked.

OAuth itself is not duplicated in this example. `hamresan-instagram-auth` already owns and tests
that flow; this consumer begins from its public authorized-connection boundary.

## Host-owned SQLAlchemy and Alembic

The example owns only `host_instagram_connection_links`. It imports no persistence model from
`instagram_auth`, `instagram_api`, or `identity`.

`get_host_alembic_target_metadata()` exposes the host metadata that a consuming application's
Alembic `env.py` can include in its own migration composition. The host owns revision files and
migration ordering.

For tests, `HostSchema.create()` is a lightweight schema bootstrap only.

## FastAPI

`create_reference_router()` demonstrates a thin host route that requires an explicit connection ID:

```text
GET /instagram/connections/{connection_id}/account
```

There is no implicit or global active Instagram account.

## Run

From this directory:

```bash
python -m pip install -e ".[test]"
make check
```

When running directly from this repository, Pytest and Pyright resolve the sibling package source
trees through the configured paths.
