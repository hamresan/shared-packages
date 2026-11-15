from business.domain.branch import Branch
from business.domain.business import Business
from business.domain.membership import BusinessMembership
from business.presentation.schemas import BranchResponse, BusinessResponse, MembershipResponse


class BusinessResponseMapper:
    def to_response(self, business: Business) -> BusinessResponse:
        return BusinessResponse.model_validate(business)


class BranchResponseMapper:
    def to_response(self, branch: Branch) -> BranchResponse:
        return BranchResponse.model_validate(branch)


class MembershipResponseMapper:
    def to_response(self, membership: BusinessMembership) -> MembershipResponse:
        return MembershipResponse.model_validate(membership)
