from uuid import UUID

from business import AuthenticatedActor, BranchAccessScope, BranchAddress, BusinessStatus


def test_public_primitives_are_importable_from_package_root() -> None:
    actor = AuthenticatedActor(user_id=UUID("c878c341-2e1f-4210-aad0-4ea4ca426a9b"))
    address = BranchAddress(city="Muscat")

    assert actor.user_id.version == 4
    assert address.city == "Muscat"
    assert BusinessStatus.ACTIVE.value == "active"
    assert BranchAccessScope.SELECTED.value == "selected"
