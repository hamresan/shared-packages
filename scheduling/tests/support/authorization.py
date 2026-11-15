"""Deterministic host authorization fake with explicit scope grants."""

from scheduling.application.models import TrustedActor
from scheduling.domain.calendar import CalendarScope


class GrantAuthorizer:
    def __init__(self) -> None:
        self._read_grants: set[tuple[str, str, CalendarScope, str]] = set()
        self._manage_grants: set[tuple[str, str, CalendarScope, str]] = set()

    def allow_read(self, actor: TrustedActor, scope: CalendarScope, scope_id: str) -> None:
        self._read_grants.add((actor.tenant_id, actor.actor_id, scope, scope_id))

    def allow_manage(self, actor: TrustedActor, scope: CalendarScope, scope_id: str) -> None:
        key = (actor.tenant_id, actor.actor_id, scope, scope_id)
        self._manage_grants.add(key)
        self._read_grants.add(key)

    async def ensure_can_read(
        self, actor: TrustedActor, scope: CalendarScope, scope_id: str
    ) -> None:
        if (actor.tenant_id, actor.actor_id, scope, scope_id) not in self._read_grants:
            raise PermissionError("Actor has no read permission for this calendar scope.")

    async def ensure_can_manage(
        self, actor: TrustedActor, scope: CalendarScope, scope_id: str
    ) -> None:
        if (actor.tenant_id, actor.actor_id, scope, scope_id) not in self._manage_grants:
            raise PermissionError("Actor has no management permission for this calendar scope.")
