from uuid import UUID

from src.application.base import BaseUseCase
from src.application.dtos.services.create_service import (
    CreateServiceRequest,
    ServiceResponse,
)
from src.application.exceptions import ApplicationError
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.entities.service import Service
from src.domain.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from src.domain.repositories.service_repository import ServiceRepository


class CreateService(BaseUseCase[CreateServiceRequest, ServiceResponse]):
    def __init__(
        self,
        service_repo: ServiceRepository,
        org_member_repo: OrganizationMemberRepository,
        uow: UnitOfWork,
    ) -> None:
        self._service_repo = service_repo
        self._org_member_repo = org_member_repo
        self._uow = uow

    async def execute(self, request: CreateServiceRequest) -> ServiceResponse:
        org_id = UUID(request.organization_id)

        memberships = await self._org_member_repo.list_by_user_id(UUID(request.owner_user_id))
        if not any(m.organization_id == org_id for m in memberships):
            raise ApplicationError("Organization not found")

        existing = await self._service_repo.get_by_name_and_org(request.name, org_id)
        if existing:
            raise ApplicationError("Service with this name already exists in this organization")

        service = Service(
            organization_id=org_id,
            name=request.name,
            price=request.price,
            duration_minutes=request.duration_minutes,
            description=request.description,
        )

        async with self._uow:
            saved = await self._service_repo.add(service)

        return ServiceResponse(
            id=str(saved.id),
            organization_id=str(saved.organization_id),
            name=saved.name,
            price=saved.price,
            duration_minutes=saved.duration_minutes,
            description=saved.description,
            is_active=saved.is_active,
        )
