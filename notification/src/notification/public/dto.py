from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NotificationReference:
    job_id: str
