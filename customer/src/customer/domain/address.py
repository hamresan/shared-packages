from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class CustomerAddress:
    id: UUID
    business_id: UUID
    customer_id: UUID
    label: str
    country_code: str
    line1: str
    city: str
    region: str | None
    postal_code: str | None
    is_default: bool

    def change_details(
        self,
        label: str,
        country_code: str,
        line1: str,
        city: str,
        region: str | None,
        postal_code: str | None,
    ) -> None:
        self.label = label
        self.country_code = country_code
        self.line1 = line1
        self.city = city
        self.region = region
        self.postal_code = postal_code

    def make_default(self) -> None:
        self.is_default = True
