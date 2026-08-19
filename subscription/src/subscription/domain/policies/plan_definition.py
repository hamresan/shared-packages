from subscription.domain.entities.plan import Plan


class PlanDefinitionPolicy:
    def validate(self, plan: Plan) -> None:
        if not plan.name or plan.name != plan.name.strip():
            raise ValueError("plan name must be a non-empty trimmed string")
        if len(plan.name) > 120:
            raise ValueError("plan name must not exceed 120 characters")
        if plan.description is not None and plan.description != plan.description.strip():
            raise ValueError("plan description must be trimmed when provided")

        entitlement_keys = [entitlement.key.value for entitlement in plan.entitlements]
        if len(entitlement_keys) != len(set(entitlement_keys)):
            raise ValueError("plan entitlement keys must be unique")
