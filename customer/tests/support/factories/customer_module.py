from uuid import UUID, uuid4

from customer import CustomerActor, CustomerActorType, CustomerModule, CustomerModuleConfig
from tests.support.fakes.authorization import AllowCustomerAuthorizer
from tests.support.fakes.clock import FixedClock
from tests.support.fakes.fingerprinter import FakeCustomerCreationFingerprinter
from tests.support.fakes.identifiers import RandomIdentifierGenerator
from tests.support.fakes.identity_verification import AcceptIdentityVerifier
from tests.support.fakes.unit_of_work import FakeCustomerUnitOfWorkFactory


def build_customer_module() -> tuple[CustomerModule, FakeCustomerUnitOfWorkFactory]:
    uow = FakeCustomerUnitOfWorkFactory()
    return (
        CustomerModule(
            CustomerModuleConfig(
                uow,
                AllowCustomerAuthorizer(),
                AcceptIdentityVerifier(),
                FixedClock(),
                RandomIdentifierGenerator(),
                FakeCustomerCreationFingerprinter(),
            )
        ),
        uow,
    )


def build_actor(business_id: UUID) -> CustomerActor:
    return CustomerActor(uuid4(), CustomerActorType.USER, business_id)
