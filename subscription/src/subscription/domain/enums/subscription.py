from enum import StrEnum


class SubscriptionType(StrEnum):
    BASE = "base"
    ADDON = "addon"


class SubscriptionSource(StrEnum):
    PAID = "paid"
    TRIAL = "trial"
    MANUAL = "manual"
    PROMOTIONAL = "promotional"
    MIGRATED = "migrated"


class SubscriptionStatus(StrEnum):
    PENDING = "pending"
    TRIALING = "trialing"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
