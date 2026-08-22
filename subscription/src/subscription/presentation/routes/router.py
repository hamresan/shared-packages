from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from subscription.domain import UsagePeriod
from subscription.presentation.dependencies import AuthenticatedActor, AuthenticatedActorDependency
from subscription.presentation.routes.entitlement import EntitlementEndpoints
from subscription.presentation.routes.plan import PlanEndpoints
from subscription.presentation.routes.subscription import SubscriptionEndpoints
from subscription.presentation.routes.usage import UsageEndpoints
from subscription.presentation.schemas import (
    ActivateSubscriptionRequest,
    ChangePlanStatusRequest,
    CreatePlanRequest,
    CreateSubscriptionRequest,
    EntitlementResponse,
    PlanResponse,
    RecordUsageRequest,
    RenewSubscriptionRequest,
    SubscriptionResponse,
    UsageCounterResponse,
    UsageRecordResponse,
)


class SubscriptionRouterFactory:
    def __init__(
        self,
        *,
        authenticated_actor_dependency: AuthenticatedActorDependency,
        plan_endpoints: PlanEndpoints,
        subscription_endpoints: SubscriptionEndpoints,
        usage_endpoints: UsageEndpoints,
        entitlement_endpoints: EntitlementEndpoints,
        prefix: str = "/subscription",
    ) -> None:
        self._authenticated_actor_dependency = authenticated_actor_dependency
        self._plan_endpoints = plan_endpoints
        self._subscription_endpoints = subscription_endpoints
        self._usage_endpoints = usage_endpoints
        self._entitlement_endpoints = entitlement_endpoints
        self._prefix = prefix

    def create(self) -> APIRouter:
        actor_dependency = self._authenticated_actor_dependency
        plan_endpoints = self._plan_endpoints
        subscription_endpoints = self._subscription_endpoints
        usage_endpoints = self._usage_endpoints
        entitlement_endpoints = self._entitlement_endpoints
        router = APIRouter(prefix=self._prefix, tags=["subscription"])

        async def create_plan(
            request: CreatePlanRequest,
            actor: Annotated[AuthenticatedActor, Depends(actor_dependency)],
        ) -> PlanResponse:
            return await plan_endpoints.create(actor, request)

        async def get_plan(
            plan_id: UUID,
            actor: Annotated[AuthenticatedActor, Depends(actor_dependency)],
        ) -> PlanResponse:
            return await plan_endpoints.get(actor, plan_id)

        async def change_plan_status(
            plan_id: UUID,
            request: ChangePlanStatusRequest,
            actor: Annotated[AuthenticatedActor, Depends(actor_dependency)],
        ) -> PlanResponse:
            return await plan_endpoints.change_status(actor, plan_id, request)

        async def create_subscription(
            request: CreateSubscriptionRequest,
            actor: Annotated[AuthenticatedActor, Depends(actor_dependency)],
        ) -> SubscriptionResponse:
            return await subscription_endpoints.create(actor, request)

        async def get_subscription(
            subscription_id: UUID,
            actor: Annotated[AuthenticatedActor, Depends(actor_dependency)],
        ) -> SubscriptionResponse:
            return await subscription_endpoints.get(actor, subscription_id)

        async def start_trial(
            subscription_id: UUID,
            actor: Annotated[AuthenticatedActor, Depends(actor_dependency)],
        ) -> SubscriptionResponse:
            return await subscription_endpoints.start_trial(actor, subscription_id)

        async def activate_subscription(
            subscription_id: UUID,
            request: ActivateSubscriptionRequest,
            actor: Annotated[AuthenticatedActor, Depends(actor_dependency)],
        ) -> SubscriptionResponse:
            return await subscription_endpoints.activate(actor, subscription_id, request)

        async def cancel_subscription(
            subscription_id: UUID,
            actor: Annotated[AuthenticatedActor, Depends(actor_dependency)],
        ) -> SubscriptionResponse:
            return await subscription_endpoints.cancel(actor, subscription_id)

        async def renew_subscription(
            subscription_id: UUID,
            request: RenewSubscriptionRequest,
            actor: Annotated[AuthenticatedActor, Depends(actor_dependency)],
        ) -> SubscriptionResponse:
            return await subscription_endpoints.renew(actor, subscription_id, request)

        async def record_usage(
            request: RecordUsageRequest,
            actor: Annotated[AuthenticatedActor, Depends(actor_dependency)],
        ) -> UsageRecordResponse:
            return await usage_endpoints.record(actor, request)

        async def get_usage_counter(
            actor: Annotated[AuthenticatedActor, Depends(actor_dependency)],
            subject_type: Annotated[str, Query(min_length=1, max_length=64)],
            subject_id: Annotated[str, Query(min_length=1, max_length=255)],
            metric: Annotated[str, Query(min_length=1, max_length=128)],
            period: UsagePeriod,
        ) -> UsageCounterResponse:
            return await usage_endpoints.get_counter(actor, subject_type, subject_id, metric, period)

        async def resolve_entitlement(
            actor: Annotated[AuthenticatedActor, Depends(actor_dependency)],
            subject_type: Annotated[str, Query(min_length=1, max_length=64)],
            subject_id: Annotated[str, Query(min_length=1, max_length=255)],
            key: Annotated[str, Query(min_length=1, max_length=128)],
        ) -> EntitlementResponse:
            return await entitlement_endpoints.resolve(actor, subject_type, subject_id, key)

        router.add_api_route(
            "/plans",
            create_plan,
            methods=["POST"],
            response_model=PlanResponse,
            status_code=status.HTTP_201_CREATED,
        )
        router.add_api_route(
            "/plans/{plan_id}", get_plan, methods=["GET"], response_model=PlanResponse
        )
        router.add_api_route(
            "/plans/{plan_id}/status",
            change_plan_status,
            methods=["PATCH"],
            response_model=PlanResponse,
        )
        router.add_api_route(
            "/subscriptions",
            create_subscription,
            methods=["POST"],
            response_model=SubscriptionResponse,
            status_code=status.HTTP_201_CREATED,
        )
        router.add_api_route(
            "/subscriptions/{subscription_id}",
            get_subscription,
            methods=["GET"],
            response_model=SubscriptionResponse,
        )
        router.add_api_route(
            "/subscriptions/{subscription_id}/trial",
            start_trial,
            methods=["POST"],
            response_model=SubscriptionResponse,
        )
        router.add_api_route(
            "/subscriptions/{subscription_id}/activate",
            activate_subscription,
            methods=["POST"],
            response_model=SubscriptionResponse,
        )
        router.add_api_route(
            "/subscriptions/{subscription_id}/cancel",
            cancel_subscription,
            methods=["POST"],
            response_model=SubscriptionResponse,
        )
        router.add_api_route(
            "/subscriptions/{subscription_id}/renew",
            renew_subscription,
            methods=["POST"],
            response_model=SubscriptionResponse,
        )
        router.add_api_route(
            "/usage",
            record_usage,
            methods=["POST"],
            response_model=UsageRecordResponse,
            status_code=status.HTTP_201_CREATED,
        )
        router.add_api_route(
            "/usage", get_usage_counter, methods=["GET"], response_model=UsageCounterResponse
        )
        router.add_api_route(
            "/entitlements",
            resolve_entitlement,
            methods=["GET"],
            response_model=EntitlementResponse,
        )
        return router
