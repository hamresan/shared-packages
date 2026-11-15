class BusinessError(Exception):
    """Base error for business-domain failures."""


class BusinessNotFoundError(BusinessError):
    """A business is absent or not visible to the current actor."""


class BusinessPermissionDeniedError(BusinessError):
    """A member lacks the owner role required by the operation."""


class BusinessArchivedError(BusinessError):
    """An archived business cannot be modified or archived again."""


class BranchNotFoundError(BusinessError):
    """The requested branch is absent or belongs to another business."""


class BranchArchivedError(BusinessError):
    """An archived branch cannot be changed or archived again."""


class BranchAlreadyActiveError(BusinessError):
    """An active branch cannot be reactivated again."""
