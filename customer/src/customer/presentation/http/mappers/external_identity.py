"""Map exact provider identity HTTP payloads to and from application contracts."""

from uuid import UUID

from customer.application.actor import CustomerActor
from customer.application.models.external_identity_commands import FindExternalIdentityQuery
from customer.application.models.identity_resolution import CustomerResolution
from customer.domain.external_identity import ExternalIdentityKey
from customer.presentation.http.dto import ExternalIdentityLookupBody, ExternalIdentityResponse


class ExternalIdentityHttpMapper:
    @staticmethod
    def to_find_query(
        business_id: UUID, actor: CustomerActor, body: ExternalIdentityLookupBody
    ) -> FindExternalIdentityQuery:
        return FindExternalIdentityQuery(
            actor,
            ExternalIdentityKey(
                business_id, body.provider, body.channel_account_id, body.external_user_id
            ),
        )

    @staticmethod
    def to_response(result: CustomerResolution) -> ExternalIdentityResponse:
        return ExternalIdentityResponse.model_validate(result, from_attributes=True)
