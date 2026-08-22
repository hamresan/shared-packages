from subscription.application import (
    ActivateSubscriptionService,
    CancelSubscriptionService,
    ChangePlanStatusService,
    CreatePlanService,
    CreateSubscriptionService,
    GetPlanService,
    GetSubscriptionService,
    GetUsageCounterService,
    RecordUsageService,
    RenewSubscriptionService,
    ResolveEntitlementsService,
    StartTrialService,
)
from subscription.presentation.dependencies import (
    AuthenticatedActorDependency,
    PlanManagementGuard,
    SubjectAccessGuard,
    SubscriptionAuthorizer,
    SubscriptionResourceAccessGuard,
)
from subscription.presentation.errors import SubscriptionHttpErrorMapper
from subscription.presentation.fastapi import FastApiSubscriptionAdapter
from subscription.presentation.mappers import (
    EntitlementValuePresentationMapper,
    SubscriptionRequestMapper,
    SubscriptionResponseMapper,
)
from subscription.presentation.routes import (
    EntitlementEndpoints,
    PlanEndpoints,
    SubscriptionEndpoints,
    SubscriptionRouterFactory,
    UsageEndpoints,
)


def build_fastapi_subscription_adapter(
    *,
    authenticated_actor_dependency: AuthenticatedActorDependency,
    authorizer: SubscriptionAuthorizer,
    create_plan: CreatePlanService,
    get_plan: GetPlanService,
    change_plan_status: ChangePlanStatusService,
    create_subscription: CreateSubscriptionService,
    get_subscription: GetSubscriptionService,
    start_trial: StartTrialService,
    activate_subscription: ActivateSubscriptionService,
    cancel_subscription: CancelSubscriptionService,
    renew_subscription: RenewSubscriptionService,
    record_usage: RecordUsageService,
    get_usage_counter: GetUsageCounterService,
    resolve_entitlements: ResolveEntitlementsService,
    prefix: str = "/subscription",
) -> FastApiSubscriptionAdapter:
    entitlement_value_mapper = EntitlementValuePresentationMapper()
    request_mapper = SubscriptionRequestMapper(entitlement_value_mapper)
    response_mapper = SubscriptionResponseMapper(entitlement_value_mapper)
    error_mapper = SubscriptionHttpErrorMapper()
    plan_guard = PlanManagementGuard(authorizer)
    subject_guard = SubjectAccessGuard(authorizer)
    resource_guard = SubscriptionResourceAccessGuard(get_subscription, subject_guard)

    router = SubscriptionRouterFactory(
        authenticated_actor_dependency=authenticated_actor_dependency,
        plan_endpoints=PlanEndpoints(
            create_plan,
            get_plan,
            change_plan_status,
            plan_guard,
            request_mapper,
            response_mapper,
            error_mapper,
        ),
        subscription_endpoints=SubscriptionEndpoints(
            create_subscription,
            start_trial,
            activate_subscription,
            cancel_subscription,
            renew_subscription,
            subject_guard,
            resource_guard,
            request_mapper,
            response_mapper,
            error_mapper,
        ),
        usage_endpoints=UsageEndpoints(
            record_usage,
            get_usage_counter,
            subject_guard,
            request_mapper,
            response_mapper,
            error_mapper,
        ),
        entitlement_endpoints=EntitlementEndpoints(
            resolve_entitlements,
            subject_guard,
            request_mapper,
            response_mapper,
            error_mapper,
        ),
        prefix=prefix,
    ).create()
    return FastApiSubscriptionAdapter(subscription_router=router)
