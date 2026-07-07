from uuid import UUID

from src.application.base import BaseUseCase
from src.application.dtos.employees.create_employee import (
    CreateEmployeeRequest,
    EmployeeResponse,
)
from src.application.exceptions import ApplicationError
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.entities.employee import Employee
from src.domain.repositories.employee_repository import EmployeeRepository
from src.domain.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)


class CreateEmployee(BaseUseCase[CreateEmployeeRequest, EmployeeResponse]):
    def __init__(
        self,
        employee_repo: EmployeeRepository,
        org_member_repo: OrganizationMemberRepository,
        uow: UnitOfWork,
    ) -> None:
        self._employee_repo = employee_repo
        self._org_member_repo = org_member_repo
        self._uow = uow

    async def execute(self, request: CreateEmployeeRequest) -> EmployeeResponse:
        org_id = UUID(request.organization_id)

        memberships = await self._org_member_repo.list_by_user_id(UUID(request.owner_user_id))
        if not any(m.organization_id == org_id for m in memberships):
            raise ApplicationError("Organization not found")

        existing = await self._employee_repo.get_by_email_and_org(request.email, org_id)
        if existing:
            raise ApplicationError("Employee with this email already exists in this organization")

        employee = Employee(
            organization_id=org_id,
            name=request.name,
            email=request.email,
            phone=request.phone,
        )

        async with self._uow:
            saved = await self._employee_repo.add(employee)

        return EmployeeResponse(
            id=str(saved.id),
            organization_id=str(saved.organization_id),
            name=saved.name,
            email=saved.email,
            phone=saved.phone,
            is_active=saved.is_active,
        )
