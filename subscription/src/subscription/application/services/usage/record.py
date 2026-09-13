from subscription.application.contracts import Clock, SubscriptionUnitOfWorkFactory
from subscription.application.dto import RecordUsageCommand
from subscription.domain import UsageRecord


class RecordUsageService:
    def __init__(
        self,
        unit_of_work_factory: SubscriptionUnitOfWorkFactory,
        clock: Clock,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock

    async def execute(self, command: RecordUsageCommand) -> UsageRecord:
        record = UsageRecord(
            subject=command.subject,
            metric=command.metric,
            amount=command.amount,
            occurred_at=self._clock.now(),
            idempotency_key=command.idempotency_key,
        )
        async with self._unit_of_work_factory() as unit_of_work:
            persisted_record = await unit_of_work.usage.add_once(record)
            await unit_of_work.commit()
        return persisted_record
