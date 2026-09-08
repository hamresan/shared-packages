from letta_agent.identity_response import LettaIdentityResponse
from letta_agent.models import LettaIdentity


class LettaIdentityResponseMapper:
    def to_identity(self, response: LettaIdentityResponse) -> LettaIdentity:
        return LettaIdentity(
            identity_id=response.id,
            identifier_key=response.identifier_key,
            name=response.name,
        )
