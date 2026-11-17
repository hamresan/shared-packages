from dataclasses import dataclass

from customer.application.services.add_address import AddAddressService
from customer.application.services.list_addresses import ListAddressesService
from customer.application.services.remove_address import RemoveAddressService
from customer.application.services.set_default_address import SetDefaultAddressService
from customer.application.services.update_address import UpdateAddressService


@dataclass(frozen=True, slots=True)
class AddressUseCases:
    add: AddAddressService
    list: ListAddressesService
    update: UpdateAddressService
    set_default: SetDefaultAddressService
    remove: RemoveAddressService
