from uuid import UUID

from src.application.base import BaseUseCase
from src.application.dtos.employees.delete_employee import DeleteEmployeeRequest
from src.application.exceptions import ApplicationError
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.repositories.employee_repository import EmployeeRepository
from src.domain.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)


class DeleteEmployee(BaseUseCase[DeleteEmployeeRequest, None]):
    def __init__(
        self,
        employee_repo: EmployeeRepository,
        org_member_repo: OrganizationMemberRepository,
        uow: UnitOfWork,
    ) -> None:
        self._employee_repo = employee_repo
        self._org_member_repo = org_member_repo
        self._uow = uow

    async def execute(self, request: DeleteEmployeeRequest) -> None:
        employee = await self._employee_repo.get_by_id(UUID(request.employee_id))
        if not employee:
            raise ApplicationError("Employee not found")

        memberships = await self._org_member_repo.list_by_user_id(UUID(request.user_id))
        if not any(m.organization_id == employee.organization_id for m in memberships):
            raise ApplicationError("Employee not found")

        # Soft delete — deactivate the employee
        employee.deactivate()

        async with self._uow:
            await self._employee_repo.update(employee)
