from uuid import UUID

import pytest

from subscription import (
    ActiveBaseSubscriptionPolicy,
    SubjectReference,
    SubscriptionStatus,
    SubscriptionType,
)
from tests.support.domain.subscription_builder import SubscriptionBuilder


def test_active_base_subscription_policy_rejects_second_base_for_same_subject() -> None:
    existing = (
        SubscriptionBuilder()
        .with_id(UUID("11111111-1111-1111-1111-111111111111"))
        .with_status(SubscriptionStatus.ACTIVE)
        .build()
    )
    candidate = SubscriptionBuilder().build()

    with pytest.raises(ValueError, match="active BASE"):
        ActiveBaseSubscriptionPolicy().ensure_available(candidate, (existing,))


def test_active_base_subscription_policy_treats_trialing_base_as_occupied() -> None:
    existing = (
        SubscriptionBuilder()
        .with_id(UUID("11111111-1111-1111-1111-111111111111"))
        .with_status(SubscriptionStatus.TRIALING)
        .build()
    )

    with pytest.raises(ValueError, match="active BASE"):
        ActiveBaseSubscriptionPolicy().ensure_available(SubscriptionBuilder().build(), (existing,))


def test_active_base_subscription_policy_allows_addon_alongside_base() -> None:
    existing = (
        SubscriptionBuilder()
        .with_id(UUID("11111111-1111-1111-1111-111111111111"))
        .with_status(SubscriptionStatus.ACTIVE)
        .build()
    )
    addon = SubscriptionBuilder().with_subscription_type(SubscriptionType.ADDON).build()

    ActiveBaseSubscriptionPolicy().ensure_available(addon, (existing,))


def test_active_base_subscription_policy_ignores_other_subjects() -> None:
    existing = (
        SubscriptionBuilder()
        .with_id(UUID("11111111-1111-1111-1111-111111111111"))
        .with_subject(SubjectReference("store", "other-store"))
        .with_status(SubscriptionStatus.ACTIVE)
        .build()
    )

    ActiveBaseSubscriptionPolicy().ensure_available(SubscriptionBuilder().build(), (existing,))
