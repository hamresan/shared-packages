from identity import IdentityModule, IdentityModuleConfig
from tests.support.authentication import FakeAccessTokenAuthenticator
from tests.support.database import SqliteIdentityDatabase
from tests.support.integrations import FakeAccessTokenIssuer, FakeNotificationSender


class IdentityTestModuleBuilder:
    def build(
        self,
        database: SqliteIdentityDatabase,
        notification_sender: FakeNotificationSender,
    ) -> IdentityModule:
        return IdentityModule(
            IdentityModuleConfig(
                session_factory=database.session_factory,
                notification_sender=notification_sender,
                access_token_issuer=FakeAccessTokenIssuer(),
                access_token_authenticator=FakeAccessTokenAuthenticator(),
                signing_secret=b"identity-test-secret",
            )
        )
