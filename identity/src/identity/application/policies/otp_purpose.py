from identity.application.errors import IdentityNotRegisteredError, UnsupportedOtpPurposeError
from identity.domain import OtpPurpose


class OtpPurposePolicy:
    def validate(self, purpose: OtpPurpose) -> None:
        if purpose in (OtpPurpose.REGISTRATION, OtpPurpose.LOGIN):
            return

        raise UnsupportedOtpPurposeError(f"OTP purpose is not supported: {purpose.value}")

    def validate_identity_state(self, purpose: OtpPurpose, *, is_registered: bool) -> None:
        if purpose is OtpPurpose.LOGIN and not is_registered:
            raise IdentityNotRegisteredError("Identity is not registered")
