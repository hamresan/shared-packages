from datetime import UTC, datetime

from instagram_auth.application.contracts import Clock, StateGenerator
from tests.application.contracts.fakes import FixedClock, FixedStateGenerator


def test_explicit_contract_implementations_are_injectable() -> None:
    now = datetime(2026, 9, 3, 12, 0, tzinfo=UTC)
    clock: Clock = FixedClock(now)
    state_generator: StateGenerator = FixedStateGenerator("opaque-state")

    assert clock.now() == now
    assert state_generator.generate() == "opaque-state"
