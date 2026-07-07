from uuid import UUID

from src.application.base import BaseUseCase
from src.application.dtos.organizations.invite_employee import (
    InviteEmployeeRequest,
    InviteEmployeeResponse,
)
from src.application.exceptions import ApplicationError
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.entities.employee import Employee
from src.domain.repositories.employee_repository import EmployeeRepository
from src.domain.repositories.organization_repository import OrganizationRepository


class InviteEmployee(BaseUseCase[InviteEmployeeRequest, InviteEmployeeResponse]):
    def __init__(
        self,
        org_repo: OrganizationRepository,
        employee_repo: EmployeeRepository,
        uow: UnitOfWork,
    ) -> None:
        self._org_repo = org_repo
        self._employee_repo = employee_repo
        self._uow = uow

    async def execute(self, request: InviteEmployeeRequest) -> InviteEmployeeResponse:
        org = await self._org_repo.get_by_id(UUID(request.organization_id))
        if not org:
            raise ApplicationError("Organization not found")

        employee = Employee(
            organization_id=org.id,
            name=request.name,
            email=request.email,
            phone=request.phone,
        )

        async with self._uow:
            saved = await self._employee_repo.add(employee)

        return InviteEmployeeResponse(
            id=str(saved.id),
            organization_id=str(saved.organization_id),
            name=saved.name,
            email=saved.email,
            phone=saved.phone,
        )
