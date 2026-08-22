from datetime import UTC, datetime
from uuid import UUID, uuid4

from subscription.application import Clock, IdentifierGenerator


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(UTC)


class UuidIdentifierGenerator(IdentifierGenerator):
    def new_id(self) -> UUID:
        return uuid4()
