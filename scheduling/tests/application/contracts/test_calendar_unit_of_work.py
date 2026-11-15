import asyncio
from dataclasses import replace

import pytest

from scheduling.application.errors import CalendarAlreadyExistsError, CalendarVersionConflictError
from scheduling.domain.calendar import CalendarScope
from tests.support.calendar_factory import make_calendar
from tests.support.persistence import InMemoryCalendarStore, InMemoryCalendarUnitOfWorkFactory


async def test_exiting_without_commit_rolls_back_staged_create() -> None:
    store = InMemoryCalendarStore()
    factory = InMemoryCalendarUnitOfWorkFactory(store)
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")

    async with factory.create() as uow:
        await uow.calendars.add(calendar)

    assert store.records == {}


async def test_repository_lookup_by_scope_respects_tenant_id() -> None:
    store = InMemoryCalendarStore()
    factory = InMemoryCalendarUnitOfWorkFactory(store)
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")
    store.seed(calendar)
    async with factory.create() as uow:
        assert (
            await uow.calendars.get_by_scope("tenant-a", CalendarScope.RESOURCE, "resource-a")
            == calendar
        )
        assert (
            await uow.calendars.get_by_scope("tenant-b", CalendarScope.RESOURCE, "resource-a")
            is None
        )


async def test_two_concurrent_stale_writers_cannot_overwrite_each_other() -> None:
    store = InMemoryCalendarStore()
    factory = InMemoryCalendarUnitOfWorkFactory(store)
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")
    store.seed(calendar)
    first = factory.create()
    second = factory.create()

    async with first, second:
        first_read = await first.calendars.get(calendar.tenant_id, calendar.calendar_id)
        second_read = await second.calendars.get(calendar.tenant_id, calendar.calendar_id)
        assert first_read == second_read == calendar
        await first.calendars.update_if_version(replace(calendar, version=2), 1)
        await second.calendars.update_if_version(replace(calendar, version=2), 1)

        results = await asyncio.gather(first.commit(), second.commit(), return_exceptions=True)

    assert sum(result is None for result in results) == 1
    assert sum(isinstance(result, CalendarVersionConflictError) for result in results) == 1
    assert store.records[(calendar.tenant_id, calendar.calendar_id)].version == 2


async def test_commit_rejects_invalid_revision_without_changing_store() -> None:
    store = InMemoryCalendarStore()
    factory = InMemoryCalendarUnitOfWorkFactory(store)
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")
    store.seed(calendar)
    async with factory.create() as uow:
        await uow.calendars.update_if_version(replace(calendar, version=4), expected_version=1)
        with pytest.raises(CalendarVersionConflictError):
            await uow.commit()

    assert store.records[(calendar.tenant_id, calendar.calendar_id)] == calendar


async def test_two_concurrent_creates_cannot_duplicate_one_scope() -> None:
    store = InMemoryCalendarStore()
    factory = InMemoryCalendarUnitOfWorkFactory(store)
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")
    first = factory.create()
    second = factory.create()

    async with first, second:
        await first.calendars.add(calendar)
        await second.calendars.add(replace(calendar, calendar_id="another-calendar-id"))

        results = await asyncio.gather(first.commit(), second.commit(), return_exceptions=True)

    assert sum(result is None for result in results) == 1
    assert sum(isinstance(result, CalendarAlreadyExistsError) for result in results) == 1
    assert len(store.records) == 1


async def test_calendar_scope_cannot_change_during_versioned_update() -> None:
    store = InMemoryCalendarStore()
    factory = InMemoryCalendarUnitOfWorkFactory(store)
    original = make_calendar(CalendarScope.RESOURCE, "resource-a")
    store.seed(original)
    async with factory.create() as uow:
        await uow.calendars.update_if_version(
            replace(original, scope_id="resource-b", version=2), expected_version=1
        )
        with pytest.raises(ValueError, match="cannot be reassigned"):
            await uow.commit()

    assert store.records[(original.tenant_id, original.calendar_id)] == original
