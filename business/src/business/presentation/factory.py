from business.presentation.dependencies import (
    AuthenticatedActorDependency,
    BranchUseCases,
    BusinessUseCases,
    MembershipUseCases,
)
from business.presentation.errors.http import BusinessHttpErrorMapper, BusinessHttpExecutor
from business.presentation.fastapi import FastApiBusinessAdapter
from business.presentation.mappers import (
    BranchRequestMapper,
    BranchResponseMapper,
    BusinessRequestMapper,
    BusinessResponseMapper,
    MembershipRequestMapper,
    MembershipResponseMapper,
)
from business.presentation.routes import (
    BranchRouterFactory,
    BusinessRouterFactory,
    MembershipRouterFactory,
)


def build_fastapi_business_adapter(
    *,
    authenticated_actor_dependency: AuthenticatedActorDependency,
    businesses: BusinessUseCases,
    branches: BranchUseCases,
    memberships: MembershipUseCases,
) -> FastApiBusinessAdapter:
    executor = BusinessHttpExecutor(BusinessHttpErrorMapper())
    return FastApiBusinessAdapter(
        business_router=BusinessRouterFactory(
            authenticated_actor_dependency,
            businesses.create,
            businesses.get,
            businesses.list,
            businesses.update,
            businesses.archive,
            BusinessRequestMapper(),
            BusinessResponseMapper(),
            executor,
        ).create(),
        branch_router=BranchRouterFactory(
            authenticated_actor_dependency,
            branches.create,
            branches.get,
            branches.list,
            branches.update,
            branches.archive,
            branches.reactivate,
            BranchRequestMapper(),
            BranchResponseMapper(),
            executor,
        ).create(),
        membership_router=MembershipRouterFactory(
            authenticated_actor_dependency,
            memberships.invite,
            memberships.accept,
            memberships.list,
            memberships.change_role,
            memberships.revoke,
            memberships.set_access,
            memberships.transfer,
            MembershipRequestMapper(),
            MembershipResponseMapper(),
            executor,
        ).create(),
    )
