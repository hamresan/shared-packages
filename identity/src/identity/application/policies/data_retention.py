from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True, slots=True)
class DataRetentionCutoffs:
    otp_challenges_before: datetime
    sessions_before: datetime


@dataclass(frozen=True, slots=True)
class DataRetentionPolicy:
    otp_challenge_retention: timedelta
    session_retention: timedelta

    def cutoffs(self, now: datetime) -> DataRetentionCutoffs:
        return DataRetentionCutoffs(
            otp_challenges_before=now - self.otp_challenge_retention,
            sessions_before=now - self.session_retention,
        )
