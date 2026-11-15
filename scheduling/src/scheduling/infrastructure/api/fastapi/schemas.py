"""Explicit boundary schemas; clients never supply tenant identity."""

from datetime import date, datetime, time

from pydantic import BaseModel, Field

from scheduling.domain.calendar import CalendarScope


class WindowSchema(BaseModel):
    start: time
    end: time


class DaySchema(BaseModel):
    weekday: int = Field(ge=0, le=6)
    windows: list[WindowSchema]


class ScheduleSchema(BaseModel):
    days: list[DaySchema] = Field(default_factory=lambda: list[DaySchema]())


class ExceptionSchema(BaseModel):
    day: date
    closed: bool = False
    override_windows: list[WindowSchema] | None = None


class ClosureSchema(BaseModel):
    month: int
    day: int


class BlockSchema(BaseModel):
    start: datetime
    end: datetime
    reason: str | None = None


class CreateCalendarSchema(BaseModel):
    calendar_id: str = Field(min_length=1)
    scope: CalendarScope
    scope_id: str = Field(min_length=1)
    timezone: str = Field(min_length=1)
    weekly_schedule: ScheduleSchema
    exceptions: list[ExceptionSchema] = Field(default_factory=lambda: list[ExceptionSchema]())
    annual_closures: list[ClosureSchema] = Field(default_factory=lambda: list[ClosureSchema]())
    blocked_periods: list[BlockSchema] = Field(default_factory=lambda: list[BlockSchema]())


class CalendarSchema(CreateCalendarSchema):
    tenant_id: str
    version: int
    archived: bool


class UpdateScheduleSchema(BaseModel):
    expected_version: int = Field(ge=1)
    weekly_schedule: ScheduleSchema


class SetExceptionSchema(BaseModel):
    expected_version: int = Field(ge=1)
    exception: ExceptionSchema


class ChangeBlockSchema(BaseModel):
    expected_version: int = Field(ge=1)
    block: BlockSchema


class VersionSchema(BaseModel):
    expected_version: int = Field(ge=1)


class AvailabilitySchema(BaseModel):
    organization_id: str = Field(min_length=1)
    location_id: str = Field(min_length=1)
    resource_ids: list[str] = Field(min_length=1)
    start: datetime
    end: datetime
    duration_minutes: int = Field(ge=1)
    step_minutes: int = Field(ge=1)
    buffer_before_minutes: int = Field(default=0, ge=0)
    buffer_after_minutes: int = Field(default=0, ge=0)
    minimum_notice_minutes: int = Field(default=0, ge=0)
    maximum_horizon_days: int = Field(default=31, ge=1, le=31)


class SlotSchema(BaseModel):
    resource_id: str
    start: datetime
    end: datetime
