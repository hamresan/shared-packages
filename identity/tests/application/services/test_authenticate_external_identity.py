from identity.application.dto_external import AuthenticateExternalIdentityCommand
from identity.public import AuthenticateExternalIdentityCommand as PublicCommand


def test_external_identity_command_is_public() -> None:
    command = PublicCommand(
        provider="instagram",
        subject="17841400000000000",
        display_name="Shop Local",
    )

    assert isinstance(command, AuthenticateExternalIdentityCommand)
    assert command.provider == "instagram"
