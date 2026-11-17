"""Optional thin HTTP adapter with host-controlled trusted actor resolution."""

from collections.abc import Awaitable, Callable
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException

from customer.application.actor import CustomerActor
from customer.application.models import (
    CreateCustomerCommand,
    GetCustomerQuery,
    UpdateCustomerCommand,
)
from customer.application.models.external_identity_commands import FindExternalIdentityQuery
from customer.bootstrap import CustomerModule
from customer.domain.errors import CustomerError
from customer.domain.external_identity import ExternalIdentityKey
from customer.presentation.http.dto import (
    CustomerCreateBody,
    CustomerResponse,
    CustomerUpdateBody,
    ExternalIdentityLookupBody,
    ExternalIdentityResponse,
)
from customer.presentation.http.error_mapping import customer_http_error


def create_customer_router(
    module: CustomerModule,
    trusted_actor: Callable[..., CustomerActor | Awaitable[CustomerActor]],
) -> APIRouter:
    """Compose routes without selecting authentication or authorization providers.

    ``trusted_actor`` must authenticate the request and derive its business scope.
    It must never trust caller-provided actor IDs or permission claims.
    """
    router = APIRouter(prefix="/businesses/{business_id}/customers", tags=["customers"])
    actor_dependency = Depends(trusted_actor)

    @router.post("", response_model=CustomerResponse, status_code=201)
    async def create(
        business_id: UUID,
        body: CustomerCreateBody,
        actor: CustomerActor = actor_dependency,
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> CustomerResponse:
        try:
            result = await module.customers.create.execute(
                CreateCustomerCommand(business_id, actor, body.display_name, idempotency_key)
            )
            return CustomerResponse.model_validate(result, from_attributes=True)
        except CustomerError as error:
            raise customer_http_error(error) from error

    @router.get("/{customer_id}", response_model=CustomerResponse)
    async def get(
        business_id: UUID,
        customer_id: UUID,
        actor: CustomerActor = actor_dependency,
    ) -> CustomerResponse:
        try:
            result = await module.customers.get.execute(
                GetCustomerQuery(business_id, actor, customer_id)
            )
            return CustomerResponse.model_validate(result, from_attributes=True)
        except CustomerError as error:
            raise customer_http_error(error) from error

    @router.patch("/{customer_id}", response_model=CustomerResponse)
    async def update(
        business_id: UUID,
        customer_id: UUID,
        body: CustomerUpdateBody,
        actor: CustomerActor = actor_dependency,
    ) -> CustomerResponse:
        try:
            result = await module.customers.update.execute(
                UpdateCustomerCommand(
                    business_id, actor, customer_id, body.expected_version, body.display_name
                )
            )
            return CustomerResponse.model_validate(result, from_attributes=True)
        except CustomerError as error:
            raise customer_http_error(error) from error

    @router.post("/identities/resolve", response_model=ExternalIdentityResponse)
    async def find_external(
        business_id: UUID,
        body: ExternalIdentityLookupBody,
        actor: CustomerActor = actor_dependency,
    ) -> ExternalIdentityResponse:
        try:
            result = await module.external_identities.find.execute(
                FindExternalIdentityQuery(
                    actor,
                    ExternalIdentityKey(
                        business_id, body.provider, body.channel_account_id, body.external_user_id
                    ),
                )
            )
            if result is None:
                raise HTTPException(status_code=404, detail="customer_unavailable")
            return ExternalIdentityResponse.model_validate(result, from_attributes=True)
        except CustomerError as error:
            raise customer_http_error(error) from error

    return router
