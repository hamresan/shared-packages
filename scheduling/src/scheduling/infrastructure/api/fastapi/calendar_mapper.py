"""HTTP schema-to-domain transformations isolated from request handlers."""

from scheduling.domain.calendar import (
    AnnualClosure,
    BlockedPeriod,
    Calendar,
    CalendarException,
    DaySchedule,
    WeeklySchedule,
    WorkingWindow,
)
from scheduling.domain.time import IanaTimeZone, UtcInterval

from .schemas import (
    BlockSchema,
    CalendarSchema,
    ClosureSchema,
    CreateCalendarSchema,
    DaySchema,
    ExceptionSchema,
    ScheduleSchema,
    WindowSchema,
)


class CalendarHttpMapper:
    def to_domain(self, tenant_id: str, input_data: CreateCalendarSchema) -> Calendar:
        return Calendar(
            calendar_id=input_data.calendar_id,
            tenant_id=tenant_id,
            scope=input_data.scope,
            scope_id=input_data.scope_id,
            timezone=IanaTimeZone(input_data.timezone),
            weekly_schedule=self.schedule(input_data.weekly_schedule),
            exceptions=tuple(self.exception(item) for item in input_data.exceptions),
            annual_closures=tuple(
                AnnualClosure(item.month, item.day) for item in input_data.annual_closures
            ),
            blocked_periods=tuple(self.block(item) for item in input_data.blocked_periods),
        )

    def to_schema(self, calendar: Calendar) -> CalendarSchema:
        return CalendarSchema(
            calendar_id=calendar.calendar_id,
            tenant_id=calendar.tenant_id,
            scope=calendar.scope,
            scope_id=calendar.scope_id,
            timezone=calendar.timezone.key,
            weekly_schedule=ScheduleSchema(
                days=[
                    DaySchema(
                        weekday=day.weekday,
                        windows=[
                            WindowSchema(start=window.start, end=window.end)
                            for window in day.windows
                        ],
                    )
                    for day in calendar.weekly_schedule.days
                ]
            ),
            exceptions=[
                ExceptionSchema(
                    day=item.day,
                    closed=item.closed,
                    override_windows=(
                        None
                        if item.override_windows is None
                        else [WindowSchema(start=w.start, end=w.end) for w in item.override_windows]
                    ),
                )
                for item in calendar.exceptions
            ],
            annual_closures=[
                ClosureSchema(month=item.month, day=item.day) for item in calendar.annual_closures
            ],
            blocked_periods=[
                BlockSchema(
                    start=item.interval.start,
                    end=item.interval.end,
                    reason=item.reason,
                )
                for item in calendar.blocked_periods
            ],
            version=calendar.version,
            archived=calendar.archived,
        )

    @staticmethod
    def schedule(value: ScheduleSchema) -> WeeklySchedule:
        return WeeklySchedule(
            tuple(
                DaySchedule(
                    weekday=day.weekday,
                    windows=tuple(WorkingWindow(w.start, w.end) for w in day.windows),
                )
                for day in value.days
            )
        )

    @staticmethod
    def exception(value: ExceptionSchema) -> CalendarException:
        return CalendarException(
            day=value.day,
            closed=value.closed,
            override_windows=(
                None
                if value.override_windows is None
                else tuple(WorkingWindow(w.start, w.end) for w in value.override_windows)
            ),
        )

    @staticmethod
    def block(value: BlockSchema) -> BlockedPeriod:
        return BlockedPeriod(UtcInterval(value.start, value.end), value.reason)
