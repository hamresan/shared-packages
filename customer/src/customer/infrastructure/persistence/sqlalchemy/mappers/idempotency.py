from uuid import uuid4

from customer.application.contracts.idempotency_repository import CustomerCreationReceipt
from customer.infrastructure.persistence.sqlalchemy.models import CustomerCreationReceiptModel


class IdempotencyMapper:
    @staticmethod
    def to_domain(row: CustomerCreationReceiptModel) -> CustomerCreationReceipt:
        return CustomerCreationReceipt(
            business_id=row.business_id,
            key=row.key,
            fingerprint=row.fingerprint,
            customer_id=row.customer_id,
        )

    @staticmethod
    def to_row(value: CustomerCreationReceipt) -> CustomerCreationReceiptModel:
        return CustomerCreationReceiptModel(
            id=uuid4(),
            business_id=value.business_id,
            key=value.key,
            fingerprint=value.fingerprint,
            customer_id=value.customer_id,
        )
