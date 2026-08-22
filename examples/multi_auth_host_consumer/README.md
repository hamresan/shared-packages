# Multi-auth host composition example

This example shows a consuming host using both `hamresan-identity` and
`hamresan-integration-auth` without coupling either package to the other.

The host owns a small `HostActor` abstraction. Authentication-specific principals are mapped at
the host boundary:

```text
identity.public.AuthenticatedPrincipal
    -> IdentityActorMapper
    -> HostActor(kind="human")

integration_auth.IntegrationPrincipal
    -> IntegrationActorMapper
    -> HostActor(kind="integration")
```

Downstream business code depends only on `HostActor`.

The example intentionally does **not** add a dependency from `integration_auth` to `identity`, or
from `identity` to `integration_auth`. It also avoids a shared authentication abstraction inside
either reusable package; the composition belongs to the consuming application.

Integration permissions and resource scopes are copied into host-owned string facts so downstream
code does not need to import integration-auth value objects. Human principals are mapped without
inventing machine permissions or scopes.

## Run

From this directory:

```bash
python -m pip install -e ".[test]"
make check
```

When working directly from the shared-packages repository, Pytest and Pyright are configured to
resolve the sibling `identity/src` and `integration_auth/src` trees.
