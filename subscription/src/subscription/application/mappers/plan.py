from subscription.application.contracts import IdentifierGenerator
from subscription.application.dto import CreatePlanCommand
from subscription.domain import EntitlementKey, Plan, PlanCode, PlanDefinitionPolicy, PlanEntitlement


class CreatePlanMapper:
    def __init__(
        self,
        identifier_generator: IdentifierGenerator,
        definition_policy: PlanDefinitionPolicy,
    ) -> None:
        self._identifier_generator = identifier_generator
        self._definition_policy = definition_policy

    def map(self, command: CreatePlanCommand) -> Plan:
        plan = Plan(
            id=self._identifier_generator.new_id(),
            code=PlanCode(command.code),
            name=command.name,
            description=command.description,
            subscription_type=command.subscription_type,
            status=command.status,
            entitlements=tuple(
                PlanEntitlement(
                    key=EntitlementKey(item.key),
                    value=item.value,
                )
                for item in command.entitlements
            ),
        )
        self._definition_policy.validate(plan)
        return plan
