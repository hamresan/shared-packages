from uuid import uuid4

from customer import CreateCustomerCommand, ExternalIdentityKey, LinkExternalIdentityCommand
from customer.presentation.http.dto import ExternalIdentityLookupBody
from customer.presentation.http.mappers import ExternalIdentityHttpMapper
from tests.support.factories.customer_module import build_actor, build_customer_module
from tests.support.fakes.external_evidence import FakeExternalEvidenceVerifier


async def test_external_identity_http_mapper_preserves_scope_and_verified_projection() -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    customer = await module.customers.create.execute(
        CreateCustomerCommand(actor.business_id, actor)
    )
    key = ExternalIdentityKey(actor.business_id, "telegram", "bot", "sender")
    verifier = module.config.external_evidence_verifier
    assert isinstance(verifier, FakeExternalEvidenceVerifier)
    verifier.register("trusted", key)
    await module.external_identities.link.execute(
        LinkExternalIdentityCommand(actor, key, customer.id, "trusted")
    )

    mapper = ExternalIdentityHttpMapper()
    query = mapper.to_find_query(
        actor.business_id,
        actor,
        ExternalIdentityLookupBody(
            provider="telegram", channel_account_id="bot", external_user_id="sender"
        ),
    )
    assert query.actor == actor and query.key == key
    resolved = await module.external_identities.find.execute(query)
    assert resolved is not None
    response = mapper.to_response(resolved)
    assert response.customer_id == customer.id
    assert "notes" not in response.model_dump()
