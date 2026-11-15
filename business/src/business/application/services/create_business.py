from business.application.actor import AuthenticatedActor
from business.application.contracts import BusinessUnitOfWorkFactory, Clock
from business.application.dto import CreateBusinessCommand
from business.application.factories import BusinessFactory, OwnerMembershipFactory
from business.application.validators import CreateBusinessCommandValidator
from business.domain.business import Business


class CreateBusinessService:
    def __init__(
        self,
        unit_of_work_factory: BusinessUnitOfWorkFactory,
        validator: CreateBusinessCommandValidator,
        business_factory: BusinessFactory,
        membership_factory: OwnerMembershipFactory,
        clock: Clock,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._validator = validator
        self._business_factory = business_factory
        self._membership_factory = membership_factory
        self._clock = clock

    async def execute(
        self, command: CreateBusinessCommand, *, actor: AuthenticatedActor
    ) -> Business:
        validated = self._validator.validate(command)
        now = self._clock.now()
        business = self._business_factory.create(validated, created_at=now)
        owner = self._membership_factory.create(
            business_id=business.id, user_id=actor.user_id, created_at=now
        )
        async with self._unit_of_work_factory() as unit_of_work:
            await unit_of_work.businesses.add(business)
            await unit_of_work.memberships.add(owner)
            await unit_of_work.commit()
        return business
