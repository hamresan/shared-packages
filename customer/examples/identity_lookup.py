"""Host-injected example: exact read-only provider identity lookup."""

from customer import (
    CustomerActor,
    CustomerModule,
    CustomerResolution,
    ExternalIdentityKey,
    FindExternalIdentityQuery,
)


async def resolve_verified_identity(
    module: CustomerModule,
    actor: CustomerActor,
    provider: str,
    channel_account_id: str,
    external_user_id: str,
) -> CustomerResolution | None:
    """The host must authenticate the provider assertion before calling."""
    return await module.external_identities.find.execute(
        FindExternalIdentityQuery(
            actor=actor,
            key=ExternalIdentityKey(
                actor.business_id,
                provider,
                channel_account_id,
                external_user_id,
            ),
        )
    )
