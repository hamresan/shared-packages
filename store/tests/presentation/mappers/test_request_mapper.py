from uuid import uuid4

from store.presentation import AuthenticatedActor
from store.presentation.mappers import StoreRequestMapper
from store.presentation.schemas import CreateStoreRequest


def test_create_request_mapper_uses_authenticated_actor_as_owner() -> None:
    actor = AuthenticatedActor(user_id=uuid4())
    request = CreateStoreRequest(
        name="Demo",
        business_type="retail",
        primary_language="en",
        country_code="OM",
        base_currency_code="OMR",
    )

    command = StoreRequestMapper().to_create_command(request, actor)

    assert command.owner_user_id == actor.user_id
    assert command.name == "Demo"
