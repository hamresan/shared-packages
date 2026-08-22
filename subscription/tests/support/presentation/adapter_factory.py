from dataclasses import dataclass
from uuid import UUID

from subscription import (
    ActiveBaseSubscriptionPolicy,
    PlanDefinitionPolicy,
    PlanStatusTransitionPolicy,
    SubscriptionValidityPolicy,
)
from subscription.application import (
    ActivateSubscriptionService,
    CancelSubscriptionService,
    ChangePlanStatusService,
    CreatePlanMapper,
    CreatePlanService,
    CreateSubscriptionMapper,
    CreateSubscriptionService,
    GetPlanService,
    GetSubscriptionService,
    GetUsageCounterService,
    RecordUsageService,
    RenewSubscriptionService,
    ResolveEntitlementsService,
    StartTrialService,
)
from subscription.presentation import FastApiSubscriptionAdapter, build_fastapi_subscription_adapter
from tests.support.application.fakes import (
    FakeSubscriptionUnitOfWorkFactory,
    FixedClock,
    FixedIdentifierGenerator,
)
from tests.support.domain.subscription_lifecycle_factory import build_subscription_lifecycle_service
from tests.support.presentation.fakes import (
    FakeSubscriptionAuthorizer,
    FixedAuthenticatedActorDependency,
)

PLAN_ID = UUID("11111111-1111-4111-8111-111111111111")
SUBSCRIPTION_ID = UUID("22222222-2222-4222-8222-222222222222")


@dataclass(frozen=True, slots=True)
class SubscriptionApiTestRuntime:
    adapter: FastApiSubscriptionAdapter
    unit_of_work_factory: FakeSubscriptionUnitOfWorkFactory
    authorizer: FakeSubscriptionAuthorizer


def build_subscription_api_test_runtime(
    *,
    authorizer: FakeSubscriptionAuthorizer | None = None,
) -> SubscriptionApiTestRuntime:
    unit_of_work_factory = FakeSubscriptionUnitOfWorkFactory()
    clock = FixedClock()
    plan_identifier = FixedIdentifierGenerator(PLAN_ID)
    subscription_identifier = FixedIdentifierGenerator(SUBSCRIPTION_ID)
    lifecycle_service = build_subscription_lifecycle_service()
    active_base_policy = ActiveBaseSubscriptionPolicy()
    effective_authorizer = authorizer or FakeSubscriptionAuthorizer()

    adapter = build_fastapi_subscription_adapter(
        authenticated_actor_dependency=FixedAuthenticatedActorDependency(),
        authorizer=effective_authorizer,
        create_plan=CreatePlanService(
            unit_of_work_factory,
            CreatePlanMapper(plan_identifier, PlanDefinitionPolicy()),
        ),
        get_plan=GetPlanService(unit_of_work_factory),
        change_plan_status=ChangePlanStatusService(
            unit_of_work_factory,
            PlanStatusTransitionPolicy(),
        ),
        create_subscription=CreateSubscriptionService(
            unit_of_work_factory,
            CreateSubscriptionMapper(subscription_identifier, clock),
        ),
        get_subscription=GetSubscriptionService(unit_of_work_factory),
        start_trial=StartTrialService(
            unit_of_work_factory,
            clock,
            lifecycle_service,
            active_base_policy,
        ),
        activate_subscription=ActivateSubscriptionService(
            unit_of_work_factory,
            clock,
            lifecycle_service,
            active_base_policy,
        ),
        cancel_subscription=CancelSubscriptionService(
            unit_of_work_factory,
            clock,
            lifecycle_service,
        ),
        renew_subscription=RenewSubscriptionService(
            unit_of_work_factory,
            clock,
            lifecycle_service,
            active_base_policy,
        ),
        record_usage=RecordUsageService(unit_of_work_factory, clock),
        get_usage_counter=GetUsageCounterService(unit_of_work_factory, clock),
        resolve_entitlements=ResolveEntitlementsService(
            unit_of_work_factory,
            clock,
            SubscriptionValidityPolicy(),
        ),
    )
    return SubscriptionApiTestRuntime(adapter, unit_of_work_factory, effective_authorizer)
