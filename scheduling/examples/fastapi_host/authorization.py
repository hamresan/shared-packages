"""Example host scope authorization; production hosts use their own identity service."""

from scheduling.application.models import TrustedActor
from scheduling.domain.calendar import CalendarScope


class DemoCalendarAuthorizer:
    def __init__(self, allowed: frozenset[tuple[CalendarScope, str]]) -> None:
        self._allowed = allowed

    async def ensure_can_read(
        self, actor: TrustedActor, scope: CalendarScope, scope_id: str
    ) -> None:
        if actor.tenant_id != "demo-tenant" or (scope, scope_id) not in self._allowed:
            raise PermissionError("Scope is not granted to this tenant.")

    async def ensure_can_manage(
        self, actor: TrustedActor, scope: CalendarScope, scope_id: str
    ) -> None:
        await self.ensure_can_read(actor, scope, scope_id)
