from uuid import UUID

from src.application.base import BaseUseCase
from src.application.dtos.services.delete_service import DeleteServiceRequest
from src.application.exceptions import ApplicationError
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from src.domain.repositories.service_repository import ServiceRepository


class DeleteService(BaseUseCase[DeleteServiceRequest, None]):
    def __init__(
        self,
        service_repo: ServiceRepository,
        org_member_repo: OrganizationMemberRepository,
        uow: UnitOfWork,
    ) -> None:
        self._service_repo = service_repo
        self._org_member_repo = org_member_repo
        self._uow = uow

    async def execute(self, request: DeleteServiceRequest) -> None:
        service = await self._service_repo.get_by_id(UUID(request.service_id))
        if not service:
            raise ApplicationError("Service not found")

        memberships = await self._org_member_repo.list_by_user_id(UUID(request.user_id))
        if not any(m.organization_id == service.organization_id for m in memberships):
            raise ApplicationError("Service not found")

        service.is_active = False

        async with self._uow:
            await self._service_repo.update(service)
