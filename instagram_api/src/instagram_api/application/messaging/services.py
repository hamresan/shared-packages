"""Instagram conversation and message application services."""

from instagram_api.application.contracts.connection import InstagramConnectionReader
from instagram_api.application.contracts.messaging import (
    InstagramConversationProvider,
    InstagramConversationReader,
    InstagramMessageProvider,
    InstagramMessageReader,
)
from instagram_api.domain import (
    InstagramConnectionId,
    InstagramConversation,
    InstagramConversationId,
    InstagramMessage,
    Page,
    PaginationCursor,
)

from .policy import InstagramMessagingReadPolicy


class InstagramConversationService(InstagramConversationReader):
    """Reads selected-connection conversations."""

    def __init__(
        self,
        connection_reader: InstagramConnectionReader,
        provider: InstagramConversationProvider,
        policy: InstagramMessagingReadPolicy,
    ) -> None:
        self._connection_reader = connection_reader
        self._provider = provider
        self._policy = policy

    async def list_conversations(
        self,
        connection_id: InstagramConnectionId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramConversation]:
        connection = await self._connection_reader.get_connection(connection_id)
        self._policy.validate_connection(connection)
        return await self._provider.list_conversations(connection_id, cursor)


class InstagramMessageService(InstagramMessageReader):
    """Reads selected-connection conversation messages."""

    def __init__(
        self,
        connection_reader: InstagramConnectionReader,
        provider: InstagramMessageProvider,
        policy: InstagramMessagingReadPolicy,
    ) -> None:
        self._connection_reader = connection_reader
        self._provider = provider
        self._policy = policy

    async def list_messages(
        self,
        connection_id: InstagramConnectionId,
        conversation_id: InstagramConversationId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramMessage]:
        connection = await self._connection_reader.get_connection(connection_id)
        self._policy.validate_connection(connection)
        return await self._provider.list_messages(connection_id, conversation_id, cursor)
