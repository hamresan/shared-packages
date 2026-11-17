from typing import Protocol


class CustomerCreationFingerprinter(Protocol):
    def fingerprint(self, display_name: str | None) -> str: ...
