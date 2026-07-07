from uuid import UUID

from src.application.base import BaseUseCase
from src.application.dtos.appointments.get_appointment import (
    AppointmentDetailResponse,
    GetAppointmentRequest,
)
from src.application.exceptions import ApplicationError
from src.domain.repositories.appointment_repository import AppointmentRepository
from src.domain.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)


class GetAppointmentById(BaseUseCase[GetAppointmentRequest, AppointmentDetailResponse]):
    def __init__(
        self,
        appointment_repo: AppointmentRepository,
        org_member_repo: OrganizationMemberRepository,
    ) -> None:
        self._appointment_repo = appointment_repo
        self._org_member_repo = org_member_repo

    async def execute(self, request: GetAppointmentRequest) -> AppointmentDetailResponse:
        appointment = await self._appointment_repo.get_by_id(UUID(request.appointment_id))
        if not appointment:
            raise ApplicationError("Appointment not found")

        memberships = await self._org_member_repo.list_by_user_id(UUID(request.user_id))
        if not any(m.organization_id == appointment.organization_id for m in memberships):
            raise ApplicationError("Appointment not found")

        return AppointmentDetailResponse(
            id=str(appointment.id),
            organization_id=str(appointment.organization_id),
            employee_id=str(appointment.employee_id),
            client_id=str(appointment.client_id),
            service_id=str(appointment.service_id),
            starts_at=appointment.starts_at,
            ends_at=appointment.ends_at,
            status=appointment.status.value,
            notes=appointment.notes,
        )
