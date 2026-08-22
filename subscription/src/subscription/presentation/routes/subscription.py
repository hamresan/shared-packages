from uuid import UUID

from subscription.application import (
    ActivateSubscriptionService,
    CancelSubscriptionService,
    CreateSubscriptionService,
    RenewSubscriptionService,
    StartTrialService,
)
from subscription.presentation.dependencies import (
    AuthenticatedActor,
    SubjectAccessGuard,
    SubscriptionResourceAccessGuard,
)
from subscription.presentation.errors import SubscriptionHttpErrorMapper
from subscription.presentation.mappers import SubscriptionRequestMapper, SubscriptionResponseMapper
from subscription.presentation.schemas import (
    ActivateSubscriptionRequest,
    CreateSubscriptionRequest,
    RenewSubscriptionRequest,
    SubscriptionResponse,
)


class SubscriptionEndpoints:
    def __init__(
        self,
        creator: CreateSubscriptionService,
        trial_starter: StartTrialService,
        activator: ActivateSubscriptionService,
        canceller: CancelSubscriptionService,
        renewer: RenewSubscriptionService,
        subject_guard: SubjectAccessGuard,
        resource_guard: SubscriptionResourceAccessGuard,
        request_mapper: SubscriptionRequestMapper,
        response_mapper: SubscriptionResponseMapper,
        error_mapper: SubscriptionHttpErrorMapper,
    ) -> None:
        self._creator = creator
        self._trial_starter = trial_starter
        self._activator = activator
        self._canceller = canceller
        self._renewer = renewer
        self._subject_guard = subject_guard
        self._resource_guard = resource_guard
        self._request_mapper = request_mapper
        self._response_mapper = response_mapper
        self._error_mapper = error_mapper

    async def create(
        self,
        actor: AuthenticatedActor,
        request: CreateSubscriptionRequest,
    ) -> SubscriptionResponse:
        try:
            command = self._request_mapper.create_subscription(request)
            await self._subject_guard.ensure_allowed(actor, command.subject)
            return self._response_mapper.subscription(await self._creator.execute(command))
        except Exception as error:
            raise self._error_mapper.map(error) from error

    async def get(self, actor: AuthenticatedActor, subscription_id: UUID) -> SubscriptionResponse:
        try:
            subscription = await self._resource_guard.ensure_allowed(actor, subscription_id)
            return self._response_mapper.subscription(subscription)
        except Exception as error:
            raise self._error_mapper.map(error) from error

    async def start_trial(
        self,
        actor: AuthenticatedActor,
        subscription_id: UUID,
    ) -> SubscriptionResponse:
        try:
            await self._resource_guard.ensure_allowed(actor, subscription_id)
            updated = await self._trial_starter.execute(subscription_id)
            return self._response_mapper.subscription(updated)
        except Exception as error:
            raise self._error_mapper.map(error) from error

    async def activate(
        self,
        actor: AuthenticatedActor,
        subscription_id: UUID,
        request: ActivateSubscriptionRequest,
    ) -> SubscriptionResponse:
        try:
            await self._resource_guard.ensure_allowed(actor, subscription_id)
            command = self._request_mapper.activate_subscription(subscription_id, request)
            return self._response_mapper.subscription(await self._activator.execute(command))
        except Exception as error:
            raise self._error_mapper.map(error) from error

    async def cancel(
        self,
        actor: AuthenticatedActor,
        subscription_id: UUID,
    ) -> SubscriptionResponse:
        try:
            await self._resource_guard.ensure_allowed(actor, subscription_id)
            updated = await self._canceller.execute(subscription_id)
            return self._response_mapper.subscription(updated)
        except Exception as error:
            raise self._error_mapper.map(error) from error

    async def renew(
        self,
        actor: AuthenticatedActor,
        subscription_id: UUID,
        request: RenewSubscriptionRequest,
    ) -> SubscriptionResponse:
        try:
            await self._resource_guard.ensure_allowed(actor, subscription_id)
            command = self._request_mapper.renew_subscription(subscription_id, request)
            return self._response_mapper.subscription(await self._renewer.execute(command))
        except Exception as error:
            raise self._error_mapper.map(error) from error
