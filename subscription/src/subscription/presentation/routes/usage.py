from subscription.application import GetUsageCounterService, RecordUsageService
from subscription.domain import UsagePeriod
from subscription.presentation.dependencies import AuthenticatedActor, SubjectAccessGuard
from subscription.presentation.errors import SubscriptionHttpErrorMapper
from subscription.presentation.mappers import SubscriptionRequestMapper, SubscriptionResponseMapper
from subscription.presentation.schemas import (
    RecordUsageRequest,
    SubjectReferenceSchema,
    UsageCounterResponse,
    UsageRecordResponse,
)


class UsageEndpoints:
    def __init__(
        self,
        recorder: RecordUsageService,
        counter_reader: GetUsageCounterService,
        subject_guard: SubjectAccessGuard,
        request_mapper: SubscriptionRequestMapper,
        response_mapper: SubscriptionResponseMapper,
        error_mapper: SubscriptionHttpErrorMapper,
    ) -> None:
        self._recorder = recorder
        self._counter_reader = counter_reader
        self._subject_guard = subject_guard
        self._request_mapper = request_mapper
        self._response_mapper = response_mapper
        self._error_mapper = error_mapper

    async def record(
        self,
        actor: AuthenticatedActor,
        request: RecordUsageRequest,
    ) -> UsageRecordResponse:
        try:
            command = self._request_mapper.record_usage(request)
            await self._subject_guard.ensure_allowed(actor, command.subject)
            return self._response_mapper.usage_record(await self._recorder.execute(command))
        except Exception as error:
            raise self._error_mapper.map(error) from error

    async def get_counter(
        self,
        actor: AuthenticatedActor,
        subject_type: str,
        subject_id: str,
        metric: str,
        period: UsagePeriod,
    ) -> UsageCounterResponse:
        try:
            subject = self._request_mapper.subject(
                SubjectReferenceSchema(subject_type=subject_type, subject_id=subject_id)
            )
            await self._subject_guard.ensure_allowed(actor, subject)
            query = self._request_mapper.usage_counter(subject, metric, period)
            return self._response_mapper.usage_counter(await self._counter_reader.execute(query))
        except Exception as error:
            raise self._error_mapper.map(error) from error
