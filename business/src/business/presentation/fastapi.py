from dataclasses import dataclass

from fastapi import APIRouter, FastAPI


@dataclass(frozen=True, slots=True)
class FastApiBusinessAdapter:
    business_router: APIRouter
    branch_router: APIRouter
    membership_router: APIRouter

    def install(self, app: FastAPI) -> None:
        app.include_router(self.business_router)
        app.include_router(self.branch_router)
        app.include_router(self.membership_router)
