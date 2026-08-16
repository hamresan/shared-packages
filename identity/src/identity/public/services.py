from typing import Protocol

from identity.application.dto import (
    AuthSessionResult,
    RefreshSessionCommand,
    RequestOtpCommand,
    RequestOtpResult,
    VerifyOtpCommand,
)


class OtpRequester(Protocol):
    async def execute(self, command: RequestOtpCommand) -> RequestOtpResult: ...


class OtpVerifier(Protocol):
    async def execute(self, command: VerifyOtpCommand) -> AuthSessionResult: ...


class SessionRefresher(Protocol):
    async def execute(self, command: RefreshSessionCommand) -> AuthSessionResult: ...


class SessionRevoker(Protocol):
    async def execute(self, refresh_token: str) -> None: ...
