"""Authorized host-data lookup for the independent advisory availability engine."""

from scheduling.application.contracts import (
    BusyIntervalReader,
    CalendarAuthorizer,
    CalendarUnitOfWorkFactory,
)
from scheduling.application.errors import CalendarNotFoundError
from scheduling.application.models import AvailabilityLookup, TrustedActor
from scheduling.domain.calendar import Calendar, CalendarScope
from scheduling.engine import AvailabilityRequest, AvailableSlot, calculate_availability


class FindAvailability:
    """Load only authorized calendars; busy data remains authoritative in the host."""

    def __init__(
        self,
        uow_factory: CalendarUnitOfWorkFactory,
        authorizer: CalendarAuthorizer,
        busy_reader: BusyIntervalReader,
    ) -> None:
        self._uow_factory = uow_factory
        self._authorizer = authorizer
        self._busy_reader = busy_reader

    async def execute(
        self, actor: TrustedActor, lookup: AvailabilityLookup
    ) -> tuple[AvailableSlot, ...]:
        identities = (
            (CalendarScope.ORGANIZATION, lookup.organization_id),
            (CalendarScope.LOCATION, lookup.location_id),
            *((CalendarScope.RESOURCE, resource_id) for resource_id in lookup.resource_ids),
        )
        for scope, scope_id in identities:
            await self._authorizer.ensure_can_read(actor, scope, scope_id)

        async with self._uow_factory.create() as unit:
            calendars: list[Calendar] = []
            for scope, scope_id in identities:
                calendar = await unit.calendars.get_by_scope(actor.tenant_id, scope, scope_id)
                if calendar is None:
                    raise CalendarNotFoundError(f"No calendar for {scope.value}: {scope_id}.")
                calendars.append(calendar)

        busy = await self._busy_reader.list_busy(
            actor.tenant_id, lookup.resource_ids, lookup.window
        )
        return calculate_availability(
            AvailabilityRequest(
                organization=calendars[0],
                location=calendars[1],
                resources=tuple(calendars[2:]),
                query_window=lookup.window,
                duration=lookup.duration,
                step=lookup.step,
                now=lookup.now,
                busy_intervals=busy,
                buffer_before=lookup.buffer_before,
                buffer_after=lookup.buffer_after,
                minimum_notice=lookup.minimum_notice,
                maximum_horizon=lookup.maximum_horizon,
            )
        )
