import httpx
import pytest
from identity import IdentityType, OtpPurpose, RequestOtpCommand, VerifyOtpCommand

from consumer_app import build_consumer_application


@pytest.mark.asyncio
async def test_identity_notification_database_and_fastapi_integration() -> None:
    application = await build_consumer_application()

    try:
        request_result = await application.identity.public_api.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.EMAIL,
                destination="owner@example.com",
                purpose=OtpPurpose.REGISTRATION,
            )
        )

        assert len(application.notification_queue.items) == 1

        payload = application.notification_queue.items[0]
        otp = payload.variables["otp"]

        assert isinstance(otp, str)
        assert payload.recipient == "owner@example.com"
        assert payload.template_key == "identity.otp"

        auth_result = await application.identity.public_api.otp_verifier.execute(
            VerifyOtpCommand(
                challenge_id=request_result.challenge_id,
                code=otp,
                full_name="Store Owner",
            )
        )

        assert auth_result.access_token
        assert auth_result.refresh_token

        principal = await application.token_adapter.authenticate(auth_result.access_token)
        assert principal.user_id == auth_result.user_id
        assert principal.session_id == auth_result.session_id

        transport = httpx.ASGITransport(app=application.fastapi)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/identity/me",
                headers={"Authorization": f"Bearer {auth_result.access_token}"},
            )

        assert response.status_code == 200
        assert response.json() == {
            "user_id": str(auth_result.user_id),
            "session_id": str(auth_result.session_id),
        }
    finally:
        await application.database.close()
