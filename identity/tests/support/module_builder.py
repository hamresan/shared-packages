from collections.abc import Mapping
from datetime import timedelta

from identity import IdentityModule, IdentityModuleConfig
from identity.application.contracts.security_events import SecurityEventSink
from tests.support.authentication import FakeAccessTokenAuthenticator
from tests.support.database_contracts import IdentityTestDatabase
from tests.support.integrations import FakeAccessTokenIssuer, FakeNotificationSender

TEST_SIGNING_SECRET = b"identity-test-signing-secret-32b!!"


class IdentityTestModuleBuilder:
    def build(
        self,
        database: IdentityTestDatabase,
        notification_sender: FakeNotificationSender,
        security_event_sink: SecurityEventSink | None = None,
        *,
        signing_secret: bytes = TEST_SIGNING_SECRET,
        signing_key_id: str = "v1",
        previous_signing_secrets: Mapping[str, bytes] | None = None,
        otp_resend_delay: timedelta = timedelta(seconds=60),
        otp_request_burst_limit: int = 5,
    ) -> IdentityModule:
        return IdentityModule(
            IdentityModuleConfig(
                session_factory=database.session_factory,
                notification_sender=notification_sender,
                access_token_issuer=FakeAccessTokenIssuer(),
                access_token_authenticator=FakeAccessTokenAuthenticator(),
                signing_secret=signing_secret,
                signing_key_id=signing_key_id,
                previous_signing_secrets=previous_signing_secrets or {},
                security_event_sink=security_event_sink,
                otp_resend_delay=otp_resend_delay,
                otp_request_burst_limit=otp_request_burst_limit,
            )
        )
