from uuid import UUID, uuid4

from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel
from store.presentation.schemas import StoreResponse

from consumer_app import build_consumer_application


class CurrentUserResponse(BaseModel):
    user_id: UUID
    session_id: UUID


async def test_identity_principal_creates_and_reads_owned_store() -> None:
    application = await build_consumer_application()
    user_id = uuid4()
    issued_token = await application.token_adapter.issue(user_id, uuid4())
    headers = {"Authorization": f"Bearer {issued_token.token}"}

    try:
        async with AsyncClient(
            transport=ASGITransport(app=application.fastapi),
            base_url="http://test",
        ) as client:
            identity_response = await client.get("/identity/me", headers=headers)
            create_response = await client.post(
                "/stores",
                headers=headers,
                json={
                    "name": "Integration Store",
                    "business_type": "retail",
                    "primary_language": "en",
                    "country_code": "OM",
                    "base_currency_code": "OMR",
                },
            )
            owned_response = await client.get("/stores/me", headers=headers)

        identity_body = CurrentUserResponse.model_validate_json(identity_response.text)
        created_store = StoreResponse.model_validate_json(create_response.text)
        owned_store = StoreResponse.model_validate_json(owned_response.text)

        assert identity_response.status_code == 200
        assert identity_body.user_id == user_id
        assert create_response.status_code == 201
        assert created_store.owner_user_id == user_id
        assert owned_response.status_code == 200
        assert owned_store.id == created_store.id
    finally:
        await application.database.close()


async def test_store_routes_require_identity_authentication() -> None:
    application = await build_consumer_application()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=application.fastapi),
            base_url="http://test",
        ) as client:
            response = await client.get("/stores/me")

        assert response.status_code == 401
    finally:
        await application.database.close()
