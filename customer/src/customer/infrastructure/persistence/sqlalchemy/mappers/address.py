from customer.domain.address import CustomerAddress
from customer.infrastructure.persistence.sqlalchemy.models import CustomerAddressModel


class AddressMapper:
    @staticmethod
    def to_domain(row: CustomerAddressModel) -> CustomerAddress:
        return CustomerAddress(
            id=row.id,
            business_id=row.business_id,
            customer_id=row.customer_id,
            label=row.label,
            country_code=row.country_code,
            line1=row.line1,
            city=row.city,
            region=row.region,
            postal_code=row.postal_code,
            is_default=row.is_default,
        )

    @staticmethod
    def to_row(value: CustomerAddress) -> CustomerAddressModel:
        return CustomerAddressModel(
            id=value.id,
            business_id=value.business_id,
            customer_id=value.customer_id,
            label=value.label,
            country_code=value.country_code,
            line1=value.line1,
            city=value.city,
            region=value.region,
            postal_code=value.postal_code,
            is_default=value.is_default,
        )
