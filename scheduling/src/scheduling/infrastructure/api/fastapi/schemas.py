"""Explicit boundary schemas; clients never supply tenant identity."""

from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field

from scheduling.domain.calendar import CalendarScope


class StrictSchema(BaseModel):
    """Reject unknown request fields instead of silently accepting untrusted input."""

    model_config = ConfigDict(extra="forbid")


class WindowSchema(StrictSchema):
    start: time
    end: time


class DaySchema(StrictSchema):
    weekday: int = Field(ge=0, le=6)
    windows: list[WindowSchema]


class ScheduleSchema(StrictSchema):
    days: list[DaySchema] = Field(default_factory=lambda: list[DaySchema]())


class ExceptionSchema(StrictSchema):
    day: date
    closed: bool = False
    override_windows: list[WindowSchema] | None = None


class ClosureSchema(StrictSchema):
    month: int
    day: int


class BlockSchema(StrictSchema):
    start: datetime
    end: datetime
    reason: str | None = None


class CreateCalendarSchema(StrictSchema):
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


class UpdateScheduleSchema(StrictSchema):
    expected_version: int = Field(ge=1)
    weekly_schedule: ScheduleSchema


class SetExceptionSchema(StrictSchema):
    expected_version: int = Field(ge=1)
    exception: ExceptionSchema


class ChangeBlockSchema(StrictSchema):
    expected_version: int = Field(ge=1)
    block: BlockSchema


class VersionSchema(StrictSchema):
    expected_version: int = Field(ge=1)


class AvailabilitySchema(StrictSchema):
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


class SlotSchema(StrictSchema):
    resource_id: str
    start: datetime
    end: datetime
