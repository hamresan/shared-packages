from identity.domain import IdentityType, OtpPurpose, UserStatus


def test_identity_enums_expose_stable_values() -> None:
    assert UserStatus.ACTIVE.value == "active"
    assert IdentityType.EMAIL.value == "email"
    assert OtpPurpose.LOGIN.value == "login"
