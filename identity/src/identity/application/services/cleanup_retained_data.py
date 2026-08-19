from identity.application.contracts.security import Clock
from identity.application.contracts.unit_of_work import IdentityUnitOfWorkFactory
from identity.application.dto import DataRetentionCleanupResult
from identity.application.policies.data_retention import DataRetentionPolicy


class CleanupRetainedIdentityDataService:
    def __init__(
        self,
        *,
        unit_of_work_factory: IdentityUnitOfWorkFactory,
        clock: Clock,
        retention_policy: DataRetentionPolicy,
        batch_size: int,
    ) -> None:
        if batch_size < 1:
            raise ValueError("Retention cleanup batch size must be positive")
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock
        self._retention_policy = retention_policy
        self._batch_size = batch_size

    async def execute(self) -> DataRetentionCleanupResult:
        cutoffs = self._retention_policy.cutoffs(self._clock.now())
        async with self._unit_of_work_factory() as uow:
            deleted_otp_challenges = await uow.otp_challenges.delete_retained_before(
                cutoffs.otp_challenges_before,
                self._batch_size,
            )
            deleted_sessions = await uow.sessions.delete_retained_before(
                cutoffs.sessions_before,
                self._batch_size,
            )
            await uow.commit()

        return DataRetentionCleanupResult(
            deleted_otp_challenges=deleted_otp_challenges,
            deleted_sessions=deleted_sessions,
        )
