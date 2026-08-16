import secrets

from identity.application.contracts.security import OtpCodeGenerator, RefreshTokenGenerator


class SecureNumericOtpCodeGenerator(OtpCodeGenerator):
    def __init__(self, digits: int = 6) -> None:
        if digits < 4:
            raise ValueError("OTP must contain at least 4 digits")
        self._digits = digits

    def generate(self) -> str:
        upper_bound = 10**self._digits
        return f"{secrets.randbelow(upper_bound):0{self._digits}d}"


class SecureRefreshTokenGenerator(RefreshTokenGenerator):
    def __init__(self, bytes_count: int = 48) -> None:
        if bytes_count < 32:
            raise ValueError("Refresh token entropy must be at least 32 bytes")
        self._bytes_count = bytes_count

    def generate(self) -> str:
        return secrets.token_urlsafe(self._bytes_count)
