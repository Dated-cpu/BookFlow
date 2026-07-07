from uuid import UUID

from src.application.base import BaseUseCase
from src.application.dtos.services.create_service import ServiceResponse
from src.application.dtos.services.get_service import GetServiceRequest
from src.application.exceptions import ApplicationError
from src.domain.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from src.domain.repositories.service_repository import ServiceRepository


class GetServiceById(BaseUseCase[GetServiceRequest, ServiceResponse]):
    def __init__(
        self,
        service_repo: ServiceRepository,
        org_member_repo: OrganizationMemberRepository,
    ) -> None:
        self._service_repo = service_repo
        self._org_member_repo = org_member_repo

    async def execute(self, request: GetServiceRequest) -> ServiceResponse:
        service = await self._service_repo.get_by_id(UUID(request.service_id))
        if not service:
            raise ApplicationError("Service not found")

        memberships = await self._org_member_repo.list_by_user_id(UUID(request.user_id))
        if not any(m.organization_id == service.organization_id for m in memberships):
            raise ApplicationError("Service not found")

        return ServiceResponse(
            id=str(service.id),
            organization_id=str(service.organization_id),
            name=service.name,
            price=service.price,
            duration_minutes=service.duration_minutes,
            description=service.description,
            is_active=service.is_active,
        )
