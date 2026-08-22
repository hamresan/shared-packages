from subscription.application import ResolveEntitlementsService
from subscription.domain import EntitlementKey
from subscription.presentation.dependencies import AuthenticatedActor, SubjectAccessGuard
from subscription.presentation.errors import SubscriptionHttpErrorMapper
from subscription.presentation.mappers import SubscriptionRequestMapper, SubscriptionResponseMapper
from subscription.presentation.schemas import EntitlementResponse, SubjectReferenceSchema


class EntitlementEndpoints:
    def __init__(
        self,
        resolver: ResolveEntitlementsService,
        subject_guard: SubjectAccessGuard,
        request_mapper: SubscriptionRequestMapper,
        response_mapper: SubscriptionResponseMapper,
        error_mapper: SubscriptionHttpErrorMapper,
    ) -> None:
        self._resolver = resolver
        self._subject_guard = subject_guard
        self._request_mapper = request_mapper
        self._response_mapper = response_mapper
        self._error_mapper = error_mapper

    async def resolve(
        self,
        actor: AuthenticatedActor,
        subject_type: str,
        subject_id: str,
        key: str,
    ) -> EntitlementResponse:
        try:
            subject = self._request_mapper.subject(
                SubjectReferenceSchema(subject_type=subject_type, subject_id=subject_id)
            )
            await self._subject_guard.ensure_allowed(actor, subject)
            grants = await self._resolver.execute(subject, EntitlementKey(key))
            return self._response_mapper.entitlements(grants)
        except Exception as error:
            raise self._error_mapper.map(error) from error
