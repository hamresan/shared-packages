from identity.application.dto import (
    AuthSessionResult,
    RefreshSessionCommand,
    RequestOtpCommand,
    RequestOtpResult,
    VerifyOtpCommand,
)
from identity.presentation.schemas import (
    AuthSessionResponse,
    RefreshSessionRequest,
    RequestOtpRequest,
    RequestOtpResponse,
    VerifyOtpRequest,
)


class IdentityRequestMapper:
    def to_request_otp_command(self, request: RequestOtpRequest) -> RequestOtpCommand:
        return RequestOtpCommand(
            identity_type=request.identity_type,
            destination=request.destination,
            purpose=request.purpose,
            locale=request.locale,
        )

    def to_verify_otp_command(self, request: VerifyOtpRequest) -> VerifyOtpCommand:
        return VerifyOtpCommand(
            challenge_id=request.challenge_id,
            code=request.code,
            full_name=request.full_name,
            device_info=request.device_info,
            ip_address=request.ip_address,
        )

    def to_refresh_session_command(
        self,
        request: RefreshSessionRequest,
    ) -> RefreshSessionCommand:
        return RefreshSessionCommand(
            refresh_token=request.refresh_token,
            device_info=request.device_info,
            ip_address=request.ip_address,
        )


class IdentityResponseMapper:
    def from_request_otp_result(self, result: RequestOtpResult) -> RequestOtpResponse:
        return RequestOtpResponse(
            challenge_id=result.challenge_id,
            expires_at=result.expires_at,
            resend_available_at=result.resend_available_at,
        )

    def from_auth_session_result(self, result: AuthSessionResult) -> AuthSessionResponse:
        return AuthSessionResponse(
            user_id=result.user_id,
            session_id=result.session_id,
            access_token=result.access_token,
            access_token_expires_at=result.access_token_expires_at,
            refresh_token=result.refresh_token,
            refresh_token_expires_at=result.refresh_token_expires_at,
        )
