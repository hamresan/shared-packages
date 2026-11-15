"""Consumer-owned FastAPI composition using a file-backed SQLAlchemy database."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from scheduling.application.policies import CalendarMutationGuard
from scheduling.application.use_cases import (
    AddBlockedPeriod,
    ArchiveCalendar,
    CreateCalendar,
    FindAvailability,
    GetCalendar,
    ListCalendars,
    RemoveBlockedPeriod,
    RemoveDateException,
    SetDateException,
    UpdateWeeklySchedule,
)
from scheduling.domain.calendar import CalendarScope
from scheduling.infrastructure.api.fastapi import (
    AvailabilityHttpMapper,
    CalendarHttpDependencies,
    CalendarHttpMapper,
    create_calendar_router,
    install_calendar_error_handlers,
)
from scheduling.infrastructure.persistence.sqlalchemy import (
    CalendarPersistenceMapper,
    SqlAlchemyCalendarRepositoryFactory,
    SqlAlchemyCalendarUnitOfWorkFactory,
    scheduling_metadata,
)

from .authorization import DemoCalendarAuthorizer
from .busy_reader import DemoBusyIntervalReader
from .clock import SystemUtcClock
from .identity import authenticated_demo_actor


def create_app() -> FastAPI:
    secret = os.environ.get("SCHEDULING_DEMO_API_KEY")
    if not secret:
        raise RuntimeError("Set SCHEDULING_DEMO_API_KEY before starting the demo host.")
    database_url = os.getenv("SCHEDULING_DEMO_DB_URL", "sqlite+aiosqlite:///./demo_scheduling.db")
    engine = create_async_engine(database_url)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    unit_factory = SqlAlchemyCalendarUnitOfWorkFactory(
        sessions, SqlAlchemyCalendarRepositoryFactory(CalendarPersistenceMapper())
    )
    allowed = frozenset(
        {
            (CalendarScope.ORGANIZATION, "org-1"),
            (CalendarScope.LOCATION, "location-1"),
            (CalendarScope.LOCATION, "location-2"),
            (CalendarScope.RESOURCE, "resource-1"),
            (CalendarScope.RESOURCE, "resource-2"),
        }
    )
    authorizer = DemoCalendarAuthorizer(allowed)
    guard = CalendarMutationGuard(authorizer)
    dependencies = CalendarHttpDependencies(
        get_actor=authenticated_demo_actor(secret),
        clock=SystemUtcClock(),
        calendar_mapper=CalendarHttpMapper(),
        availability_mapper=AvailabilityHttpMapper(),
        create=CreateCalendar(unit_factory, authorizer),
        get=GetCalendar(unit_factory, authorizer),
        list_calendars=ListCalendars(unit_factory, authorizer),
        update_schedule=UpdateWeeklySchedule(unit_factory, guard),
        set_exception=SetDateException(unit_factory, guard),
        remove_exception=RemoveDateException(unit_factory, guard),
        add_block=AddBlockedPeriod(unit_factory, guard),
        remove_block=RemoveBlockedPeriod(unit_factory, guard),
        archive=ArchiveCalendar(unit_factory, guard),
        availability=FindAvailability(unit_factory, authorizer, DemoBusyIntervalReader()),
    )

    @asynccontextmanager
    async def lifespan(_application: FastAPI) -> AsyncIterator[None]:
        async with engine.begin() as connection:
            await connection.run_sync(scheduling_metadata().create_all)
        yield
        await engine.dispose()

    application = FastAPI(lifespan=lifespan)
    install_calendar_error_handlers(application)
    application.include_router(create_calendar_router(dependencies))
    return application
