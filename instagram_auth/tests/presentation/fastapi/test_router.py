"""Behavior tests for the optional FastAPI adapter."""

from asyncio import run

from instagram_auth.baseline import InstagramConnectionState, InstagramPermission
from tests.presentation.fastapi.builders import (
    REDIRECT_URI,
    build_connection,
    build_test_context,
)


def test_login_start_maps_http_input_to_authorization_use_case() -> None:
    context = build_test_context(owner_user_id=None)

    response = context.client.get("/instagram/auth/start")

    assert response.status_code == 200
    assert response.json()["authorization_url"].endswith("state=secure-state")
    assert context.url_builder.redirect_uri == REDIRECT_URI


def test_connect_account_requires_host_owner_and_preserves_optional_permissions() -> None:
    context = build_test_context(owner_user_id="owner-1")

    response = context.client.get(
        "/instagram/auth/start",
        params={
            "flow": "connect_account",
            "optional_permissions": InstagramPermission.MANAGE_INSIGHTS.value,
        },
    )

    assert response.status_code == 200
    assert InstagramPermission.MANAGE_INSIGHTS in context.url_builder.permissions


def test_connect_account_returns_host_authentication_error_when_owner_is_missing() -> None:
    context = build_test_context(owner_user_id=None)

    response = context.client.get(
        "/instagram/auth/start",
        params={"flow": "connect_account"},
    )

    assert response.status_code == 401


def test_callback_validates_state_then_delegates_host_response_behavior() -> None:
    context = build_test_context(owner_user_id=None)
    start_response = context.client.get("/instagram/auth/start")
    assert start_response.status_code == 200

    response = context.client.get(
        "/instagram/auth/callback",
        params={"code": "authorization-code", "state": "secure-state"},
    )

    assert response.status_code == 200
    assert response.json() == {"handled": True}
    assert context.callback_responder.authorization_code == "authorization-code"
    assert context.callback_responder.authorization is not None


def test_callback_rejects_invalid_state_before_host_callback_responder() -> None:
    context = build_test_context(owner_user_id=None)

    response = context.client.get(
        "/instagram/auth/callback",
        params={"code": "authorization-code", "state": "invalid-state"},
    )

    assert response.status_code == 400
    assert context.callback_responder.authorization_code is None


def test_list_connections_returns_only_authenticated_owners_connections() -> None:
    first = build_connection(1, "owner-1")
    second = build_connection(2, "owner-1")
    other = build_connection(3, "owner-2")
    context = build_test_context(connections=(first, second, other))

    response = context.client.get("/instagram/connections")

    assert response.status_code == 200
    assert {item["id"] for item in response.json()} == {
        str(first.id.value),
        str(second.id.value),
    }


def test_get_connection_uses_explicit_connection_id_and_rejects_cross_owner_access() -> None:
    owned = build_connection(4, "owner-1")
    other = build_connection(5, "owner-2")
    context = build_test_context(connections=(owned, other))

    owned_response = context.client.get(f"/instagram/connections/{owned.id.value}")
    other_response = context.client.get(f"/instagram/connections/{other.id.value}")

    assert owned_response.status_code == 200
    assert owned_response.json()["id"] == str(owned.id.value)
    assert other_response.status_code == 403


def test_get_connection_returns_not_found_for_unknown_connection_id() -> None:
    context = build_test_context()

    response = context.client.get(
        "/instagram/connections/00000000-0000-0000-0000-000000000099"
    )

    assert response.status_code == 404


def test_disconnect_changes_only_selected_connection() -> None:
    selected = build_connection(6, "owner-1")
    sibling = build_connection(7, "owner-1")
    context = build_test_context(connections=(selected, sibling))

    response = context.client.post(
        f"/instagram/connections/{selected.id.value}/disconnect"
    )

    assert response.status_code == 200
    assert response.json()["status"] == InstagramConnectionState.DISCONNECTED.value
    assert context.store.connections[selected.id].status is InstagramConnectionState.DISCONNECTED
    assert context.store.connections[sibling.id] == sibling


def test_reconnect_updates_selected_connection_without_creating_duplicate() -> None:
    selected = build_connection(8, "owner-1")
    sibling = build_connection(9, "owner-1")
    context = build_test_context(connections=(selected, sibling))

    response = context.client.post(
        f"/instagram/connections/{selected.id.value}/reconnect"
    )

    assert response.status_code == 200
    assert response.json()["id"] == str(selected.id.value)
    assert response.json()["status"] == InstagramConnectionState.AUTHORIZING.value
    assert len(context.store.connections) == 2
    assert context.store.connections[sibling.id] == sibling


def test_authorization_state_is_consumed_once_through_callback_route() -> None:
    context = build_test_context(owner_user_id=None)
    context.client.get("/instagram/auth/start")

    first = context.client.get(
        "/instagram/auth/callback",
        params={"code": "first-code", "state": "secure-state"},
    )
    second = context.client.get(
        "/instagram/auth/callback",
        params={"code": "second-code", "state": "secure-state"},
    )

    assert first.status_code == 200
    assert second.status_code == 400
    assert run(context.state_store.consume("secure-state")) is None
