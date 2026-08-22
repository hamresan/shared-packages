from datetime import datetime
from uuid import UUID

from subscription import Subscription
from subscription.application import (
    ActivateSubscriptionCommand,
    ActivateSubscriptionService,
    RenewSubscriptionCommand,
    RenewSubscriptionService,
)


class PaidSubscriptionEventHandler:
    def __init__(
        self,
        activator: ActivateSubscriptionService,
        renewer: RenewSubscriptionService,
    ) -> None:
        self._activator = activator
        self._renewer = renewer

    async def activate_after_payment(
        self,
        subscription_id: UUID,
        expires_at: datetime,
    ) -> Subscription:
        return await self._activator.execute(
            ActivateSubscriptionCommand(subscription_id=subscription_id, expires_at=expires_at)
        )

    async def renew_after_payment(
        self,
        subscription_id: UUID,
        new_expires_at: datetime,
    ) -> Subscription:
        return await self._renewer.execute(
            RenewSubscriptionCommand(
                subscription_id=subscription_id,
                new_expires_at=new_expires_at,
            )
        )
