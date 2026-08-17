from store.domain import StoreModerationStatus
from store.infrastructure.persistence.sqlalchemy import build_store_persistence_mapper
from tests.support.persistence import build_persistence_store


def test_store_persistence_mapper_round_trips_full_store() -> None:
    store = build_persistence_store()
    mapper = build_store_persistence_mapper()

    restored = mapper.to_domain(mapper.to_model(store))

    assert restored == store


def test_store_persistence_mapper_round_trips_optional_empty_values() -> None:
    store = build_persistence_store()
    store.address = None
    store.contacts = ()
    store.currencies = ()
    store.timezone = None
    store.working_schedule = None
    store.moderation_status = StoreModerationStatus.ACTIVE
    store.suspension_reason = None
    store.suspension_description = None
    store.suspended_by_actor_id = None
    store.suspended_at = None
    mapper = build_store_persistence_mapper()

    restored = mapper.to_domain(mapper.to_model(store))

    assert restored == store
