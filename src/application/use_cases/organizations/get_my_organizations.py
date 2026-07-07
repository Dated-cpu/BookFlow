from uuid import UUID

from src.application.base import BaseUseCase
from src.application.dtos.organizations.get_my_organizations import (
    GetMyOrganizationsRequest,
    OrganizationWithRoleDTO,
)
from src.domain.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from src.domain.repositories.organization_repository import OrganizationRepository


class GetMyOrganizations(BaseUseCase[GetMyOrganizationsRequest, list[OrganizationWithRoleDTO]]):
    def __init__(
        self,
        org_repo: OrganizationRepository,
        org_member_repo: OrganizationMemberRepository,
    ) -> None:
        self._org_repo = org_repo
        self._org_member_repo = org_member_repo

    async def execute(self, request: GetMyOrganizationsRequest) -> list[OrganizationWithRoleDTO]:
        memberships = await self._org_member_repo.list_by_user_id(UUID(request.user_id))
        result: list[OrganizationWithRoleDTO] = []
        for m in memberships:
            org = await self._org_repo.get_by_id(m.organization_id)
            if org:
                result.append(
                    OrganizationWithRoleDTO(
                        id=str(org.id),
                        name=org.name,
                        slug=org.slug,
                        role=m.role.value,
                    )
                )
        return result
