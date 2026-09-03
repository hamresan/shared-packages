"""Host-linking test fakes."""

from .security import FakeInstagramAccessTokenProtector, FixedInstagramConnectionIdGenerator
from .unit_of_work import FakeInstagramAuthUnitOfWork

__all__ = [
    "FakeInstagramAccessTokenProtector",
    "FakeInstagramAuthUnitOfWork",
    "FixedInstagramConnectionIdGenerator",
]
