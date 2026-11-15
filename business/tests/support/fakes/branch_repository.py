from copy import deepcopy
from uuid import UUID

from business.application.contracts import BranchRepository
from business.domain.branch import Branch
from tests.support.fakes.database import InMemoryBusinessDatabase


class InMemoryBranchRepository(BranchRepository):
    def __init__(
        self,
        database: InMemoryBusinessDatabase,
        staged_branches: dict[UUID, Branch],
        *,
        fail_add: bool = False,
    ) -> None:
        self._database = database
        self._staged_branches = staged_branches
        self._fail_add = fail_add

    async def add(self, branch: Branch) -> None:
        if self._fail_add:
            raise RuntimeError("Branch write failed")
        self._staged_branches[branch.id] = deepcopy(branch)

    async def get_for_business(self, business_id: UUID, branch_id: UUID) -> Branch | None:
        branch = self._all_branches().get(branch_id)
        if branch is None or branch.business_id != business_id:
            return None
        return deepcopy(branch)

    async def list_for_business(
        self, business_id: UUID, *, city: str | None, country_code: str | None
    ) -> tuple[Branch, ...]:
        result: list[Branch] = []
        for branch in self._all_branches().values():
            if branch.business_id != business_id:
                continue
            if city is not None and (
                branch.address is None
                or branch.address.city is None
                or branch.address.city.casefold() != city
            ):
                continue
            if country_code is not None and (
                branch.address is None or branch.address.country_code != country_code
            ):
                continue
            result.append(deepcopy(branch))
        return tuple(result)

    async def save(self, branch: Branch) -> None:
        self._staged_branches[branch.id] = deepcopy(branch)

    def _all_branches(self) -> dict[UUID, Branch]:
        return {**self._database.branches, **self._staged_branches}
