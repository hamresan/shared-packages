import sys

import customer


def test_core_import_has_no_optional_framework_dependencies() -> None:
    assert "fastapi" not in sys.modules
    assert "sqlalchemy" not in sys.modules
    assert customer.CustomerModule


def test_public_exports_are_controlled() -> None:
    assert set(customer.__all__) == {
        "CustomerActor",
        "CustomerActorType",
        "CustomerAuthorizer",
        "CustomerModule",
        "CustomerModuleConfig",
        "CustomerPermission",
        "IdentityVerifier",
    }
