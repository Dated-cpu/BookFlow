from uuid import UUID

from src.application.base import BaseUseCase
from src.application.dtos.services.create_service import ServiceResponse
from src.application.dtos.services.list_services import ListServicesRequest
from src.application.exceptions import ApplicationError
from src.domain.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from src.domain.repositories.service_repository import ServiceRepository


class ListServices(BaseUseCase[ListServicesRequest, list[ServiceResponse]]):
    def __init__(
        self,
        service_repo: ServiceRepository,
        org_member_repo: OrganizationMemberRepository,
    ) -> None:
        self._service_repo = service_repo
        self._org_member_repo = org_member_repo

    async def execute(self, request: ListServicesRequest) -> list[ServiceResponse]:
        org_id = UUID(request.organization_id)

        memberships = await self._org_member_repo.list_by_user_id(UUID(request.user_id))
        if not any(m.organization_id == org_id for m in memberships):
            raise ApplicationError("Organization not found")

        services = await self._service_repo.list_by_organization_id(org_id)
        return [
            ServiceResponse(
                id=str(s.id),
                organization_id=str(s.organization_id),
                name=s.name,
                price=s.price,
                duration_minutes=s.duration_minutes,
                description=s.description,
                is_active=s.is_active,
            )
            for s in services
        ]
