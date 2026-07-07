from abc import ABC, abstractmethod

from src.domain.entities.organization import Organization
from src.domain.repositories.base import AbstractBaseRepository


class OrganizationRepository(AbstractBaseRepository[Organization], ABC):
    @abstractmethod
    async def get_by_slug(self, slug: str) -> Organization | None: ...
