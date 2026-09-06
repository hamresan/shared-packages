from letta_client import APIError, APIStatusError, AsyncLetta

from letta_agent.contracts import LettaGateway
from letta_agent.errors import LettaProviderError
from letta_agent.interaction_mapper import LettaInteractionResponseMapper
from letta_agent.models import (
    LettaAgentSpec,
    LettaCreatedAgent,
    LettaCreatedConversation,
    LettaInteractionResult,
    LettaKnowledgeResult,
)


class SdkLettaGateway(LettaGateway):
    _knowledge_label = "account_knowledge"

    def __init__(self, client: AsyncLetta) -> None:
        self._client = client
        self._interaction_mapper = LettaInteractionResponseMapper()

    async def create_agent(self, spec: LettaAgentSpec) -> LettaCreatedAgent:
        try:
            agent = await self._client.agents.create(
                name=spec.name,
                model=spec.model,
                memory_blocks=[
                    {
                        "label": "persona",
                        "value": spec.persona,
                    }
                ],
            )
        except APIError as error:
            raise LettaProviderError("Letta agent creation failed") from error

        return LettaCreatedAgent(agent_id=agent.id)

    async def create_conversation(
        self,
        *,
        agent_id: str,
    ) -> LettaCreatedConversation:
        try:
            conversation = await self._client.conversations.create(
                agent_id=agent_id,
            )
        except APIError as error:
            raise LettaProviderError(
                "Letta conversation creation failed"
            ) from error

        return LettaCreatedConversation(
            conversation_id=conversation.id,
        )

    async def set_knowledge(
        self,
        *,
        agent_id: str,
        value: str,
    ) -> LettaKnowledgeResult:
        try:
            await self._client.agents.blocks.retrieve(
                self._knowledge_label,
                agent_id=agent_id,
            )
        except APIStatusError as error:
            if error.status_code != 404:
                raise LettaProviderError("Letta knowledge lookup failed") from error
        except APIError as error:
            raise LettaProviderError("Letta knowledge lookup failed") from error
        else:
            try:
                updated = await self._client.agents.blocks.update(
                    self._knowledge_label,
                    agent_id=agent_id,
                    value=value,
                    read_only=True,
                )
            except APIError as error:
                raise LettaProviderError("Letta knowledge update failed") from error
            return LettaKnowledgeResult(block_id=updated.id)

        try:
            created = await self._client.blocks.create(
                label=self._knowledge_label,
                value=value,
                read_only=True,
            )
            await self._client.agents.blocks.attach(
                created.id,
                agent_id=agent_id,
            )
        except APIError as error:
            raise LettaProviderError("Letta knowledge creation failed") from error

        return LettaKnowledgeResult(block_id=created.id)

    async def interact(
        self,
        *,
        agent_id: str,
        message: str,
    ) -> LettaInteractionResult:
        try:
            response = await self._client.agents.messages.create(
                agent_id=agent_id,
                input=message,
            )
        except APIError as error:
            raise LettaProviderError("Letta agent interaction failed") from error

        return self._interaction_mapper.to_result(response)

    async def interact_in_conversation(
        self,
        *,
        agent_id: str,
        conversation_id: str,
        message: str,
    ) -> LettaInteractionResult:
        try:
            response = await self._client.conversations.messages.create(
                conversation_id,
                agent_id=agent_id,
                input=message,
                streaming=False,
            )
        except APIError as error:
            raise LettaProviderError(
                "Letta conversation interaction failed"
            ) from error

        return self._interaction_mapper.to_result(response)
