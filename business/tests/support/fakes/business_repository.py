from copy import deepcopy
from uuid import UUID

from business.application.contracts import BusinessRepository
from business.domain.business import Business
from tests.support.fakes.database import InMemoryBusinessDatabase


class InMemoryBusinessRepository(BusinessRepository):
    def __init__(
        self, database: InMemoryBusinessDatabase, staged_businesses: dict[UUID, Business]
    ) -> None:
        self._database = database
        self._staged_businesses = staged_businesses

    async def add(self, business: Business) -> None:
        self._staged_businesses[business.id] = deepcopy(business)

    async def get_by_id(self, business_id: UUID) -> Business | None:
        business = self._staged_businesses.get(business_id)
        if business is None:
            business = self._database.businesses.get(business_id)
        return deepcopy(business)

    async def list_by_ids(self, business_ids: tuple[UUID, ...]) -> tuple[Business, ...]:
        results: list[Business] = []
        for business_id in dict.fromkeys(business_ids):
            business = await self.get_by_id(business_id)
            if business is not None:
                results.append(business)
        return tuple(results)

    async def save(self, business: Business) -> None:
        self._staged_businesses[business.id] = deepcopy(business)
