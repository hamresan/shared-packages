from identity.application.errors import UnsupportedOtpPurposeError
from identity.domain import OtpPurpose


class OtpPurposePolicy:
    def validate(self, purpose: OtpPurpose) -> None:
        if purpose in (OtpPurpose.REGISTRATION, OtpPurpose.LOGIN):
            return

        raise UnsupportedOtpPurposeError(f"OTP purpose is not supported: {purpose.value}")
