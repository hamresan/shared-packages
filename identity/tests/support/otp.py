from tests.support.integrations import FakeNotificationSender


def latest_otp(sender: FakeNotificationSender) -> str:
    value = sender.commands[-1].variables["otp"]
    if not isinstance(value, str):
        raise AssertionError("Expected OTP notification variable to be a string")
    return value


def invalid_otp_for(valid_otp: str) -> str:
    return "111111" if valid_otp == "000000" else "000000"
