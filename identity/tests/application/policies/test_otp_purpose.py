import pytest

from identity.application.errors import IdentityNotRegisteredError, UnsupportedOtpPurposeError
from identity.application.policies.otp_purpose import OtpPurposePolicy
from identity.domain import OtpPurpose


def test_policy_allows_public_authentication_purposes_without_account_state() -> None:
    policy = OtpPurposePolicy()

    policy.validate(OtpPurpose.REGISTRATION)
    policy.validate(OtpPurpose.LOGIN)


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
        policy.validate(purpose)


def test_policy_rejects_login_for_unregistered_identity() -> None:
    policy = OtpPurposePolicy()

    with pytest.raises(IdentityNotRegisteredError):
        policy.validate_identity_state(OtpPurpose.LOGIN, is_registered=False)


def test_policy_allows_registration_for_unregistered_identity() -> None:
    policy = OtpPurposePolicy()

    policy.validate_identity_state(OtpPurpose.REGISTRATION, is_registered=False)


def test_policy_allows_login_for_registered_identity() -> None:
    policy = OtpPurposePolicy()

    policy.validate_identity_state(OtpPurpose.LOGIN, is_registered=True)
