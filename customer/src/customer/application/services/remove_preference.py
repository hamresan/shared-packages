from customer.application.contracts import CustomerUnitOfWorkFactory
from customer.application.models.preference_commands import RemovePreferenceCommand
from customer.application.permissions import CustomerPermission
from customer.application.policies.detail_access import CustomerDetailAccessPolicy
from customer.application.validation.preference import PreferenceValidator
from customer.domain.errors import CustomerNotFoundError


class RemovePreferenceService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        access: CustomerDetailAccessPolicy,
        validator: PreferenceValidator,
    ) -> None:
        self.uow = uow
        self.access = access
        self.validator = validator

    async def execute(self, command: RemovePreferenceCommand) -> None:
        key = self.validator.normalize_key(command.key)
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
            if existing is None:
                raise CustomerNotFoundError("Preference was not found")
            await transaction.preferences.remove(command.business_id, command.customer_id, key)
            await transaction.commit()
