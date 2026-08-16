import pytest

from notification.domain.enums import NotificationChannel
from notification.infrastructure.providers.resolver import StaticNotificationProviderResolver
from tests.support.fakes import FakeProvider


def test_provider_resolver_returns_provider_for_channel() -> None:
    provider = FakeProvider()
    resolver = StaticNotificationProviderResolver({NotificationChannel.SMS: provider})

    assert resolver.resolve(NotificationChannel.SMS) is provider


def test_provider_resolver_raises_for_unconfigured_channel() -> None:
    resolver = StaticNotificationProviderResolver({})

    with pytest.raises(ValueError, match="No notification provider configured"):
        resolver.resolve(NotificationChannel.SMS)
