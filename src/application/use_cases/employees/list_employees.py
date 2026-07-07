from uuid import UUID

from src.application.base import BaseUseCase
from src.application.dtos.employees.create_employee import EmployeeResponse
from src.application.dtos.employees.list_employees import ListEmployeesRequest
from src.application.exceptions import ApplicationError
from src.domain.repositories.employee_repository import EmployeeRepository
from src.domain.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)


class ListEmployees(BaseUseCase[ListEmployeesRequest, list[EmployeeResponse]]):
    def __init__(
        self,
        employee_repo: EmployeeRepository,
        org_member_repo: OrganizationMemberRepository,
    ) -> None:
        self._employee_repo = employee_repo
        self._org_member_repo = org_member_repo

    async def execute(self, request: ListEmployeesRequest) -> list[EmployeeResponse]:
        org_id = UUID(request.organization_id)

        memberships = await self._org_member_repo.list_by_user_id(UUID(request.user_id))
        if not any(m.organization_id == org_id for m in memberships):
            raise ApplicationError("Organization not found")

        employees = await self._employee_repo.list_by_organization_id(org_id)
        return [
            EmployeeResponse(
                id=str(e.id),
                organization_id=str(e.organization_id),
                name=e.name,
                email=e.email,
                phone=e.phone,
                is_active=e.is_active,
            )
            for e in employees
        ]
