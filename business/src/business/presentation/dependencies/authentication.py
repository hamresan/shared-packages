from collections.abc import Awaitable, Callable

from business.application.actor import AuthenticatedActor

AuthenticatedActorDependency = Callable[..., Awaitable[AuthenticatedActor]]
