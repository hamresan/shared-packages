from enum import StrEnum


class UsagePeriod(StrEnum):
    LIFETIME = "lifetime"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    BILLING_PERIOD = "billing_period"
    TRIAL = "trial"
