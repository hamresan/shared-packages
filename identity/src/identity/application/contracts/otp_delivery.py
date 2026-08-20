from typing import Protocol

from identity.domain import IdentityType, OtpPurpose


class OtpDelivery(Protocol):
    async def send(
        self,
        *,
        identity_type: IdentityType,
        destination: str,
        code: str,
        purpose: OtpPurpose,
        locale: str,
    ) -> None: ...
