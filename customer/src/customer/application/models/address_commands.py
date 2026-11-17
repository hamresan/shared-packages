from dataclasses import dataclass

from customer.application.models.profile_detail_commands import (
    CustomerChildMutation,
    CustomerDetailsQuery,
)


@dataclass(frozen=True, slots=True)
class AddAddressCommand(CustomerDetailsQuery):
    label: str
    country_code: str
    line1: str
    city: str
    region: str | None = None
    postal_code: str | None = None
    is_default: bool = False


@dataclass(frozen=True, slots=True)
class UpdateAddressCommand(CustomerChildMutation):
    label: str
    country_code: str
    line1: str
    city: str
    region: str | None = None
    postal_code: str | None = None
