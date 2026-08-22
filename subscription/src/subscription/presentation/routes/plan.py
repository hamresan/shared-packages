from uuid import UUID

from subscription.application import ChangePlanStatusService, CreatePlanService, GetPlanService
from subscription.presentation.dependencies import AuthenticatedActor, PlanManagementGuard
from subscription.presentation.errors import SubscriptionHttpErrorMapper
from subscription.presentation.mappers import SubscriptionRequestMapper, SubscriptionResponseMapper
from subscription.presentation.schemas import ChangePlanStatusRequest, CreatePlanRequest, PlanResponse


class PlanEndpoints:
    def __init__(
        self,
        creator: CreatePlanService,
        reader: GetPlanService,
        status_changer: ChangePlanStatusService,
        guard: PlanManagementGuard,
        request_mapper: SubscriptionRequestMapper,
        response_mapper: SubscriptionResponseMapper,
        error_mapper: SubscriptionHttpErrorMapper,
    ) -> None:
        self._creator = creator
        self._reader = reader
        self._status_changer = status_changer
        self._guard = guard
        self._request_mapper = request_mapper
        self._response_mapper = response_mapper
        self._error_mapper = error_mapper

    async def create(self, actor: AuthenticatedActor, request: CreatePlanRequest) -> PlanResponse:
        try:
            await self._guard.ensure_allowed(actor)
            plan = await self._creator.execute(self._request_mapper.create_plan(request))
            return self._response_mapper.plan(plan)
        except Exception as error:
            raise self._error_mapper.map(error) from error

    async def get(self, actor: AuthenticatedActor, plan_id: UUID) -> PlanResponse:
        try:
            await self._guard.ensure_allowed(actor)
            return self._response_mapper.plan(await self._reader.execute(plan_id))
        except Exception as error:
            raise self._error_mapper.map(error) from error

    async def change_status(
        self,
        actor: AuthenticatedActor,
        plan_id: UUID,
        request: ChangePlanStatusRequest,
    ) -> PlanResponse:
        try:
            await self._guard.ensure_allowed(actor)
            plan = await self._status_changer.execute(plan_id, request.status)
            return self._response_mapper.plan(plan)
        except Exception as error:
            raise self._error_mapper.map(error) from error
