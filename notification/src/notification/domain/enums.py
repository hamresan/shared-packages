from enum import StrEnum


class NotificationChannel(StrEnum):
    SMS = "sms"
    EMAIL = "email"
    CONSOLE = "console"
