from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RenderedMessage:
    subject: str | None
    body: str
