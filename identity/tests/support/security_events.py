from identity.application.contracts.security_events import SecurityEvent, SecurityEventSink


class RecordingSecurityEventSink(SecurityEventSink):
    def __init__(self) -> None:
        self.events: list[SecurityEvent] = []

    async def emit(self, event: SecurityEvent) -> None:
        self.events.append(event)
