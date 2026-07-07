import uuid
from abc import ABC, abstractmethod

from src.domain.entities.employee import Employee
from src.domain.repositories.base import AbstractBaseRepository


class EmployeeRepository(AbstractBaseRepository[Employee], ABC):
    @abstractmethod
    async def list_by_organization_id(self, organization_id: uuid.UUID) -> list[Employee]: ...

    @abstractmethod
    async def get_by_email_and_org(
        self, email: str, organization_id: uuid.UUID
    ) -> Employee | None: ...
