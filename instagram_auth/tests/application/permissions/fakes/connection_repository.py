from instagram_auth.application.contracts import InstagramConnectionRepository
from instagram_auth.domain import InstagramConnection, InstagramConnectionId


class FakeInstagramConnectionRepository(InstagramConnectionRepository):
    """In-memory repository fake scoped to permission tests."""

    def __init__(self, connections: tuple[InstagramConnection, ...] = ()) -> None:
        self.connections = {connection.id: connection for connection in connections}

    async def add(self, connection: InstagramConnection) -> None:
        self.connections[connection.id] = connection

    async def update(self, connection: InstagramConnection) -> None:
        self.connections[connection.id] = connection

    async def find_by_owner_and_account(
        self,
        *,
        owner_user_id: str,
        instagram_account_id: str,
    ) -> InstagramConnection | None:
        return next(
            (
                connection
                for connection in self.connections.values()
                if connection.owner_user_id == owner_user_id
                and connection.instagram_account_id == instagram_account_id
            ),
            None,
        )

    async def get_by_id(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramConnection | None:
        return self.connections.get(connection_id)
