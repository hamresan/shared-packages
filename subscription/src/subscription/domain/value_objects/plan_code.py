import re
from dataclasses import dataclass

_PLAN_CODE_PATTERN = re.compile(r"^[a-z][a-z0-9._-]{0,63}$")


@dataclass(frozen=True, slots=True)
class PlanCode:
    value: str

    def __post_init__(self) -> None:
        if not _PLAN_CODE_PATTERN.fullmatch(self.value):
            raise ValueError(
                "plan code must be a canonical lowercase identifier containing only "
                "letters, digits, '.', '_' or '-'"
            )
