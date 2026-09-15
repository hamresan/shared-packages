import asyncio

from letta_agent.lifecycle_contracts import LettaAgentLifecycleGateway
from letta_agent.lifecycle_service import LettaAgentLifecycleService


class FakeLettaAgentLifecycleGateway(LettaAgentLifecycleGateway):
    def __init__(self) -> None:
        self.deleted_agent_ids: list[str] = []

    async def delete_agent(self, *, agent_id: str) -> None:
        self.deleted_agent_ids.append(agent_id)


def test_lifecycle_service_delegates_agent_deletion() -> None:
    gateway = FakeLettaAgentLifecycleGateway()
    service = LettaAgentLifecycleService(gateway)

    asyncio.run(service.delete_agent(agent_id="agent-1"))

    assert gateway.deleted_agent_ids == ["agent-1"]
