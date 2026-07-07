import uuid
from abc import ABC, abstractmethod

from src.domain.entities.service import Service
from src.domain.repositories.base import AbstractBaseRepository


class ServiceRepository(AbstractBaseRepository[Service], ABC):
    @abstractmethod
    async def list_by_organization_id(self, organization_id: uuid.UUID) -> list[Service]: ...

    @abstractmethod
    async def get_by_name_and_org(
        self, name: str, organization_id: uuid.UUID
    ) -> Service | None: ...
