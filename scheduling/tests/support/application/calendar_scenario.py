"""Compose real use cases against independent transactional test fakes."""

from dataclasses import dataclass

from scheduling.application.models import TrustedActor
from scheduling.domain.calendar import Calendar, CalendarScope
from tests.support.authorization import GrantAuthorizer
from tests.support.persistence import InMemoryCalendarStore, InMemoryCalendarUnitOfWorkFactory


@dataclass(frozen=True, slots=True)
class CalendarScenario:
    actor: TrustedActor
    store: InMemoryCalendarStore
    uow_factory: InMemoryCalendarUnitOfWorkFactory
    authorizer: GrantAuthorizer

    def grant_calendar(self, calendar: Calendar) -> None:
        self.authorizer.allow_manage(self.actor, calendar.scope, calendar.scope_id)

    def grant_scope(self, scope: CalendarScope, scope_id: str) -> None:
        self.authorizer.allow_manage(self.actor, scope, scope_id)


def build_calendar_scenario() -> CalendarScenario:
    store = InMemoryCalendarStore()
    return CalendarScenario(
        actor=TrustedActor("tenant-a", "actor-a"),
        store=store,
        uow_factory=InMemoryCalendarUnitOfWorkFactory(store),
        authorizer=GrantAuthorizer(),
    )
