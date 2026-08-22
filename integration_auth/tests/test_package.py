import integration_auth


def test_package_imports() -> None:
    assert integration_auth.__all__ == ()
