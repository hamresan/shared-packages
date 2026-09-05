from letta_client import AsyncLetta

from letta_agent.sdk_gateway import SdkLettaGateway
from letta_agent.service import LettaAgentService


class LettaAgentServiceFactory:
    def build(
        self,
        *,
        api_key: str | None,
        base_url: str | None,
    ) -> LettaAgentService:
        client = AsyncLetta(
            api_key=api_key,
            base_url=base_url,
        )
        return LettaAgentService(SdkLettaGateway(client))
