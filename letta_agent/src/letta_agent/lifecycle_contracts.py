from typing import Protocol


class LettaAgentLifecycleGateway(Protocol):
    async def delete_agent(self, *, agent_id: str) -> None: ...
