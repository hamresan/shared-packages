"""Shared registration mechanics for explicitly injected callables."""

from collections.abc import Callable, Mapping
from types import MappingProxyType

from langgraph_yaml.registration.errors import (
    DuplicateRegistrationError,
    InvalidRegistrationError,
    UnknownRegistrationError,
)

class CallableRegistry[CallableType: Callable[..., object]]:
    """Keep an isolated, read-only snapshot of named callable implementations."""

    def __init__(
        self,
        implementations: Mapping[str, CallableType] | None = None,
        *,
        kind: str,
    ) -> None:
        self._kind = kind
        entries: dict[str, CallableType] = {}
        for name, implementation in (implementations or {}).items():
            self.validate_registration(name, implementation)
            entries[name] = implementation
        self._entries: Mapping[str, CallableType] = MappingProxyType(entries)

    def validate_registration(self, name: str, implementation: object) -> None:
        """Reject invalid keys and non-callable implementations."""
        if not name.strip():
            raise InvalidRegistrationError(
                f"{self._kind} name must be a non-empty string"
            )
        if not callable(implementation):
            raise InvalidRegistrationError(
                f"{self._kind} {name!r} must be callable"
            )

    def resolve(self, name: str) -> CallableType:
        """Resolve a named implementation or raise a typed lookup error."""
        try:
            return self._entries[name]
        except (KeyError, TypeError) as exc:
            raise UnknownRegistrationError(
                f"Unknown {self._kind} {name!r}; "
                f"available: {', '.join(self._entries) or '(none)'}"
            ) from exc

    def register(self, name: str, implementation: CallableType) -> None:
        """Register an implementation, refusing to overwrite existing names."""
        self.validate_registration(name, implementation)
        if name in self._entries:
            raise DuplicateRegistrationError(
                f"{self._kind} {name!r} is already registered"
            )
        updated = dict(self._entries)
        updated[name] = implementation
        self._entries = MappingProxyType(updated)

    def names(self) -> tuple[str, ...]:
        """Return names in deterministic insertion order."""
        return tuple(self._entries)
