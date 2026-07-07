import uuid
from abc import ABC, abstractmethod

from src.domain.entities.organization_member import OrganizationMember
from src.domain.repositories.base import AbstractBaseRepository


class OrganizationMemberRepository(AbstractBaseRepository[OrganizationMember], ABC):
    @abstractmethod
    async def list_by_user_id(self, user_id: uuid.UUID) -> list[OrganizationMember]: ...
