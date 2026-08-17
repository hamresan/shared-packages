from dataclasses import dataclass

from fastapi import APIRouter, FastAPI


@dataclass(frozen=True, slots=True)
class FastApiStoreAdapter:
    store_router: APIRouter

    def router(self) -> APIRouter:
        return self.store_router

    def install(self, app: FastAPI) -> None:
        app.include_router(self.store_router)
