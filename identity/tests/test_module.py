from identity.application.services.refresh_session import RefreshSessionService
from identity.application.services.request_otp import RequestOtpService
from identity.application.services.revoke_session import RevokeSessionService
from identity.application.services.verify_otp import VerifyOtpService
from identity.infrastructure.persistence.sqlalchemy import SqlAlchemyIdentityUnitOfWork
from identity.presentation.fastapi import FastApiIdentityAdapter
from tests.support.database import SqliteIdentityDatabase
from tests.support.integrations import FakeNotificationSender
from tests.support.module_builder import IdentityTestModuleBuilder


def test_identity_module_wires_authentication_components() -> None:
    module = IdentityTestModuleBuilder().build(
        SqliteIdentityDatabase(),
        FakeNotificationSender(),
    )

    assert isinstance(module.unit_of_work, SqlAlchemyIdentityUnitOfWork)
    assert isinstance(module.otp_requester, RequestOtpService)
    assert isinstance(module.otp_verifier, VerifyOtpService)
    assert isinstance(module.session_refresher, RefreshSessionService)
    assert isinstance(module.session_revoker, RevokeSessionService)
    assert module.public_api.otp_requester is module.otp_requester
    assert isinstance(module.fastapi, FastApiIdentityAdapter)
