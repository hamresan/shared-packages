from customer.domain.preference import CustomerPreference
from customer.infrastructure.persistence.sqlalchemy.models import CustomerPreferenceModel


class PreferenceMapper:
    @staticmethod
    def to_domain(row: CustomerPreferenceModel) -> CustomerPreference:
        return CustomerPreference(
            id=row.id,
            business_id=row.business_id,
            customer_id=row.customer_id,
            key=row.key,
            value=row.value,
        )

    @staticmethod
    def to_row(value: CustomerPreference) -> CustomerPreferenceModel:
        return CustomerPreferenceModel(
            id=value.id,
            business_id=value.business_id,
            customer_id=value.customer_id,
            key=value.key,
            value=value.value,
        )
