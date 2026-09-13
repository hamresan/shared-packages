import pytest

from subscription import SubjectReference, UsageMetric, UsagePeriod
from subscription.application import (
    GetUsageCounterQuery,
    GetUsageCounterService,
    RecordUsageCommand,
    RecordUsageService,
)
from tests.support.application.fakes import FakeSubscriptionUnitOfWorkFactory, FixedClock


@pytest.mark.asyncio
async def test_record_usage_service_persists_usage_event() -> None:
    unit_of_work_factory = FakeSubscriptionUnitOfWorkFactory()
    service = RecordUsageService(unit_of_work_factory, FixedClock())
    command = RecordUsageCommand(
        subject=SubjectReference("store", "store-1"),
        metric=UsageMetric("conversations"),
        amount=3,
    )

    result = await service.execute(command)

    assert result.amount == 3
    assert unit_of_work_factory.usage_repository.records == [result]
    assert unit_of_work_factory.unit_of_work.commit_count == 1


@pytest.mark.asyncio
async def test_record_usage_service_reuses_record_for_same_idempotency_key() -> None:
    unit_of_work_factory = FakeSubscriptionUnitOfWorkFactory()
    service = RecordUsageService(unit_of_work_factory, FixedClock())
    command = RecordUsageCommand(
        subject=SubjectReference("store", "store-1"),
        metric=UsageMetric("conversations"),
        idempotency_key="conversation-session-1",
    )

    first = await service.execute(command)
    second = await service.execute(command)

    assert second == first
    assert unit_of_work_factory.usage_repository.records == [first]
    assert unit_of_work_factory.unit_of_work.commit_count == 2


@pytest.mark.asyncio
async def test_record_usage_service_scopes_idempotency_key_by_subject_and_metric() -> None:
    unit_of_work_factory = FakeSubscriptionUnitOfWorkFactory()
    service = RecordUsageService(unit_of_work_factory, FixedClock())
    shared_key = "conversation-session-1"

    first = await service.execute(
        RecordUsageCommand(
            subject=SubjectReference("store", "store-1"),
            metric=UsageMetric("conversations"),
            idempotency_key=shared_key,
        )
    )
    second = await service.execute(
        RecordUsageCommand(
            subject=SubjectReference("store", "store-2"),
            metric=UsageMetric("conversations"),
            idempotency_key=shared_key,
        )
    )
    third = await service.execute(
        RecordUsageCommand(
            subject=SubjectReference("store", "store-1"),
            metric=UsageMetric("messages"),
            idempotency_key=shared_key,
        )
    )

    assert unit_of_work_factory.usage_repository.records == [first, second, third]


@pytest.mark.asyncio
async def test_get_usage_counter_service_reads_current_counter() -> None:
    subject = SubjectReference("store", "store-1")
    metric = UsageMetric("conversations")
    unit_of_work_factory = FakeSubscriptionUnitOfWorkFactory()
    unit_of_work_factory.usage_repository.counters[(subject, metric, UsagePeriod.WEEK)] = 12
    service = GetUsageCounterService(unit_of_work_factory, FixedClock())

    result = await service.execute(GetUsageCounterQuery(subject, metric, UsagePeriod.WEEK))

    assert result.consumed == 12
