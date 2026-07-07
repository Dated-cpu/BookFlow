from uuid import UUID

from src.application.base import BaseUseCase
from src.application.dtos.employees.create_employee import EmployeeResponse
from src.application.dtos.employees.get_employee import GetEmployeeRequest
from src.application.exceptions import ApplicationError
from src.domain.repositories.employee_repository import EmployeeRepository
from src.domain.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)


class GetEmployeeById(BaseUseCase[GetEmployeeRequest, EmployeeResponse]):
    def __init__(
        self,
        employee_repo: EmployeeRepository,
        org_member_repo: OrganizationMemberRepository,
    ) -> None:
        self._employee_repo = employee_repo
        self._org_member_repo = org_member_repo

    async def execute(self, request: GetEmployeeRequest) -> EmployeeResponse:
        employee = await self._employee_repo.get_by_id(UUID(request.employee_id))
        if not employee:
            raise ApplicationError("Employee not found")

        memberships = await self._org_member_repo.list_by_user_id(UUID(request.user_id))
        if not any(m.organization_id == employee.organization_id for m in memberships):
            raise ApplicationError("Employee not found")

        return EmployeeResponse(
            id=str(employee.id),
            organization_id=str(employee.organization_id),
            name=employee.name,
            email=employee.email,
            phone=employee.phone,
            is_active=employee.is_active,
        )
