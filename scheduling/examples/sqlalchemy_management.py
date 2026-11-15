"""Host-owned SQLAlchemy composition for calendar management (demo database only)."""

import asyncio
from datetime import time

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from scheduling.application.models import TrustedActor
from scheduling.application.policies import CalendarMutationGuard
from scheduling.application.use_cases import CreateCalendar, GetCalendar, UpdateWeeklySchedule
from scheduling.domain.calendar import (
    Calendar,
    CalendarScope,
    DaySchedule,
    WeeklySchedule,
    WorkingWindow,
)
from scheduling.domain.time import IanaTimeZone
from scheduling.infrastructure.persistence.sqlalchemy import (
    CalendarPersistenceMapper,
    SqlAlchemyCalendarRepositoryFactory,
    SqlAlchemyCalendarUnitOfWorkFactory,
    scheduling_metadata,
)


class DemoCalendarAuthorizer:
    """Only the demo resource is authorized; production hosts verify real ownership."""

    async def ensure_can_read(
        self, actor: TrustedActor, scope: CalendarScope, scope_id: str
    ) -> None:
        if (actor.tenant_id, scope, scope_id) != (
            "demo-tenant",
            CalendarScope.RESOURCE,
            "resource-1",
        ):
            raise PermissionError("Not authorized for this calendar.")

    async def ensure_can_manage(
        self, actor: TrustedActor, scope: CalendarScope, scope_id: str
    ) -> None:
        await self.ensure_can_read(actor, scope, scope_id)


async def run_demo() -> Calendar:
    """Create, update and read a calendar through real SQLAlchemy transactions."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    try:
        async with engine.begin() as connection:
            await connection.run_sync(scheduling_metadata().create_all)

        sessions = async_sessionmaker(engine, expire_on_commit=False)
        unit_factory = SqlAlchemyCalendarUnitOfWorkFactory(
            sessions, SqlAlchemyCalendarRepositoryFactory(CalendarPersistenceMapper())
        )
        authorizer = DemoCalendarAuthorizer()
        actor = TrustedActor(tenant_id="demo-tenant", actor_id="demo-user")
        initial = Calendar(
            calendar_id="resource-calendar-1",
            tenant_id=actor.tenant_id,
            scope=CalendarScope.RESOURCE,
            scope_id="resource-1",
            timezone=IanaTimeZone("Asia/Muscat"),
            weekly_schedule=WeeklySchedule(
                (DaySchedule(0, (WorkingWindow(time(9), time(12)),)),)
            ),
        )

        await CreateCalendar(unit_factory, authorizer).execute(actor, initial)
        revised_schedule = WeeklySchedule(
            (DaySchedule(0, (WorkingWindow(time(10), time(14)),)),)
        )
        await UpdateWeeklySchedule(unit_factory, CalendarMutationGuard(authorizer)).execute(
            actor, initial.calendar_id, expected_version=1, schedule=revised_schedule
        )
        return await GetCalendar(unit_factory, authorizer).execute(actor, initial.calendar_id)
    finally:
        await engine.dispose()


def main() -> None:
    calendar = asyncio.run(run_demo())
    print(calendar.calendar_id, calendar.version, calendar.weekly_schedule.days)


if __name__ == "__main__":
    main()
