from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from subscription.application import UsageRepository
from subscription.domain import (
    SubjectReference,
    UsageCounter,
    UsageMetric,
    UsagePeriod,
    UsageRecord,
)
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

    async def add_once(self, record: UsageRecord) -> UsageRecord:
        if record.idempotency_key is None:
            await self.add(record)
            return record

        existing = await self._get_by_idempotency_key(record)
        if existing is not None:
            return existing

        try:
            async with self._session.begin_nested():
                self._session.add(self._mapper.to_model(record))
                await self._session.flush()
        except IntegrityError:
            existing = await self._get_by_idempotency_key(record)
            if existing is None:
                raise
            return existing

        return record

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

    async def _get_by_idempotency_key(self, record: UsageRecord) -> UsageRecord | None:
        statement = select(UsageRecordModel).where(
            UsageRecordModel.subject_type == record.subject.subject_type,
            UsageRecordModel.subject_id == record.subject.subject_id,
            UsageRecordModel.metric == record.metric.key,
            UsageRecordModel.idempotency_key == record.idempotency_key,
        )
        model = (await self._session.execute(statement)).scalar_one_or_none()
        if model is None:
            return None
        return self._mapper.to_domain(model)
