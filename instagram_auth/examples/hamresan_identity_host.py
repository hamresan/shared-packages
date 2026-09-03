"""Conceptual host composition with hamresan-identity kept behind host-owned adapters."""

from typing import Protocol

from instagram_auth.application import (
    InstagramAuthorizationCorrelation,
    InstagramAuthorizationGrant,
    LinkInstagramAuthorization,
    LinkInstagramAuthorizationCommand,
    PrepareInstagramHostIdentityHandoff,
)
from instagram_auth.domain import InstagramExternalIdentity


class HostUserLinker(Protocol):
    """Host-owned adapter that may delegate to hamresan-identity."""

    async def find_or_create_user(self, identity: InstagramExternalIdentity) -> str: ...


async def complete_login(
    *,
    identity: InstagramExternalIdentity,
    grant: InstagramAuthorizationGrant,
    correlation: InstagramAuthorizationCorrelation,
    user_linker: HostUserLinker,
    instagram_linker: LinkInstagramAuthorization,
) -> str:
    """Resolve the local user in the host, then persist the Instagram connection."""
    handoff = PrepareInstagramHostIdentityHandoff().execute(
        identity=identity,
        correlation=correlation,
    )
    owner_user_id = handoff.owner_user_id
    if owner_user_id is None:
        owner_user_id = await user_linker.find_or_create_user(handoff.identity)
    await instagram_linker.execute(
        LinkInstagramAuthorizationCommand(
            owner_user_id=owner_user_id,
            identity=identity,
            grant=grant,
        )
    )
    return owner_user_id
