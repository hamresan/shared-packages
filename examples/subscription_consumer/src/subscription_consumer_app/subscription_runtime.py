from dataclasses import dataclass

from fastapi import FastAPI

from subscription import (
    ActiveBaseSubscriptionPolicy,
    PlanDefinitionPolicy,
    PlanStatusTransitionPolicy,
    SubscriptionDefinitionValidator,
    SubscriptionLifecycleService,
    SubscriptionStateValidator,
    SubscriptionStatusTransitionPolicy,
    SubscriptionTimelineValidator,
    SubscriptionValidityPolicy,
    TimestampOrderValidator,
    TimezoneAwareDatetimeValidator,
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
from subscription.infrastructure.persistence import build_sqlalchemy_subscription_unit_of_work_factory
from subscription.presentation import FastApiSubscriptionAdapter, build_fastapi_subscription_adapter

from subscription_consumer_app.authentication import StaticAuthenticatedActorDependency
from subscription_consumer_app.authorization import StoreSubscriptionAuthorizer
from subscription_consumer_app.database import ConsumerDatabase
from subscription_consumer_app.payment_events import PaidSubscriptionEventHandler
from subscription_consumer_app.runtime_support import SystemClock, UuidIdentifierGenerator


@dataclass(frozen=True, slots=True)
class SubscriptionRuntime:
    app: FastAPI
    database: ConsumerDatabase
    adapter: FastApiSubscriptionAdapter
    payment_events: PaidSubscriptionEventHandler


def build_subscription_runtime(database_url: str = "sqlite+aiosqlite:///:memory:") -> SubscriptionRuntime:
    database = ConsumerDatabase(database_url)
    unit_of_work_factory = build_sqlalchemy_subscription_unit_of_work_factory(database.session_factory)
    clock = SystemClock()
    identifier_generator = UuidIdentifierGenerator()
    datetime_validator = TimezoneAwareDatetimeValidator()
    lifecycle_service = SubscriptionLifecycleService(
        transition_policy=SubscriptionStatusTransitionPolicy(),
        definition_validator=SubscriptionDefinitionValidator(
            timeline_validator=SubscriptionTimelineValidator(
                datetime_validator=datetime_validator,
                timestamp_order_validator=TimestampOrderValidator(),
            ),
            state_validator=SubscriptionStateValidator(),
        ),
        datetime_validator=datetime_validator,
    )
    active_base_policy = ActiveBaseSubscriptionPolicy()

    create_plan = CreatePlanService(
        unit_of_work_factory,
        CreatePlanMapper(identifier_generator, PlanDefinitionPolicy()),
    )
    get_plan = GetPlanService(unit_of_work_factory)
    change_plan_status = ChangePlanStatusService(
        unit_of_work_factory,
        PlanStatusTransitionPolicy(),
    )
    create_subscription = CreateSubscriptionService(
        unit_of_work_factory,
        CreateSubscriptionMapper(identifier_generator, clock),
    )
    get_subscription = GetSubscriptionService(unit_of_work_factory)
    start_trial = StartTrialService(
        unit_of_work_factory,
        clock,
        lifecycle_service,
        active_base_policy,
    )
    activate_subscription = ActivateSubscriptionService(
        unit_of_work_factory,
        clock,
        lifecycle_service,
        active_base_policy,
    )
    cancel_subscription = CancelSubscriptionService(
        unit_of_work_factory,
        clock,
        lifecycle_service,
    )
    renew_subscription = RenewSubscriptionService(
        unit_of_work_factory,
        clock,
        lifecycle_service,
        active_base_policy,
    )
    record_usage = RecordUsageService(unit_of_work_factory, clock)
    get_usage_counter = GetUsageCounterService(unit_of_work_factory, clock)
    resolve_entitlements = ResolveEntitlementsService(
        unit_of_work_factory,
        clock,
        SubscriptionValidityPolicy(datetime_validator),
    )

    adapter = build_fastapi_subscription_adapter(
        authenticated_actor_dependency=StaticAuthenticatedActorDependency("admin-1"),
        authorizer=StoreSubscriptionAuthorizer("admin-1", {"store-1"}),
        create_plan=create_plan,
        get_plan=get_plan,
        change_plan_status=change_plan_status,
        create_subscription=create_subscription,
        get_subscription=get_subscription,
        start_trial=start_trial,
        activate_subscription=activate_subscription,
        cancel_subscription=cancel_subscription,
        renew_subscription=renew_subscription,
        record_usage=record_usage,
        get_usage_counter=get_usage_counter,
        resolve_entitlements=resolve_entitlements,
    )
    app = FastAPI(title="Subscription Consumer Example")
    adapter.install(app)
    payment_events = PaidSubscriptionEventHandler(activate_subscription, renew_subscription)
    return SubscriptionRuntime(
        app=app,
        database=database,
        adapter=adapter,
        payment_events=payment_events,
    )
