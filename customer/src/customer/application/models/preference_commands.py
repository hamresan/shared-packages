from dataclasses import dataclass

from customer.application.models.profile_detail_commands import CustomerDetailsQuery
from customer.domain.preference import PreferenceValue


@dataclass(frozen=True, slots=True)
class SetPreferenceCommand(CustomerDetailsQuery):
    key: str
    value: PreferenceValue


@dataclass(frozen=True, slots=True)
class RemovePreferenceCommand(CustomerDetailsQuery):
    key: str
