from business.application.actor import AuthenticatedActor
from business.application.contracts import BusinessUnitOfWorkFactory, Clock
from business.application.dto import UpdateBusinessCommand
from business.application.policies import BusinessAccessPolicy
from business.application.validators import UpdateBusinessCommandValidator
from business.domain.business import Business
from business.domain.errors import BusinessNotFoundError


class UpdateBusinessService:
    def __init__(
        self,
        unit_of_work_factory: BusinessUnitOfWorkFactory,
        access_policy: BusinessAccessPolicy,
        validator: UpdateBusinessCommandValidator,
        clock: Clock,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._access_policy = access_policy
        self._validator = validator
        self._clock = clock

    async def execute(
        self, command: UpdateBusinessCommand, *, actor: AuthenticatedActor
    ) -> Business:
        async with self._unit_of_work_factory() as unit_of_work:
            membership = await unit_of_work.memberships.get_by_business_and_user(
                command.business_id, actor.user_id
            )
            self._access_policy.require_owner(membership)
            business = await unit_of_work.businesses.get_by_id(command.business_id)
            if business is None:
                raise BusinessNotFoundError("Business was not found")
            validated = self._validator.validate(command)
            business.update_profile(
                name=validated.name,
                business_type=validated.business_type,
                updated_at=self._clock.now(),
            )
            await unit_of_work.businesses.save(business)
            await unit_of_work.commit()
            return business
