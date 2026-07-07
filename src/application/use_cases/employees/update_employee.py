from uuid import UUID

from src.application.base import BaseUseCase
from src.application.dtos.employees.update_employee import (
    UpdateEmployeeRequest,
    UpdateEmployeeResponse,
)
from src.application.exceptions import ApplicationError
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.repositories.employee_repository import EmployeeRepository
from src.domain.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)


class UpdateEmployee(BaseUseCase[UpdateEmployeeRequest, UpdateEmployeeResponse]):
    def __init__(
        self,
        employee_repo: EmployeeRepository,
        org_member_repo: OrganizationMemberRepository,
        uow: UnitOfWork,
    ) -> None:
        self._employee_repo = employee_repo
        self._org_member_repo = org_member_repo
        self._uow = uow

    async def execute(self, request: UpdateEmployeeRequest) -> UpdateEmployeeResponse:
        employee = await self._employee_repo.get_by_id(UUID(request.employee_id))
        if not employee:
            raise ApplicationError("Employee not found")

        memberships = await self._org_member_repo.list_by_user_id(UUID(request.user_id))
        if not any(m.organization_id == employee.organization_id for m in memberships):
            raise ApplicationError("Employee not found")

        if request.name is not None:
            employee.name = request.name
        if request.phone is not None:
            employee.phone = request.phone
        if request.is_active is not None:
            if request.is_active:
                employee.activate()
            else:
                employee.deactivate()

        async with self._uow:
            updated = await self._employee_repo.update(employee)

        return UpdateEmployeeResponse(
            id=str(updated.id),
            organization_id=str(updated.organization_id),
            name=updated.name,
            email=updated.email,
            phone=updated.phone,
            is_active=updated.is_active,
        )
