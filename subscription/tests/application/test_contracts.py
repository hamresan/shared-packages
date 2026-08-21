from uuid import UUID

from subscription.application import Clock, IdentifierGenerator, SubscriptionUnitOfWorkFactory
from tests.support.application.fakes import (
    FakeSubscriptionUnitOfWorkFactory,
    FixedClock,
    FixedIdentifierGenerator,
)


def test_runtime_fakes_explicitly_implement_public_contracts() -> None:
    clock: Clock = FixedClock()
    identifier_generator: IdentifierGenerator = FixedIdentifierGenerator(
        UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    )
    unit_of_work_factory: SubscriptionUnitOfWorkFactory = FakeSubscriptionUnitOfWorkFactory()

    assert clock.now().tzinfo is not None
    assert identifier_generator.new_id().version == 4
    assert unit_of_work_factory() is not None
