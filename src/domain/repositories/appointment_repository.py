import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from src.domain.entities.appointment import Appointment
from src.domain.repositories.base import AbstractBaseRepository


class AppointmentRepository(AbstractBaseRepository[Appointment], ABC):
    @abstractmethod
    async def list_by_organization_id(self, organization_id: uuid.UUID) -> list[Appointment]: ...

    @abstractmethod
    async def list_for_employee(self, employee_id, limit: int = 100) -> list[Appointment]: ...

    @abstractmethod
    async def list_for_client(self, client_id, limit: int = 100) -> list[Appointment]: ...

    @abstractmethod
    async def list_between_dates(self, start: datetime, end: datetime) -> list[Appointment]: ...

    @abstractmethod
    async def find_overlapping(
        self,
        employee_id: uuid.UUID,
        starts_at: datetime,
        ends_at: datetime,
        exclude_id: uuid.UUID | None = None,
    ) -> list[Appointment]: ...
