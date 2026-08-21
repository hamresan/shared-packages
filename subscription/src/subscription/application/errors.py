class SubscriptionApplicationError(Exception):
    """Base application-layer error."""


class PlanNotFoundError(SubscriptionApplicationError):
    pass


class PlanCodeAlreadyExistsError(SubscriptionApplicationError):
    pass


class PlanUnavailableError(SubscriptionApplicationError):
    pass


class SubscriptionNotFoundError(SubscriptionApplicationError):
    pass
