import pytest

from identity.application.dto_external import AuthenticateExternalIdentityCommand
from identity.public import AuthenticateExternalIdentityCommand as PublicCommand
from tests.support.database import SqliteIdentityDatabase
from tests.support.integrations import FakeNotificationSender
from tests.support.module_builder import IdentityTestModuleBuilder


def test_external_identity_command_is_public() -> None:
    command = PublicCommand(
        provider="instagram",
        subject="17841400000000000",
        display_name="Shop Local",
    )

    assert isinstance(command, AuthenticateExternalIdentityCommand)
    assert command.provider == "instagram"


@pytest.mark.asyncio
async def test_external_identity_login_is_idempotent_and_creates_sessions() -> None:
    database = SqliteIdentityDatabase()
    await database.start()
    module = IdentityTestModuleBuilder().build(database, FakeNotificationSender())

    try:
        first = await module.public_api.external_identity_authenticator.execute(
            PublicCommand(
                provider="Instagram",
                subject="17841400000000000",
                display_name="Shop Local",
                device_info="pytest",
                ip_address="127.0.0.1",
            )
        )
        second = await module.public_api.external_identity_authenticator.execute(
            PublicCommand(
                provider="instagram",
                subject="17841400000000000",
                display_name="Changed Display Name",
            )
        )

        assert first.user_id == second.user_id
        assert first.session_id != second.session_id
        assert first.access_token != second.access_token
        assert first.refresh_token != second.refresh_token
    finally:
        await database.close()


@pytest.mark.asyncio
async def test_different_external_subjects_create_different_users() -> None:
    database = SqliteIdentityDatabase()
    await database.start()
    module = IdentityTestModuleBuilder().build(database, FakeNotificationSender())

    try:
        first = await module.public_api.external_identity_authenticator.execute(
            PublicCommand(
                provider="instagram",
                subject="account-1",
                display_name="Account One",
            )
        )
        second = await module.public_api.external_identity_authenticator.execute(
            PublicCommand(
                provider="instagram",
                subject="account-2",
                display_name="Account Two",
            )
        )

        assert first.user_id != second.user_id
    finally:
        await database.close()
