"""HTTP composition, equally valid for in-memory and SQLAlchemy repositories."""

from dataclasses import dataclass

from fastapi import FastAPI

from scheduling.application.contracts import CalendarUnitOfWorkFactory
from scheduling.application.models import TrustedActor
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
from scheduling.infrastructure.api.fastapi import (
    AvailabilityHttpMapper,
    CalendarHttpDependencies,
    CalendarHttpMapper,
    create_calendar_router,
    install_calendar_error_handlers,
)
from tests.support.authorization import GrantAuthorizer

from .busy_reader import FakeBusyIntervalReader
from .clock import FixedUtcClock
from .identity import FakeActorProvider


@dataclass(slots=True)
class HttpTestHost:
    app: FastAPI
    actor_provider: FakeActorProvider
    authorizer: GrantAuthorizer
    busy_reader: FakeBusyIntervalReader


def build_http_test_host(factory: CalendarUnitOfWorkFactory) -> HttpTestHost:
    actor_provider = FakeActorProvider(TrustedActor("tenant-a", "actor-a"))
    authorizer = GrantAuthorizer()
    reader = FakeBusyIntervalReader()
    guard = CalendarMutationGuard(authorizer)
    deps = CalendarHttpDependencies(
        get_actor=actor_provider,
        clock=FixedUtcClock(),
        calendar_mapper=CalendarHttpMapper(),
        availability_mapper=AvailabilityHttpMapper(),
        create=CreateCalendar(factory, authorizer),
        get=GetCalendar(factory, authorizer),
        list_calendars=ListCalendars(factory, authorizer),
        update_schedule=UpdateWeeklySchedule(factory, guard),
        set_exception=SetDateException(factory, guard),
        remove_exception=RemoveDateException(factory, guard),
        add_block=AddBlockedPeriod(factory, guard),
        remove_block=RemoveBlockedPeriod(factory, guard),
        archive=ArchiveCalendar(factory, guard),
        availability=FindAvailability(factory, authorizer, reader),
    )
    app = FastAPI()
    install_calendar_error_handlers(app)
    app.include_router(create_calendar_router(deps))
    return HttpTestHost(app, actor_provider, authorizer, reader)
