from fastapi import APIRouter, Depends, status

from src.application.dtos.employees.create_employee import (
    CreateEmployeeRequest as CreateEmployeeAppRequest,
)
from src.application.dtos.employees.delete_employee import DeleteEmployeeRequest
from src.application.dtos.employees.get_employee import GetEmployeeRequest
from src.application.dtos.employees.list_employees import ListEmployeesRequest
from src.application.dtos.employees.update_employee import (
    UpdateEmployeeRequest as UpdateEmployeeAppRequest,
)
from src.application.use_cases.employees.create_employee import CreateEmployee
from src.application.use_cases.employees.delete_employee import DeleteEmployee
from src.application.use_cases.employees.get_employee import GetEmployeeById
from src.application.use_cases.employees.list_employees import ListEmployees
from src.application.use_cases.employees.update_employee import UpdateEmployee
from src.domain.entities.user import User
from src.presentation.api.v1.dependencies import (
    get_create_employee_use_case,
    get_current_user,
    get_delete_employee_use_case,
    get_employee_by_id_use_case,
    get_list_employees_use_case,
    get_update_employee_use_case,
)
from src.presentation.api.v1.schemas.employees import (
    EmployeeCreateRequest,
    EmployeeResponse,
    EmployeeUpdateRequest,
)

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_employee(
    body: EmployeeCreateRequest,
    current_user: User = Depends(get_current_user),
    use_case: CreateEmployee = Depends(get_create_employee_use_case),
) -> EmployeeResponse:
    app_request = CreateEmployeeAppRequest(
        organization_id=body.organization_id,
        owner_user_id=str(current_user.id),
        name=body.name,
        email=body.email,
        phone=body.phone,
    )
    result = await use_case.execute(app_request)
    return EmployeeResponse(
        id=result.id,
        organization_id=result.organization_id,
        name=result.name,
        email=result.email,
        phone=result.phone,
        is_active=result.is_active,
    )


@router.get(
    "",
    response_model=list[EmployeeResponse],
    status_code=status.HTTP_200_OK,
)
async def list_employees(
    organization_id: str,
    current_user: User = Depends(get_current_user),
    use_case: ListEmployees = Depends(get_list_employees_use_case),
) -> list[EmployeeResponse]:
    app_request = ListEmployeesRequest(
        organization_id=organization_id,
        user_id=str(current_user.id),
    )
    result = await use_case.execute(app_request)
    return [
        EmployeeResponse(
            id=e.id,
            organization_id=e.organization_id,
            name=e.name,
            email=e.email,
            phone=e.phone,
            is_active=e.is_active,
        )
        for e in result
    ]


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
)
async def get_employee(
    employee_id: str,
    current_user: User = Depends(get_current_user),
    use_case: GetEmployeeById = Depends(get_employee_by_id_use_case),
) -> EmployeeResponse:
    app_request = GetEmployeeRequest(
        employee_id=employee_id,
        user_id=str(current_user.id),
    )
    result = await use_case.execute(app_request)
    return EmployeeResponse(
        id=result.id,
        organization_id=result.organization_id,
        name=result.name,
        email=result.email,
        phone=result.phone,
        is_active=result.is_active,
    )


@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
)
async def update_employee(
    employee_id: str,
    body: EmployeeUpdateRequest,
    current_user: User = Depends(get_current_user),
    use_case: UpdateEmployee = Depends(get_update_employee_use_case),
) -> EmployeeResponse:
    app_request = UpdateEmployeeAppRequest(
        employee_id=employee_id,
        user_id=str(current_user.id),
        name=body.name,
        phone=body.phone,
        is_active=body.is_active,
    )
    result = await use_case.execute(app_request)
    return EmployeeResponse(
        id=result.id,
        organization_id=result.organization_id,
        name=result.name,
        email=result.email,
        phone=result.phone,
        is_active=result.is_active,
    )


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_employee(
    employee_id: str,
    current_user: User = Depends(get_current_user),
    use_case: DeleteEmployee = Depends(get_delete_employee_use_case),
) -> None:
    app_request = DeleteEmployeeRequest(
        employee_id=employee_id,
        user_id=str(current_user.id),
    )
    await use_case.execute(app_request)
