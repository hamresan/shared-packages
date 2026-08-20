from tests.support.integrations import FakeNotificationSender


def latest_otp(sender: FakeNotificationSender) -> str:
    value = sender.commands[-1].variables["otp"]
    if not isinstance(value, str):
        raise AssertionError("Expected OTP notification variable to be a string")
    return value
