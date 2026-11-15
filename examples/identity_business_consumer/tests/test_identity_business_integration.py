from httpx import ASGITransport, AsyncClient
from identity import IdentityType, OtpPurpose, RequestOtpCommand, VerifyOtpCommand

from identity_business_consumer_app import build_consumer_application


async def test_real_otp_notification_jwt_and_business_authorization() -> None:
    application = await build_consumer_application(
        signing_secret="test-only-signing-secret-with-32-or-more-bytes"
    )
    try:
        challenge = await application.identity.public_api.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.EMAIL,
                destination="owner@example.com",
                purpose=OtpPurpose.REGISTRATION,
            )
        )
        assert len(application.notification_queue.messages) == 1
        otp = application.notification_queue.messages[0].variables["otp"]
        assert isinstance(otp, str)
        session = await application.identity.public_api.otp_verifier.execute(
            VerifyOtpCommand(challenge_id=challenge.challenge_id, code=otp, full_name="Owner")
        )
        token = {"Authorization": f"Bearer {session.access_token}"}
        async with AsyncClient(
            transport=ASGITransport(app=application.fastapi), base_url="http://test"
        ) as client:
            assert (await client.get("/identity/me", headers=token)).json()["user_id"] == str(
                session.user_id
            )
            created = await client.post(
                "/businesses",
                headers=token,
                json={
                    "name": "Oman Services",
                    "country_code": "OM",
                    "default_language": "en",
                    "default_currency_code": "OMR",
                },
            )
            assert created.status_code == 201, created.text
            business_id = created.json()["id"]
            assert (
                await client.get(f"/businesses/{business_id}", headers=token)
            ).status_code == 200
            assert (await client.get(f"/businesses/{business_id}")).status_code == 401
            assert (
                await client.get(
                    f"/businesses/{business_id}",
                    headers={"Authorization": "Bearer invalid.jwt.token"},
                )
            ).status_code == 401
    finally:
        await application.database.close()
