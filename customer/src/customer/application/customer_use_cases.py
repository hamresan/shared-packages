"""Small use-case group exposed by the public facade."""

from dataclasses import dataclass

from customer.application.services.archive_customer import ArchiveCustomerService
from customer.application.services.create_customer import CreateCustomerService
from customer.application.services.erase_customer import EraseCustomerService
from customer.application.services.get_customer import GetCustomerService
from customer.application.services.reactivate_customer import ReactivateCustomerService
from customer.application.services.search_customers import SearchCustomersService
from customer.application.services.update_customer import UpdateCustomerService


@dataclass(frozen=True, slots=True)
class CustomerUseCases:
    create: CreateCustomerService
    erase: EraseCustomerService
    get: GetCustomerService
    update: UpdateCustomerService
    archive: ArchiveCustomerService
    reactivate: ReactivateCustomerService
    search: SearchCustomersService
