from dataclasses import dataclass

from fastapi import APIRouter, FastAPI


@dataclass(frozen=True, slots=True)
class FastApiSubscriptionAdapter:
    subscription_router: APIRouter

    def router(self) -> APIRouter:
        return self.subscription_router

    def install(self, app: FastAPI) -> None:
        app.include_router(self.subscription_router)
