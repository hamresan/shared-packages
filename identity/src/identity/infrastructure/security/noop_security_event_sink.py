from identity.application.contracts.security_events import SecurityEvent, SecurityEventSink


class NoOpSecurityEventSink(SecurityEventSink):
    async def emit(self, event: SecurityEvent) -> None:
        return None
