from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from subscription.application import UsageRepository
from subscription.domain import SubjectReference, UsageCounter, UsageMetric, UsagePeriod, UsageRecord
from subscription.infrastructure.persistence.sqlalchemy.mappers import UsagePersistenceMapper
from subscription.infrastructure.persistence.sqlalchemy.models import UsageRecordModel
from subscription.infrastructure.persistence.sqlalchemy.repositories.usage_window import (
    SqlAlchemyUsageWindowResolver,
)


class SqlAlchemyUsageRepository(UsageRepository):
    def __init__(
        self,
        session: AsyncSession,
        mapper: UsagePersistenceMapper,
        window_resolver: SqlAlchemyUsageWindowResolver,
    ) -> None:
        self._session = session
        self._mapper = mapper
        self._window_resolver = window_resolver

    async def add(self, record: UsageRecord) -> None:
        self._session.add(self._mapper.to_model(record))

    async def get_counter(
        self,
        subject: SubjectReference,
        metric: UsageMetric,
        period: UsagePeriod,
        at: datetime,
    ) -> UsageCounter:
        window = await self._window_resolver.resolve(subject, period, at)
        statement = select(func.coalesce(func.sum(UsageRecordModel.amount), 0)).where(
            UsageRecordModel.subject_type == subject.subject_type,
            UsageRecordModel.subject_id == subject.subject_id,
            UsageRecordModel.metric == metric.key,
            UsageRecordModel.occurred_at <= window.end,
        )
        if window.start is not None:
            statement = statement.where(UsageRecordModel.occurred_at >= window.start)
        consumed = int((await self._session.execute(statement)).scalar_one())
        return UsageCounter(metric=metric, period=period, consumed=consumed)
