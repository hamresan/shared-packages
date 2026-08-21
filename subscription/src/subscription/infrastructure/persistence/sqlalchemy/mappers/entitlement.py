from subscription.domain import (
    BooleanEntitlementValue,
    DecimalEntitlementValue,
    EntitlementKey,
    EntitlementValueType,
    IntegerEntitlementValue,
    PlanEntitlement,
    StringEntitlementValue,
    UnlimitedEntitlementValue,
)
from subscription.infrastructure.persistence.sqlalchemy.models import PlanEntitlementModel


class EntitlementPersistenceMapper:
    def to_model(self, plan_id: str, entitlement: PlanEntitlement) -> PlanEntitlementModel:
        model = PlanEntitlementModel(
            plan_id=plan_id,
            key=entitlement.key.value,
            value_type=entitlement.value.value_type.value,
        )
        value = entitlement.value
        if isinstance(value, BooleanEntitlementValue):
            model.boolean_value = value.value
        elif isinstance(value, IntegerEntitlementValue):
            model.integer_value = value.value
        elif isinstance(value, DecimalEntitlementValue):
            model.decimal_value = value.value
        elif isinstance(value, StringEntitlementValue):
            model.string_value = value.value
        return model

    def to_domain(self, model: PlanEntitlementModel) -> PlanEntitlement:
        value_type = EntitlementValueType(model.value_type)
        if value_type is EntitlementValueType.BOOLEAN:
            value = BooleanEntitlementValue(bool(model.boolean_value))
        elif value_type is EntitlementValueType.INTEGER:
            value = IntegerEntitlementValue(int(model.integer_value or 0))
        elif value_type is EntitlementValueType.DECIMAL:
            if model.decimal_value is None:
                raise ValueError("decimal entitlement persistence value is missing")
            value = DecimalEntitlementValue(model.decimal_value)
        elif value_type is EntitlementValueType.STRING:
            value = StringEntitlementValue(model.string_value or "")
        else:
            value = UnlimitedEntitlementValue()
        return PlanEntitlement(key=EntitlementKey(model.key), value=value)
