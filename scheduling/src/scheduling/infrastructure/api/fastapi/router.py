"""Thin optional FastAPI router; no authorization or persistence implementation."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from scheduling.application.models import TrustedActor
from scheduling.domain.calendar import CalendarScope

from .dependencies import CalendarHttpDependencies
from .schemas import (
    AvailabilitySchema,
    CalendarSchema,
    ChangeBlockSchema,
    CreateCalendarSchema,
    SetExceptionSchema,
    SlotSchema,
    UpdateScheduleSchema,
    VersionSchema,
)


def create_calendar_router(deps: CalendarHttpDependencies) -> APIRouter:
    router = APIRouter(prefix="/scheduling", tags=["scheduling"])

    @router.post("/calendars", response_model=CalendarSchema, status_code=201)
    async def create_calendar(
        body: CreateCalendarSchema, actor: Annotated[TrustedActor, Depends(deps.get_actor)]
    ) -> CalendarSchema:
        calendar = deps.calendar_mapper.to_domain(actor.tenant_id, body)
        return deps.calendar_mapper.to_schema(await deps.create.execute(actor, calendar))

    @router.get("/calendars", response_model=list[CalendarSchema])
    async def list_calendars(
        actor: Annotated[TrustedActor, Depends(deps.get_actor)],
        scope: CalendarScope,
        scope_id: Annotated[str, Query(min_length=1)],
    ) -> list[CalendarSchema]:
        calendars = await deps.list_calendars.execute(actor, scope, scope_id)
        return [deps.calendar_mapper.to_schema(calendar) for calendar in calendars]

    @router.get("/calendars/{calendar_id}", response_model=CalendarSchema)
    async def get_calendar(
        calendar_id: str, actor: Annotated[TrustedActor, Depends(deps.get_actor)]
    ) -> CalendarSchema:
        return deps.calendar_mapper.to_schema(await deps.get.execute(actor, calendar_id))

    @router.put("/calendars/{calendar_id}/weekly-schedule", response_model=CalendarSchema)
    async def update_schedule(
        calendar_id: str,
        body: UpdateScheduleSchema,
        actor: Annotated[TrustedActor, Depends(deps.get_actor)],
    ) -> CalendarSchema:
        result = await deps.update_schedule.execute(
            actor,
            calendar_id,
            body.expected_version,
            deps.calendar_mapper.schedule(body.weekly_schedule),
        )
        return deps.calendar_mapper.to_schema(result)

    @router.put("/calendars/{calendar_id}/exceptions", response_model=CalendarSchema)
    async def set_exception(
        calendar_id: str,
        body: SetExceptionSchema,
        actor: Annotated[TrustedActor, Depends(deps.get_actor)],
    ) -> CalendarSchema:
        result = await deps.set_exception.execute(
            actor,
            calendar_id,
            body.expected_version,
            deps.calendar_mapper.exception(body.exception),
        )
        return deps.calendar_mapper.to_schema(result)

    @router.delete("/calendars/{calendar_id}/exceptions/{day}", response_model=CalendarSchema)
    async def remove_exception(
        calendar_id: str,
        day: date,
        actor: Annotated[TrustedActor, Depends(deps.get_actor)],
        expected_version: Annotated[int, Query(ge=1)],
    ) -> CalendarSchema:
        result = await deps.remove_exception.execute(actor, calendar_id, expected_version, day)
        return deps.calendar_mapper.to_schema(result)

    @router.post("/calendars/{calendar_id}/blocked-periods", response_model=CalendarSchema)
    async def add_block(
        calendar_id: str,
        body: ChangeBlockSchema,
        actor: Annotated[TrustedActor, Depends(deps.get_actor)],
    ) -> CalendarSchema:
        result = await deps.add_block.execute(
            actor, calendar_id, body.expected_version, deps.calendar_mapper.block(body.block)
        )
        return deps.calendar_mapper.to_schema(result)

    @router.delete("/calendars/{calendar_id}/blocked-periods", response_model=CalendarSchema)
    async def remove_block(
        calendar_id: str,
        body: ChangeBlockSchema,
        actor: Annotated[TrustedActor, Depends(deps.get_actor)],
    ) -> CalendarSchema:
        result = await deps.remove_block.execute(
            actor, calendar_id, body.expected_version, deps.calendar_mapper.block(body.block)
        )
        return deps.calendar_mapper.to_schema(result)

    @router.post("/calendars/{calendar_id}/archive", response_model=CalendarSchema)
    async def archive_calendar(
        calendar_id: str,
        body: VersionSchema,
        actor: Annotated[TrustedActor, Depends(deps.get_actor)],
    ) -> CalendarSchema:
        result = await deps.archive.execute(actor, calendar_id, body.expected_version)
        return deps.calendar_mapper.to_schema(result)

    @router.post("/availability", response_model=list[SlotSchema])
    async def find_availability(
        body: AvailabilitySchema, actor: Annotated[TrustedActor, Depends(deps.get_actor)]
    ) -> list[SlotSchema]:
        lookup = deps.availability_mapper.to_lookup(body, deps.clock.now())
        slots = await deps.availability.execute(actor, lookup)
        return [deps.availability_mapper.to_schema(slot) for slot in slots]

    return router
