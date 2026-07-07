from fastapi import APIRouter, Depends, status

from src.application.dtos.appointments.cancel_appointment import (
    CancelAppointmentRequest as CancelAppointmentAppRequest,
)
from src.application.dtos.appointments.create_appointment import (
    CreateAppointmentRequest as CreateAppointmentAppRequest,
)
from src.application.dtos.appointments.get_appointment import (
    GetAppointmentRequest as GetAppointmentAppRequest,
)
from src.application.dtos.appointments.list_appointments import (
    ListAppointmentsRequest as ListAppointmentsAppRequest,
)
from src.application.dtos.appointments.update_appointment import (
    UpdateAppointmentRequest as UpdateAppointmentAppRequest,
)
from src.application.use_cases.appointments.cancel_appointment import CancelAppointment
from src.application.use_cases.appointments.create_appointment import CreateAppointment
from src.application.use_cases.appointments.get_appointment import GetAppointmentById
from src.application.use_cases.appointments.list_appointments import ListAppointments
from src.application.use_cases.appointments.update_appointment import UpdateAppointment
from src.domain.entities.user import User
from src.presentation.api.v1.dependencies import (
    get_appointment_by_id_use_case,
    get_cancel_appointment_use_case,
    get_create_appointment_use_case,
    get_current_user,
    get_list_appointments_use_case,
    get_update_appointment_use_case,
)
from src.presentation.api.v1.schemas.appointments import (
    AppointmentCreateRequest,
    AppointmentResponse,
    AppointmentUpdateRequest,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_appointment(
    body: AppointmentCreateRequest,
    current_user: User = Depends(get_current_user),
    use_case: CreateAppointment = Depends(get_create_appointment_use_case),
) -> AppointmentResponse:
    app_request = CreateAppointmentAppRequest(
        organization_id=body.organization_id,
        owner_user_id=str(current_user.id),
        employee_id=body.employee_id,
        client_id=body.client_id,
        service_id=body.service_id,
        starts_at=body.starts_at,
        ends_at=body.ends_at,
        notes=body.notes,
    )
    result = await use_case.execute(app_request)
    return AppointmentResponse(
        id=result.id,
        organization_id=result.organization_id,
        employee_id=result.employee_id,
        client_id=result.client_id,
        service_id=result.service_id,
        starts_at=result.starts_at,
        ends_at=result.ends_at,
        status=result.status,
        notes=result.notes,
    )


@router.get(
    "",
    response_model=list[AppointmentResponse],
    status_code=status.HTTP_200_OK,
)
async def list_appointments(
    organization_id: str,
    current_user: User = Depends(get_current_user),
    use_case: ListAppointments = Depends(get_list_appointments_use_case),
) -> list[AppointmentResponse]:
    app_request = ListAppointmentsAppRequest(
        organization_id=organization_id,
        user_id=str(current_user.id),
    )
    result = await use_case.execute(app_request)
    return [
        AppointmentResponse(
            id=a.id,
            organization_id=a.organization_id,
            employee_id=a.employee_id,
            client_id=a.client_id,
            service_id=a.service_id,
            starts_at=a.starts_at,
            ends_at=a.ends_at,
            status=a.status,
            notes=a.notes,
        )
        for a in result
    ]


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_appointment(
    appointment_id: str,
    current_user: User = Depends(get_current_user),
    use_case: GetAppointmentById = Depends(get_appointment_by_id_use_case),
) -> AppointmentResponse:
    app_request = GetAppointmentAppRequest(
        appointment_id=appointment_id,
        user_id=str(current_user.id),
    )
    result = await use_case.execute(app_request)
    return AppointmentResponse(
        id=result.id,
        organization_id=result.organization_id,
        employee_id=result.employee_id,
        client_id=result.client_id,
        service_id=result.service_id,
        starts_at=result.starts_at,
        ends_at=result.ends_at,
        status=result.status,
        notes=result.notes,
    )


@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    status_code=status.HTTP_200_OK,
)
async def update_appointment(
    appointment_id: str,
    body: AppointmentUpdateRequest,
    current_user: User = Depends(get_current_user),
    use_case: UpdateAppointment = Depends(get_update_appointment_use_case),
) -> AppointmentResponse:
    app_request = UpdateAppointmentAppRequest(
        appointment_id=appointment_id,
        user_id=str(current_user.id),
        starts_at=body.starts_at,
        ends_at=body.ends_at,
        notes=body.notes,
    )
    result = await use_case.execute(app_request)
    return AppointmentResponse(
        id=result.id,
        organization_id=result.organization_id,
        employee_id=result.employee_id,
        client_id=result.client_id,
        service_id=result.service_id,
        starts_at=result.starts_at,
        ends_at=result.ends_at,
        status=result.status,
        notes=result.notes,
    )


@router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def cancel_appointment(
    appointment_id: str,
    current_user: User = Depends(get_current_user),
    use_case: CancelAppointment = Depends(get_cancel_appointment_use_case),
) -> None:
    app_request = CancelAppointmentAppRequest(
        appointment_id=appointment_id,
        user_id=str(current_user.id),
    )
    await use_case.execute(app_request)
