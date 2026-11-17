from uuid import uuid4

import pytest

from customer import CustomerActor, CustomerActorType


def test_actor_preserves_trusted_host_identity_and_scope() -> None:
    actor_id, business_id = uuid4(), uuid4()
    actor = CustomerActor(actor_id, CustomerActorType.SERVICE, business_id)

    assert actor.actor_id == actor_id
    assert actor.business_id == business_id
    assert actor.actor_type is CustomerActorType.SERVICE


def test_actor_is_immutable() -> None:
    actor = CustomerActor(uuid4(), CustomerActorType.USER, uuid4())

    with pytest.raises(AttributeError):
        actor.business_id = uuid4()  # type: ignore[misc]
