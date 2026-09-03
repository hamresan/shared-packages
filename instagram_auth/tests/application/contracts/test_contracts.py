from datetime import UTC, datetime

from instagram_auth.application.contracts import Clock, StateGenerator


class FixedClock(Clock):
    def __init__(self, current_time: datetime) -> None:
        self.current_time = current_time

    def now(self) -> datetime:
        return self.current_time


class FixedStateGenerator(StateGenerator):
    def __init__(self, state: str) -> None:
        self.state = state

    def generate(self) -> str:
        return self.state


def test_explicit_contract_implementations_are_injectable() -> None:
    now = datetime(2026, 9, 3, 12, 0, tzinfo=UTC)
    clock: Clock = FixedClock(now)
    state_generator: StateGenerator = FixedStateGenerator("opaque-state")

    assert clock.now() == now
    assert state_generator.generate() == "opaque-state"
