"""Test fakes for authorization use cases."""

from tests.application.authorization.fakes.state_store import (
    FakeInstagramAuthorizationStateStore,
)
from tests.application.authorization.fakes.url_builder import FakeInstagramAuthorizationUrlBuilder

__all__ = [
    "FakeInstagramAuthorizationStateStore",
    "FakeInstagramAuthorizationUrlBuilder",
]
