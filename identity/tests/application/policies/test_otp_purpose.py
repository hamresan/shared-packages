import pytest

from identity.application.errors import UnsupportedOtpPurposeError
from identity.application.policies.otp_purpose import OtpPurposePolicy
from identity.domain import OtpPurpose


@pytest.mark.parametrize(
    "purpose",
    [
        OtpPurpose.VERIFY_EMAIL,
        OtpPurpose.CHANGE_EMAIL,
        OtpPurpose.CHANGE_MOBILE,
        OtpPurpose.ACCOUNT_RECOVERY,
    ],
)
def test_policy_rejects_unimplemented_purposes(purpose: OtpPurpose) -> None:
    policy = OtpPurposePolicy()

    with pytest.raises(UnsupportedOtpPurposeError):
        policy.validate(purpose, identity=None)
