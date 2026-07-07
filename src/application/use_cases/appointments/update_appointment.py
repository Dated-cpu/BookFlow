from uuid import UUID

from src.application.base import BaseUseCase
from src.application.dtos.appointments.update_appointment import (
    UpdateAppointmentRequest,
    UpdateAppointmentResponse,
)
from src.application.exceptions import ApplicationError
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.repositories.appointment_repository import AppointmentRepository
from src.domain.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)


class UpdateAppointment(BaseUseCase[UpdateAppointmentRequest, UpdateAppointmentResponse]):
    def __init__(
        self,
        appointment_repo: AppointmentRepository,
        org_member_repo: OrganizationMemberRepository,
        uow: UnitOfWork,
    ) -> None:
        self._appointment_repo = appointment_repo
        self._org_member_repo = org_member_repo
        self._uow = uow

    async def execute(self, request: UpdateAppointmentRequest) -> UpdateAppointmentResponse:
        appointment = await self._appointment_repo.get_by_id(UUID(request.appointment_id))
        if not appointment:
            raise ApplicationError("Appointment not found")

        memberships = await self._org_member_repo.list_by_user_id(UUID(request.user_id))
        if not any(m.organization_id == appointment.organization_id for m in memberships):
            raise ApplicationError("Appointment not found")

        if request.starts_at is not None or request.ends_at is not None:
            new_starts_at = (
                request.starts_at if request.starts_at is not None
                else appointment.starts_at
            )
            new_ends_at = (
                request.ends_at if request.ends_at is not None
                else appointment.ends_at
            )

            overlapping = await self._appointment_repo.find_overlapping(
                employee_id=appointment.employee_id,
                starts_at=new_starts_at,
                ends_at=new_ends_at,
                exclude_id=appointment.id,
            )
            if overlapping:
                raise ApplicationError("Employee already has an appointment in this time slot")

            appointment.reschedule(new_starts_at, new_ends_at)

        if request.notes is not None:
            appointment.notes = request.notes

        async with self._uow:
            saved = await self._appointment_repo.update(appointment)

        return UpdateAppointmentResponse(
            id=str(saved.id),
            organization_id=str(saved.organization_id),
            employee_id=str(saved.employee_id),
            client_id=str(saved.client_id),
            service_id=str(saved.service_id),
            starts_at=saved.starts_at,
            ends_at=saved.ends_at,
            status=saved.status.value,
            notes=saved.notes,
        )
