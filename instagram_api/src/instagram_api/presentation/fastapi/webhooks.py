"""Optional FastAPI adapter for Instagram webhooks."""

from fastapi import APIRouter, Header, HTTPException, Query, Request, Response

from instagram_api.application.webhooks import (
    InstagramWebhookAuthenticationError,
    InstagramWebhookHandshakeError,
    InstagramWebhookHandshakeService,
    InstagramWebhookProcessor,
)


def create_instagram_webhook_router(
    handshake_service: InstagramWebhookHandshakeService,
    processor: InstagramWebhookProcessor,
) -> APIRouter:
    """Create a thin FastAPI router around package-owned webhook use cases."""

    router = APIRouter()

    async def verify_webhook(
        mode: str | None = Query(default=None, alias="hub.mode"),
        verify_token: str | None = Query(default=None, alias="hub.verify_token"),
        challenge: str | None = Query(default=None, alias="hub.challenge"),
    ) -> Response:
        try:
            verified_challenge = handshake_service.verify(
                mode=mode,
                verify_token=verify_token,
                challenge=challenge,
            )
        except InstagramWebhookHandshakeError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        return Response(content=verified_challenge, media_type="text/plain")

    async def receive_webhook(
        request: Request,
        signature: str | None = Header(
            default=None,
            alias="X-Hub-Signature-256",
        ),
    ) -> dict[str, int]:
        payload = await request.body()
        try:
            dispatched = await processor.process(payload, signature)
        except InstagramWebhookAuthenticationError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        return {"dispatched": dispatched}

    router.add_api_route(
        "/webhooks/instagram",
        verify_webhook,
        methods=["GET"],
    )
    router.add_api_route(
        "/webhooks/instagram",
        receive_webhook,
        methods=["POST"],
    )
    return router
