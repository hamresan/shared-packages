from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from subscription.domain import SubjectReference, SubscriptionStatus, UsagePeriod
from subscription.infrastructure.persistence.sqlalchemy.models import SubscriptionModel


@dataclass(frozen=True, slots=True)
class UsageWindow:
    start: datetime | None
    end: datetime


class CalendarUsageWindowCalculator:
    def calculate(self, period: UsagePeriod, at: datetime) -> UsageWindow | None:
        if period is UsagePeriod.LIFETIME:
            return UsageWindow(None, at)
        if period is UsagePeriod.DAY:
            return UsageWindow(at.replace(hour=0, minute=0, second=0, microsecond=0), at)
        if period is UsagePeriod.WEEK:
            day_start = at.replace(hour=0, minute=0, second=0, microsecond=0)
            return UsageWindow(day_start - timedelta(days=at.weekday()), at)
        if period is UsagePeriod.MONTH:
            return UsageWindow(at.replace(day=1, hour=0, minute=0, second=0, microsecond=0), at)
        return None


class SqlAlchemyUsageWindowResolver:
    def __init__(
        self,
        session: AsyncSession,
        calendar_calculator: CalendarUsageWindowCalculator,
    ) -> None:
        self._session = session
        self._calendar_calculator = calendar_calculator

    async def resolve(
        self,
        subject: SubjectReference,
        period: UsagePeriod,
        at: datetime,
    ) -> UsageWindow:
        calendar_window = self._calendar_calculator.calculate(period, at)
        if calendar_window is not None:
            return calendar_window
        status = (
            SubscriptionStatus.TRIALING.value
            if period is UsagePeriod.TRIAL
            else SubscriptionStatus.ACTIVE.value
        )
        result = await self._session.execute(
            select(SubscriptionModel)
            .where(
                SubscriptionModel.subject_type == subject.subject_type,
                SubscriptionModel.subject_id == subject.subject_id,
                SubscriptionModel.status == status,
            )
            .order_by(SubscriptionModel.started_at.desc())
            .limit(1)
        )
        subscription = result.scalar_one_or_none()
        if subscription is None:
            return UsageWindow(at, at)
        start = (
            subscription.trial_started_at
            if period is UsagePeriod.TRIAL
            else subscription.started_at
        )
        return UsageWindow(start or at, at)
