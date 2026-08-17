from typing import cast

from store.domain import DailyWorkingHours, WeeklyWorkingSchedule


class DailyWorkingHoursPersistenceMapper:
    def to_record(self, hours: DailyWorkingHours | None) -> dict[str, object] | None:
        if hours is None:
            return None
        return {"opens_at": hours.opens_at, "closes_at": hours.closes_at}

    def to_domain(self, record: object) -> DailyWorkingHours | None:
        if not isinstance(record, dict):
            return None
        typed_record = cast(dict[str, object], record)
        opens_at = typed_record.get("opens_at")
        closes_at = typed_record.get("closes_at")
        if not isinstance(opens_at, str) or not isinstance(closes_at, str):
            return None
        return DailyWorkingHours(opens_at=opens_at, closes_at=closes_at)


class WeeklyWorkingSchedulePersistenceMapper:
    def __init__(self, daily_mapper: DailyWorkingHoursPersistenceMapper) -> None:
        self._daily_mapper = daily_mapper

    def to_record(self, schedule: WeeklyWorkingSchedule | None) -> dict[str, object] | None:
        if schedule is None:
            return None
        return {
            "monday": self._daily_mapper.to_record(schedule.monday),
            "tuesday": self._daily_mapper.to_record(schedule.tuesday),
            "wednesday": self._daily_mapper.to_record(schedule.wednesday),
            "thursday": self._daily_mapper.to_record(schedule.thursday),
            "friday": self._daily_mapper.to_record(schedule.friday),
            "saturday": self._daily_mapper.to_record(schedule.saturday),
            "sunday": self._daily_mapper.to_record(schedule.sunday),
        }

    def to_domain(self, record: dict[str, object] | None) -> WeeklyWorkingSchedule | None:
        if record is None:
            return None
        return WeeklyWorkingSchedule(
            monday=self._daily_mapper.to_domain(record.get("monday")),
            tuesday=self._daily_mapper.to_domain(record.get("tuesday")),
            wednesday=self._daily_mapper.to_domain(record.get("wednesday")),
            thursday=self._daily_mapper.to_domain(record.get("thursday")),
            friday=self._daily_mapper.to_domain(record.get("friday")),
            saturday=self._daily_mapper.to_domain(record.get("saturday")),
            sunday=self._daily_mapper.to_domain(record.get("sunday")),
        )
