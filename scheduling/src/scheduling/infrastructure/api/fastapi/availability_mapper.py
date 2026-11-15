"""Availability API transport conversion, independent of business orchestration."""

from datetime import datetime, timedelta

from scheduling.application.models import AvailabilityLookup
from scheduling.domain.time import UtcInterval
from scheduling.engine import AvailableSlot

from .schemas import AvailabilitySchema, SlotSchema


class AvailabilityHttpMapper:
    def to_lookup(self, value: AvailabilitySchema, now: datetime) -> AvailabilityLookup:
        return AvailabilityLookup(
            organization_id=value.organization_id,
            location_id=value.location_id,
            resource_ids=tuple(value.resource_ids),
            window=UtcInterval(value.start, value.end),
            duration=timedelta(minutes=value.duration_minutes),
            step=timedelta(minutes=value.step_minutes),
            now=now,
            buffer_before=timedelta(minutes=value.buffer_before_minutes),
            buffer_after=timedelta(minutes=value.buffer_after_minutes),
            minimum_notice=timedelta(minutes=value.minimum_notice_minutes),
            maximum_horizon=timedelta(days=value.maximum_horizon_days),
        )

    @staticmethod
    def to_schema(slot: AvailableSlot) -> SlotSchema:
        return SlotSchema(
            resource_id=slot.resource_id,
            start=slot.interval.start,
            end=slot.interval.end,
        )
