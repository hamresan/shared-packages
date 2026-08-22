"""Protected credential secret material for persistence boundaries."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ProtectedCredentialSecret:
    """Opaque protected secret material that is safe to hand to persistence."""

    value: bytes = field(repr=False)

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("protected credential secret must not be empty")
