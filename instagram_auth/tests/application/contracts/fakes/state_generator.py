from instagram_auth.application.contracts import StateGenerator


class FixedStateGenerator(StateGenerator):
    """Deterministic OAuth state generator fake for application tests."""

    def __init__(self, state: str) -> None:
        self.state = state

    def generate(self) -> str:
        return self.state
