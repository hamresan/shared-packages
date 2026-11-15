import pytest

from scheduling.application.models import TrustedActor


def test_trusted_actor_keeps_authoritative_identity() -> None:
    actor = TrustedActor(tenant_id="tenant-a", actor_id="actor-a")

    assert actor.tenant_id == "tenant-a"
    assert actor.actor_id == "actor-a"


@pytest.mark.parametrize(("tenant_id", "actor_id"), [(" ", "actor"), ("tenant", "")])
def test_trusted_actor_requires_both_identifiers(tenant_id: str, actor_id: str) -> None:
    with pytest.raises(ValueError):
        TrustedActor(tenant_id=tenant_id, actor_id=actor_id)
