from letta_agent.identity_mapper import LettaIdentityResponseMapper
from letta_agent.identity_response import LettaIdentityResponse
from letta_agent.models import LettaIdentity


def test_identity_response_mapper_maps_provider_response() -> None:
    response = LettaIdentityResponse(
        id="identity-1",
        identifier_key="business-1:customer-1",
        name="Instagram customer",
    )

    result = LettaIdentityResponseMapper().to_identity(response)

    assert result == LettaIdentity(
        identity_id="identity-1",
        identifier_key="business-1:customer-1",
        name="Instagram customer",
    )
