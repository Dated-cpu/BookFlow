from uuid import UUID

from src.application.base import BaseUseCase
from src.application.dtos.clients.create_client import (
    CreateClientRequest,
    CreateClientResponse,
)
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.entities.client import Client
from src.domain.repositories.client_repository import ClientRepository


class CreateClient(BaseUseCase[CreateClientRequest, CreateClientResponse]):
    def __init__(
        self,
        client_repo: ClientRepository,
        uow: UnitOfWork,
    ) -> None:
        self._client_repo = client_repo
        self._uow = uow

    async def execute(self, request: CreateClientRequest) -> CreateClientResponse:
        client = Client(
            organization_id=UUID(request.organization_id),
            name=request.name,
            email=request.email,
            phone=request.phone,
        )

        async with self._uow:
            saved = await self._client_repo.add(client)

        return CreateClientResponse(
            id=str(saved.id),
            organization_id=str(saved.organization_id),
            name=saved.name,
            email=saved.email,
            phone=saved.phone,
        )
