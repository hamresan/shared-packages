from letta_agent.lifecycle_contracts import LettaAgentLifecycleGateway


class LettaAgentLifecycleService:
    def __init__(self, gateway: LettaAgentLifecycleGateway) -> None:
        self._gateway = gateway

    async def delete_agent(self, *, agent_id: str) -> None:
        await self._gateway.delete_agent(agent_id=agent_id)
