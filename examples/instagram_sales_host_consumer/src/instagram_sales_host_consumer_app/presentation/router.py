"""Thin FastAPI route demonstrating explicit selected-connection reads."""

from fastapi import APIRouter

from instagram_api.application.contracts import InstagramAccountReader
from instagram_api.domain import InstagramConnectionId


def create_reference_router(account_reader: InstagramAccountReader) -> APIRouter:
    """Create a minimal host route for selected-account profile reads."""

    router = APIRouter()

    async def get_account(connection_id: str) -> dict[str, str | None]:
        account = await account_reader.get_account(
            InstagramConnectionId(connection_id)
        )
        return {
            "id": str(account.id),
            "username": account.username,
            "biography": account.biography,
        }

    router.add_api_route(
        "/instagram/connections/{connection_id}/account",
        get_account,
        methods=["GET"],
    )
    return router
