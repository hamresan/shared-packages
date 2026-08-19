import subscription


def test_subscription_package_imports() -> None:
    assert subscription.__all__ == []
