from uuid import uuid4

from fastapi import FastAPI

from store.presentation import build_fastapi_store_adapter
from tests.support.presentation import (
    ActorBuilder,
    FakeAuthenticatedActorDependency,
    FakeOwnedStoreReader,
    FakeStoreCreator,
    FakeStoreReader,
    StoreHttpTestClient,
    StorePresentationBuilder,
    build_store_http_test_client,
)


def build_client(
    actor_dependency: FakeAuthenticatedActorDependency,
    store_creator: FakeStoreCreator,
    owned_store_reader: FakeOwnedStoreReader,
    store_reader: FakeStoreReader,
) -> StoreHttpTestClient:
    app = FastAPI()
    adapter = build_fastapi_store_adapter(
        authenticated_actor_dependency=actor_dependency,
        store_creator=store_creator,
        owned_store_reader=owned_store_reader,
        store_reader=store_reader,
    )
    adapter.install(app)
    return build_store_http_test_client(app)


def test_create_store_uses_authenticated_actor_owner_id() -> None:
    actor = ActorBuilder().build()
    store = StorePresentationBuilder().build()
    creator = FakeStoreCreator(store)
    client = build_client(
        FakeAuthenticatedActorDependency(actor),
        creator,
        FakeOwnedStoreReader(store),
        FakeStoreReader(store),
    )

    response = client.post(
        "/stores",
        json={
            "name": "Demo",
            "business_type": "retail",
            "primary_language": "en",
            "country_code": "OM",
            "base_currency_code": "OMR",
        },
    )

    assert response.status_code == 201
    assert creator.received_command is not None
    assert creator.received_command.owner_user_id == actor.user_id
    assert response.json()["owner_user_id"] == str(actor.user_id)


def test_create_store_rejects_owner_user_id_from_request_body() -> None:
    actor = ActorBuilder().build()
    store = StorePresentationBuilder().build()
    client = build_client(
        FakeAuthenticatedActorDependency(actor),
        FakeStoreCreator(store),
        FakeOwnedStoreReader(store),
        FakeStoreReader(store),
    )

    response = client.post(
        "/stores",
        json={
            "owner_user_id": str(uuid4()),
            "name": "Demo",
            "business_type": "retail",
            "primary_language": "en",
            "country_code": "OM",
            "base_currency_code": "OMR",
        },
    )

    assert response.status_code == 422


def test_get_owned_store_uses_authenticated_actor() -> None:
    actor = ActorBuilder().build()
    store = StorePresentationBuilder().build()
    reader = FakeOwnedStoreReader(store)
    client = build_client(
        FakeAuthenticatedActorDependency(actor),
        FakeStoreCreator(store),
        reader,
        FakeStoreReader(store),
    )

    response = client.get("/stores/me")

    assert response.status_code == 200
    assert reader.received_query is not None
    assert reader.received_query.owner_user_id == actor.user_id


def test_get_store_by_id_uses_store_reader_and_requires_authentication() -> None:
    store = StorePresentationBuilder().build()
    reader = FakeStoreReader(store)
    client = build_client(
        FakeAuthenticatedActorDependency(ActorBuilder().build()),
        FakeStoreCreator(store),
        FakeOwnedStoreReader(store),
        reader,
    )

    response = client.get(f"/stores/{store.id}")

    assert response.status_code == 200
    assert reader.received_query is not None
    assert reader.received_query.store_id == store.id


def test_routes_use_host_authentication_dependency() -> None:
    store = StorePresentationBuilder().build()
    client = build_client(
        FakeAuthenticatedActorDependency(None),
        FakeStoreCreator(store),
        FakeOwnedStoreReader(store),
        FakeStoreReader(store),
    )

    assert client.get("/stores/me").status_code == 401
    assert client.get(f"/stores/{store.id}").status_code == 401


def test_get_owned_store_maps_missing_store_to_404() -> None:
    client = build_client(
        FakeAuthenticatedActorDependency(ActorBuilder().build()),
        FakeStoreCreator(StorePresentationBuilder().build()),
        FakeOwnedStoreReader(None),
        FakeStoreReader(None),
    )

    response = client.get("/stores/me")

    assert response.status_code == 404
    assert response.json() == {"detail": "Store not found"}


def test_create_store_maps_application_value_error_to_422() -> None:
    store = StorePresentationBuilder().build()
    creator = FakeStoreCreator(store)
    creator.error = ValueError("Owner already has a store")
    client = build_client(
        FakeAuthenticatedActorDependency(ActorBuilder().build()),
        creator,
        FakeOwnedStoreReader(store),
        FakeStoreReader(store),
    )

    response = client.post(
        "/stores",
        json={
            "name": "Demo",
            "business_type": "retail",
            "primary_language": "en",
            "country_code": "OM",
            "base_currency_code": "OMR",
        },
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Owner already has a store"}


def test_get_store_maps_missing_store_to_404() -> None:
    store = StorePresentationBuilder().build()
    client = build_client(
        FakeAuthenticatedActorDependency(ActorBuilder().build()),
        FakeStoreCreator(store),
        FakeOwnedStoreReader(store),
        FakeStoreReader(None),
    )

    response = client.get(f"/stores/{uuid4()}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Store not found"}


def test_adapter_exposes_router() -> None:
    store = StorePresentationBuilder().build()
    adapter = build_fastapi_store_adapter(
        authenticated_actor_dependency=FakeAuthenticatedActorDependency(ActorBuilder().build()),
        store_creator=FakeStoreCreator(store),
        owned_store_reader=FakeOwnedStoreReader(store),
        store_reader=FakeStoreReader(store),
    )

    assert adapter.router() is adapter.store_router
