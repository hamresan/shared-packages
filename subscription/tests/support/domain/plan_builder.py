from uuid import UUID

from subscription import (
    BooleanEntitlementValue,
    EntitlementKey,
    Plan,
    PlanCode,
    PlanEntitlement,
    PlanStatus,
    SubscriptionType,
)


class PlanBuilder:
    def __init__(self) -> None:
        self._id = UUID("11111111-1111-1111-1111-111111111111")
        self._code = PlanCode("pro")
        self._name = "Pro"
        self._description: str | None = "Professional plan"
        self._subscription_type = SubscriptionType.BASE
        self._status = PlanStatus.ACTIVE
        self._entitlements: tuple[PlanEntitlement, ...] = (
            PlanEntitlement(
                key=EntitlementKey("analytics.advanced"),
                value=BooleanEntitlementValue(True),
            ),
        )

    def with_name(self, name: str) -> "PlanBuilder":
        self._name = name
        return self

    def with_description(self, description: str | None) -> "PlanBuilder":
        self._description = description
        return self

    def with_entitlements(self, *entitlements: PlanEntitlement) -> "PlanBuilder":
        self._entitlements = tuple(entitlements)
        return self

    def build(self) -> Plan:
        return Plan(
            id=self._id,
            code=self._code,
            name=self._name,
            description=self._description,
            subscription_type=self._subscription_type,
            status=self._status,
            entitlements=self._entitlements,
        )
