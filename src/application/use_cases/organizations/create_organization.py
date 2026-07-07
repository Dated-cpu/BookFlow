import re
from uuid import UUID

from src.application.base import BaseUseCase
from src.application.dtos.organizations.create_organization import (
    CreateOrganizationRequest,
    CreateOrganizationResponse,
)
from src.application.exceptions import ApplicationError
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.entities.organization import Organization
from src.domain.entities.organization_member import OrganizationMember, OrganizationRole
from src.domain.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from src.domain.repositories.organization_repository import OrganizationRepository


def _slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s-]+", "-", s)
    return s.strip("-")


class CreateOrganization(BaseUseCase[CreateOrganizationRequest, CreateOrganizationResponse]):
    def __init__(
        self,
        org_repo: OrganizationRepository,
        org_member_repo: OrganizationMemberRepository,
        uow: UnitOfWork,
    ) -> None:
        self._org_repo = org_repo
        self._org_member_repo = org_member_repo
        self._uow = uow

    async def execute(self, request: CreateOrganizationRequest) -> CreateOrganizationResponse:
        slug = _slugify(request.name)
        if not slug:
            raise ApplicationError("Could not generate slug from name")

        existing = await self._org_repo.get_by_slug(slug)
        if existing:
            raise ApplicationError("Organization with this name already exists")

        org = Organization(name=request.name, slug=slug)

        async with self._uow:
            saved_org = await self._org_repo.add(org)
            member = OrganizationMember(
                user_id=UUID(request.owner_user_id),
                organization_id=saved_org.id,
                role=OrganizationRole.OWNER,
            )
            saved_member = await self._org_member_repo.add(member)

        return CreateOrganizationResponse(
            id=str(saved_org.id),
            name=saved_org.name,
            slug=saved_org.slug,
            membership_id=str(saved_member.id),
        )
