from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest

from business.application import AuthenticatedActor


def test_authenticated_actor_carries_a_trusted_external_identity() -> None:
    user_id = UUID("ddc43236-d4b7-495c-a09d-3e15ddca5d82")

    actor = AuthenticatedActor(user_id=user_id)

    assert actor.user_id == user_id


def test_authenticated_actor_is_immutable() -> None:
    actor = AuthenticatedActor(user_id=UUID("ddc43236-d4b7-495c-a09d-3e15ddca5d82"))

    with pytest.raises(FrozenInstanceError):
        actor.__setattr__("user_id", UUID("21b7b74e-e6b2-4936-b327-03f3f86bb0d5"))
