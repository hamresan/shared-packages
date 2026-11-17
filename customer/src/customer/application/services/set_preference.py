from customer.application.contracts import CustomerUnitOfWorkFactory, IdentifierGenerator
from customer.application.mapping.preference_result import PreferenceResultMapper
from customer.application.models.preference_commands import SetPreferenceCommand
from customer.application.models.preference_result import PreferenceResult
from customer.application.permissions import CustomerPermission
from customer.application.policies.detail_access import CustomerDetailAccessPolicy
from customer.application.validation.preference import PreferenceValidator
from customer.domain.preference import CustomerPreference


class SetPreferenceService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        access: CustomerDetailAccessPolicy,
        validator: PreferenceValidator,
        identifiers: IdentifierGenerator,
        mapper: PreferenceResultMapper,
    ) -> None:
        self.uow = uow
        self.access = access
        self.validator = validator
        self.identifiers = identifiers
        self.mapper = mapper

    async def execute(self, command: SetPreferenceCommand) -> PreferenceResult:
        key = self.validator.validate(command.key, command.value)
        async with self.uow(command.business_id) as transaction:
            await self.access.require(
                transaction.customers,
                command.business_id,
                command.customer_id,
                command.actor,
                CustomerPermission.UPDATE,
                mutating=True,
            )
            existing = await transaction.preferences.get(
                command.business_id, command.customer_id, key
            )
            preference = CustomerPreference(
                existing.id if existing else self.identifiers.new_id(),
                command.business_id,
                command.customer_id,
                key,
                command.value,
            )
            await transaction.preferences.upsert(preference)
            await transaction.commit()
            return self.mapper.to_result(preference)
