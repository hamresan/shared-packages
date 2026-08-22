"""Executable rotation and authorization example using the package domain APIs."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from integration_auth.domain.entities.integration_credential import IntegrationCredential
from integration_auth.domain.entities.integration_principal import IntegrationPrincipal
from integration_auth.domain.enums.credential_direction import CredentialDirection
from integration_auth.domain.enums.credential_status import CredentialStatus
from integration_auth.domain.policies.credential_rotation_policy import CredentialRotationPolicy
from integration_auth.domain.policies.permission_requirement_policy import PermissionRequirementPolicy
from integration_auth.domain.policies.resource_scope_authorization_policy import (
    ResourceScopeAuthorizationPolicy,
)
from integration_auth.domain.value_objects.identifiers import (
    IntegrationClientId,
    IntegrationCredentialId,
)
from integration_auth.domain.value_objects.integration_resource import IntegrationResource
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from integration_auth.domain.value_objects.permission import Permission

VECTORS_PATH = Path(__file__).with_name("vectors.json")


def main() -> None:
    vectors = json.loads(VECTORS_PATH.read_text(encoding="utf-8"))
    rotation = vectors["rotation"]
    authorization = vectors["authorization"]
    client_id = IntegrationClientId(rotation["client_id"])
    issued_at = datetime.fromtimestamp(rotation["current_timestamp"] - 300, tz=UTC)
    existing_expiry = datetime.fromtimestamp(rotation["current_timestamp"] + 3600, tz=UTC)

    inbound = IntegrationCredential(
        credential_id=IntegrationCredentialId(rotation["inbound_credential_id"]),
        client_id=client_id,
        direction=CredentialDirection.INBOUND,
        status=CredentialStatus.ACTIVE,
        issued_at=issued_at,
        expires_at=existing_expiry,
    )
    outbound = IntegrationCredential(
        credential_id=IntegrationCredentialId(rotation["outbound_credential_id"]),
        client_id=client_id,
        direction=CredentialDirection.OUTBOUND,
        status=CredentialStatus.ACTIVE,
        issued_at=issued_at,
        expires_at=existing_expiry,
    )
    prepared = CredentialRotationPolicy().prepare_previous_credentials(
        credentials=(inbound, outbound),
        client_id=client_id,
        direction=CredentialDirection.INBOUND,
        current_timestamp=rotation["current_timestamp"],
        overlap_seconds=rotation["overlap_seconds"],
    )
    expected_expiry = datetime.fromtimestamp(rotation["current_timestamp"], tz=UTC) + timedelta(
        seconds=rotation["overlap_seconds"]
    )

    principal = IntegrationPrincipal(
        client_id=client_id,
        permissions=frozenset(Permission(value) for value in authorization["permissions"]),
        scopes=frozenset(
            IntegrationScope(*value.split(":", maxsplit=1)) for value in authorization["scopes"]
        ),
    )
    permission_policy = PermissionRequirementPolicy()
    scope_policy = ResourceScopeAuthorizationPolicy()

    results = {
        "rotation_inbound_only": len(prepared) == 1
        and prepared[0].credential_id == inbound.credential_id
        and prepared[0].expires_at == expected_expiry,
        "permission_allow": permission_policy.allows(
            principal=principal,
            permission=Permission(authorization["allowed_permission"]),
        ),
        "permission_deny": not permission_policy.allows(
            principal=principal,
            permission=Permission(authorization["denied_permission"]),
        ),
        "scope_allow": scope_policy.allows(
            principal=principal,
            resource=IntegrationResource(*authorization["allowed_resource"]),
        ),
        "scope_deny": not scope_policy.allows(
            principal=principal,
            resource=IntegrationResource(*authorization["denied_resource"]),
        ),
    }
    print(json.dumps(results, sort_keys=True))
    if not all(results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
