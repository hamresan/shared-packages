from subscription.application.contracts import Clock, SubscriptionUnitOfWorkFactory
from subscription.application.dto import EntitlementGrant
from subscription.domain import EntitlementKey, SubjectReference, SubscriptionValidityPolicy


class ResolveEntitlementsService:
    def __init__(
        self,
        unit_of_work_factory: SubscriptionUnitOfWorkFactory,
        clock: Clock,
        validity_policy: SubscriptionValidityPolicy,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock
        self._validity_policy = validity_policy

    async def execute(
        self,
        subject: SubjectReference,
        key: EntitlementKey,
    ) -> tuple[EntitlementGrant, ...]:
        now = self._clock.now()
        grants: list[EntitlementGrant] = []

        async with self._unit_of_work_factory() as unit_of_work:
            subscriptions = await unit_of_work.subscriptions.list_for_subject(subject)
            for subscription in subscriptions:
                if not self._validity_policy.is_valid(subscription, now):
                    continue
                plan = await unit_of_work.plans.get_by_id(subscription.plan_id)
                if plan is None:
                    continue
                for entitlement in plan.entitlements:
                    if entitlement.key == key:
                        grants.append(
                            EntitlementGrant(
                                subscription_id=subscription.id,
                                plan_id=plan.id,
                                value=entitlement.value,
                            )
                        )
        return tuple(grants)
