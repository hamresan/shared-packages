from store.presentation.mappers import StoreResponseMapper, StoreValueObjectResponseMapper
from tests.support.presentation import StorePresentationBuilder


def test_response_mapper_maps_nested_store_values() -> None:
    store = StorePresentationBuilder().build()

    response = StoreResponseMapper(StoreValueObjectResponseMapper()).to_response(store)

    assert response.id == store.id
    assert response.address is not None
    assert response.address.city == "Muscat"
    assert response.contacts[0].type == "whatsapp"
    assert response.currencies[0].code == "OMR"
    assert response.working_schedule is not None
    assert response.working_schedule.monday is not None
    assert response.working_schedule.monday.opens_at == "09:00"


def test_response_mapper_handles_missing_optional_value_objects() -> None:
    store = StorePresentationBuilder().build()
    store.address = None
    store.working_schedule = None

    response = StoreResponseMapper(StoreValueObjectResponseMapper()).to_response(store)

    assert response.address is None
    assert response.working_schedule is None
