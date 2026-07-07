from uuid import UUID

from src.application.base import BaseUseCase
from src.application.dtos.appointments.cancel_appointment import (
    CancelAppointmentRequest,
    CancelAppointmentResponse,
)
from src.application.exceptions import ApplicationError
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.repositories.appointment_repository import AppointmentRepository
from src.domain.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)


class CancelAppointment(BaseUseCase[CancelAppointmentRequest, CancelAppointmentResponse]):
    def __init__(
        self,
        appointment_repo: AppointmentRepository,
        org_member_repo: OrganizationMemberRepository,
        uow: UnitOfWork,
    ) -> None:
        self._appointment_repo = appointment_repo
        self._org_member_repo = org_member_repo
        self._uow = uow

    async def execute(self, request: CancelAppointmentRequest) -> CancelAppointmentResponse:
        appointment = await self._appointment_repo.get_by_id(UUID(request.appointment_id))
        if not appointment:
            raise ApplicationError("Appointment not found")

        memberships = await self._org_member_repo.list_by_user_id(UUID(request.user_id))
        if not any(m.organization_id == appointment.organization_id for m in memberships):
            raise ApplicationError("Appointment not found")

        appointment.cancel()

        async with self._uow:
            saved = await self._appointment_repo.update(appointment)

        return CancelAppointmentResponse(
            id=str(saved.id),
            status=saved.status.value,
        )
