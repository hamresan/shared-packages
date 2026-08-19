from identity.application.errors import (
    IdentityAlreadyRegisteredError,
    IdentityNotRegisteredError,
    UnsupportedOtpPurposeError,
)
from identity.domain import OtpPurpose, UserIdentity


class OtpPurposePolicy:
    def validate(self, purpose: OtpPurpose, identity: UserIdentity | None) -> None:
        if purpose is OtpPurpose.REGISTRATION:
            if identity is not None:
                raise IdentityAlreadyRegisteredError("Identity is already registered")
            return

        if purpose is OtpPurpose.LOGIN:
            if identity is None:
                raise IdentityNotRegisteredError("Identity is not registered")
            return

        raise UnsupportedOtpPurposeError(f"OTP purpose is not supported: {purpose.value}")
