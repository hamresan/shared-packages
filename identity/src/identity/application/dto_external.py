from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AuthenticateExternalIdentityCommand:
    provider: str
    subject: str
    display_name: str
    device_info: str | None = None
    ip_address: str | None = None
