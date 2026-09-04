"""Opaque identifiers used by the Instagram API package."""

from typing import NewType

InstagramConnectionId = NewType("InstagramConnectionId", str)
InstagramAccountId = NewType("InstagramAccountId", str)
InstagramMediaId = NewType("InstagramMediaId", str)
InstagramConversationId = NewType("InstagramConversationId", str)
InstagramMessageId = NewType("InstagramMessageId", str)
InstagramCommentId = NewType("InstagramCommentId", str)
InstagramUserId = NewType("InstagramUserId", str)
PaginationCursor = NewType("PaginationCursor", str)
