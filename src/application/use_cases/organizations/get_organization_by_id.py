from uuid import UUID

from src.application.base import BaseUseCase
from src.application.dtos.organizations.get_organization_by_id import (
    GetOrganizationByIdRequest,
    OrganizationResponseDTO,
)
from src.application.exceptions import ApplicationError
from src.domain.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from src.domain.repositories.organization_repository import OrganizationRepository


class GetOrganizationById(BaseUseCase[GetOrganizationByIdRequest, OrganizationResponseDTO]):
    def __init__(
        self,
        org_repo: OrganizationRepository,
        org_member_repo: OrganizationMemberRepository,
    ) -> None:
        self._org_repo = org_repo
        self._org_member_repo = org_member_repo

    async def execute(self, request: GetOrganizationByIdRequest) -> OrganizationResponseDTO:
        org = await self._org_repo.get_by_id(UUID(request.organization_id))
        if not org:
            raise ApplicationError("Organization not found")

        memberships = await self._org_member_repo.list_by_user_id(UUID(request.user_id))
        if not any(m.organization_id == org.id for m in memberships):
            raise ApplicationError("Organization not found")

        return OrganizationResponseDTO(
            id=str(org.id),
            name=org.name,
            slug=org.slug,
            is_active=org.is_active,
        )
