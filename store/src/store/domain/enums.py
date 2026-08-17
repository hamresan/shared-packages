from enum import StrEnum


class StoreSetupStatus(StrEnum):
    DRAFT = "draft"
    READY = "ready"


class StoreAvailabilityStatus(StrEnum):
    OFFLINE = "offline"
    ONLINE = "online"


class StoreModerationStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"


class StoreSuspensionReason(StrEnum):
    POLICY_VIOLATION = "policy_violation"
    FRAUD_RISK = "fraud_risk"
    LEGAL = "legal"
    OTHER = "other"


class StoreContactType(StrEnum):
    PHONE = "phone"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    INSTAGRAM = "instagram"
    EMAIL = "email"
    WEBSITE = "website"
    OTHER = "other"
