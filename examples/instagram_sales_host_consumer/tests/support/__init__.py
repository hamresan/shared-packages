"""Reusable support fakes for the reference integration test."""

from .instagram_api import (
    FakeAccountProvider,
    FakeMediaProvider,
    RecordingCommentReplyProvider,
    RecordingMessageProvider,
)
from .instagram_auth import (
    FakeAuthAccessTokenProvider,
    FakeAuthConnectionReader,
)

__all__ = [
    "FakeAccountProvider",
    "FakeAuthAccessTokenProvider",
    "FakeAuthConnectionReader",
    "FakeMediaProvider",
    "RecordingCommentReplyProvider",
    "RecordingMessageProvider",
]
