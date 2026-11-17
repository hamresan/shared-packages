"""Map Customer HTTP payloads to and from application contracts."""

from uuid import UUID

from customer.application.actor import CustomerActor
from customer.application.models import (
    CreateCustomerCommand,
    CustomerResult,
    GetCustomerQuery,
    UpdateCustomerCommand,
)
from customer.presentation.http.dto import (
    CustomerCreateBody,
    CustomerResponse,
    CustomerUpdateBody,
)


class CustomerHttpMapper:
    @staticmethod
    def to_create_command(
        business_id: UUID,
        actor: CustomerActor,
        body: CustomerCreateBody,
        idempotency_key: str | None,
    ) -> CreateCustomerCommand:
        return CreateCustomerCommand(business_id, actor, body.display_name, idempotency_key)

    @staticmethod
    def to_get_query(
        business_id: UUID, actor: CustomerActor, customer_id: UUID
    ) -> GetCustomerQuery:
        return GetCustomerQuery(business_id, actor, customer_id)

    @staticmethod
    def to_update_command(
        business_id: UUID,
        actor: CustomerActor,
        customer_id: UUID,
        body: CustomerUpdateBody,
    ) -> UpdateCustomerCommand:
        return UpdateCustomerCommand(
            business_id, actor, customer_id, body.expected_version, body.display_name
        )

    @staticmethod
    def to_response(result: CustomerResult) -> CustomerResponse:
        return CustomerResponse.model_validate(result, from_attributes=True)
