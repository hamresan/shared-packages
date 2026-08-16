from identity.application.errors import (
    IdentityAlreadyRegisteredError,
    IdentityNotRegisteredError,
)
from identity.domain import OtpPurpose, UserIdentity


class OtpPurposePolicy:
    def validate(self, purpose: OtpPurpose, identity: UserIdentity | None) -> None:
        if purpose is OtpPurpose.REGISTRATION and identity is not None:
            raise IdentityAlreadyRegisteredError("Identity is already registered")
        if purpose is OtpPurpose.LOGIN and identity is None:
            raise IdentityNotRegisteredError("Identity is not registered")
