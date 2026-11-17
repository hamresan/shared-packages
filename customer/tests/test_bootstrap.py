from customer import CustomerModule, CustomerModuleConfig
from tests.support.fakes.authorization import AllowCustomerAuthorizer
from tests.support.fakes.identity_verification import AcceptIdentityVerifier
from tests.support.fakes.unit_of_work import FakeCustomerUnitOfWorkFactory


def test_module_uses_explicit_injected_dependencies() -> None:
    uow = FakeCustomerUnitOfWorkFactory()
    authorizer = AllowCustomerAuthorizer()
    verifier = AcceptIdentityVerifier()
    config = CustomerModuleConfig(uow, authorizer, verifier)

    module = CustomerModule(config)

    assert module.config.unit_of_work_factory is uow
    assert module.config.authorizer is authorizer
    assert module.config.identity_verifier is verifier
