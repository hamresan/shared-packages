"""Load and authorize an editable calendar at one expected version."""

from scheduling.domain.calendar import Calendar

from ..contracts import CalendarAuthorizer, CalendarRepository
from ..errors import CalendarNotFoundError, CalendarVersionConflictError
from ..models import TrustedActor


class CalendarMutationGuard:
    def __init__(self, authorizer: CalendarAuthorizer) -> None:
        self._authorizer = authorizer

    async def load(
        self,
        actor: TrustedActor,
        calendar_id: str,
        expected_version: int,
        repository: CalendarRepository,
    ) -> Calendar:
        calendar = await repository.get(actor.tenant_id, calendar_id)
        if calendar is None:
            raise CalendarNotFoundError("Calendar not found in the trusted tenant.")
        await self._authorizer.ensure_can_manage(actor, calendar.scope, calendar.scope_id)
        if calendar.version != expected_version:
            raise CalendarVersionConflictError("Calendar version no longer matches.")
        return calendar
