"""Instagram public and private comment reply services."""

from instagram_api.application.contracts.comments import (
    InstagramPrivateCommentReplier,
    InstagramPrivateCommentReplyProvider,
    InstagramPublicCommentReplier,
    InstagramPublicCommentReplyProvider,
)
from instagram_api.application.contracts.connection import InstagramConnectionReader
from instagram_api.domain import (
    InstagramCommentId,
    InstagramCommentReplyResult,
    InstagramConnectionId,
    InstagramPrivateCommentReplyRequest,
    InstagramPrivateCommentReplyResult,
)

from .reply_policy import (
    InstagramCommentReplyAccessPolicy,
    InstagramCommentReplyTextPolicy,
    InstagramPrivateReplyEligibilityPolicy,
)


class InstagramPublicCommentReplyService(InstagramPublicCommentReplier):
    """Publishes public replies through the selected Instagram connection."""

    def __init__(
        self,
        connection_reader: InstagramConnectionReader,
        provider: InstagramPublicCommentReplyProvider,
        access_policy: InstagramCommentReplyAccessPolicy,
        text_policy: InstagramCommentReplyTextPolicy,
    ) -> None:
        self._connection_reader = connection_reader
        self._provider = provider
        self._access_policy = access_policy
        self._text_policy = text_policy

    async def reply_publicly(
        self,
        connection_id: InstagramConnectionId,
        comment_id: InstagramCommentId,
        text: str,
    ) -> InstagramCommentReplyResult:
        connection = await self._connection_reader.get_connection(connection_id)
        self._access_policy.validate_connection(connection)
        self._text_policy.validate(text)
        return await self._provider.reply(connection_id, comment_id, text)


class InstagramPrivateCommentReplyService(InstagramPrivateCommentReplier):
    """Publishes private replies only when explicit eligibility checks pass."""

    def __init__(
        self,
        connection_reader: InstagramConnectionReader,
        provider: InstagramPrivateCommentReplyProvider,
        access_policy: InstagramCommentReplyAccessPolicy,
        text_policy: InstagramCommentReplyTextPolicy,
        eligibility_policy: InstagramPrivateReplyEligibilityPolicy,
    ) -> None:
        self._connection_reader = connection_reader
        self._provider = provider
        self._access_policy = access_policy
        self._text_policy = text_policy
        self._eligibility_policy = eligibility_policy

    async def reply_privately(
        self,
        connection_id: InstagramConnectionId,
        request: InstagramPrivateCommentReplyRequest,
    ) -> InstagramPrivateCommentReplyResult:
        connection = await self._connection_reader.get_connection(connection_id)
        self._access_policy.validate_connection(connection)
        self._text_policy.validate(request.text)
        self._eligibility_policy.validate(request)
        return await self._provider.reply(connection_id, request)
