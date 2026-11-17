from customer.application.models.address_result import AddressResult
from customer.domain.address import CustomerAddress


class AddressResultMapper:
    def to_result(self, address: CustomerAddress) -> AddressResult:
        return AddressResult(
            address.id,
            address.business_id,
            address.customer_id,
            address.label,
            address.country_code,
            address.line1,
            address.city,
            address.region,
            address.postal_code,
            address.is_default,
        )
