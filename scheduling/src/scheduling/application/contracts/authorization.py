"""Host-owned permission checks across calendar scopes."""

from typing import Protocol

from scheduling.domain.calendar import CalendarScope

from ..models import TrustedActor


class CalendarAuthorizer(Protocol):
    async def ensure_can_read(
        self, actor: TrustedActor, scope: CalendarScope, scope_id: str
    ) -> None: ...

    async def ensure_can_manage(
        self, actor: TrustedActor, scope: CalendarScope, scope_id: str
    ) -> None: ...
