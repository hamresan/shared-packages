from letta_client import APIError, APIStatusError, AsyncLetta

from letta_agent.errors import LettaProviderError
from letta_agent.lifecycle_contracts import LettaAgentLifecycleGateway


class SdkLettaAgentLifecycleGateway(LettaAgentLifecycleGateway):
    def __init__(self, client: AsyncLetta) -> None:
        self._client = client

    async def delete_agent(self, *, agent_id: str) -> None:
        try:
            await self._client.agents.delete(agent_id)
        except APIStatusError as error:
            if error.status_code == 404:
                return
            raise LettaProviderError("Letta agent deletion failed") from error
        except APIError as error:
            raise LettaProviderError("Letta agent deletion failed") from error
