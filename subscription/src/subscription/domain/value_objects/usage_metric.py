import re
from dataclasses import dataclass

_USAGE_METRIC_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_MAX_USAGE_METRIC_LENGTH = 120


@dataclass(frozen=True, slots=True)
class UsageMetric:
    """Consumer-defined usage metric identifier."""

    key: str

    def __post_init__(self) -> None:
        if not _USAGE_METRIC_PATTERN.fullmatch(self.key):
            raise ValueError("usage metric must be a canonical lowercase identifier")
        if len(self.key) > _MAX_USAGE_METRIC_LENGTH:
            raise ValueError(f"usage metric must not exceed {_MAX_USAGE_METRIC_LENGTH} characters")
