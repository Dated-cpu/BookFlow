from uuid import UUID

from src.application.base import BaseUseCase
from src.application.dtos.services.update_service import (
    UpdateServiceRequest,
    UpdateServiceResponse,
)
from src.application.exceptions import ApplicationError
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from src.domain.repositories.service_repository import ServiceRepository


class UpdateService(BaseUseCase[UpdateServiceRequest, UpdateServiceResponse]):
    def __init__(
        self,
        service_repo: ServiceRepository,
        org_member_repo: OrganizationMemberRepository,
        uow: UnitOfWork,
    ) -> None:
        self._service_repo = service_repo
        self._org_member_repo = org_member_repo
        self._uow = uow

    async def execute(self, request: UpdateServiceRequest) -> UpdateServiceResponse:
        service = await self._service_repo.get_by_id(UUID(request.service_id))
        if not service:
            raise ApplicationError("Service not found")

        memberships = await self._org_member_repo.list_by_user_id(UUID(request.user_id))
        if not any(m.organization_id == service.organization_id for m in memberships):
            raise ApplicationError("Service not found")

        if request.name is not None:
            existing = await self._service_repo.get_by_name_and_org(
                request.name, service.organization_id
            )
            if existing and existing.id != service.id:
                raise ApplicationError("Service with this name already exists")
            service.name = request.name
        if request.price is not None:
            service.price = request.price
        if request.duration_minutes is not None:
            service.duration_minutes = request.duration_minutes
        if request.description is not None:
            service.description = request.description
        if request.is_active is not None:
            service.is_active = request.is_active

        async with self._uow:
            updated = await self._service_repo.update(service)

        return UpdateServiceResponse(
            id=str(updated.id),
            organization_id=str(updated.organization_id),
            name=updated.name,
            price=updated.price,
            duration_minutes=updated.duration_minutes,
            description=updated.description,
            is_active=updated.is_active,
        )
