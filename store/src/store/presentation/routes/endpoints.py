from uuid import UUID

from store.application import OwnedStoreReader, StoreCreator, StoreReader
from store.presentation.dependencies import AuthenticatedActor
from store.presentation.errors import StoreHttpErrorMapper
from store.presentation.mappers import StoreRequestMapper, StoreResponseMapper
from store.presentation.schemas import CreateStoreRequest, StoreResponse


class CreateStoreEndpoint:
    def __init__(
        self,
        service: StoreCreator,
        request_mapper: StoreRequestMapper,
        response_mapper: StoreResponseMapper,
        error_mapper: StoreHttpErrorMapper,
    ) -> None:
        self._service = service
        self._request_mapper = request_mapper
        self._response_mapper = response_mapper
        self._error_mapper = error_mapper

    async def __call__(
        self,
        request: CreateStoreRequest,
        actor: AuthenticatedActor,
    ) -> StoreResponse:
        try:
            result = await self._service.execute(
                self._request_mapper.to_create_command(request, actor)
            )
        except ValueError as error:
            raise self._error_mapper.application_error(error) from error
        return self._response_mapper.to_response(result.store)


class GetOwnedStoreEndpoint:
    def __init__(
        self,
        service: OwnedStoreReader,
        request_mapper: StoreRequestMapper,
        response_mapper: StoreResponseMapper,
        error_mapper: StoreHttpErrorMapper,
    ) -> None:
        self._service = service
        self._request_mapper = request_mapper
        self._response_mapper = response_mapper
        self._error_mapper = error_mapper

    async def __call__(self, actor: AuthenticatedActor) -> StoreResponse:
        store = await self._service.execute(self._request_mapper.to_owned_store_query(actor))
        if store is None:
            raise self._error_mapper.store_not_found()
        return self._response_mapper.to_response(store)


class GetStoreEndpoint:
    def __init__(
        self,
        service: StoreReader,
        request_mapper: StoreRequestMapper,
        response_mapper: StoreResponseMapper,
        error_mapper: StoreHttpErrorMapper,
    ) -> None:
        self._service = service
        self._request_mapper = request_mapper
        self._response_mapper = response_mapper
        self._error_mapper = error_mapper

    async def __call__(self, store_id: UUID) -> StoreResponse:
        store = await self._service.execute(self._request_mapper.to_store_query(store_id))
        if store is None:
            raise self._error_mapper.store_not_found()
        return self._response_mapper.to_response(store)
