from uuid import UUID

from src.application.base import BaseUseCase
from src.application.dtos.appointments.list_appointments import (
    ListAppointmentsItem,
    ListAppointmentsRequest,
)
from src.application.exceptions import ApplicationError
from src.domain.repositories.appointment_repository import AppointmentRepository
from src.domain.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)


class ListAppointments(BaseUseCase[ListAppointmentsRequest, list[ListAppointmentsItem]]):
    def __init__(
        self,
        appointment_repo: AppointmentRepository,
        org_member_repo: OrganizationMemberRepository,
    ) -> None:
        self._appointment_repo = appointment_repo
        self._org_member_repo = org_member_repo

    async def execute(
        self, request: ListAppointmentsRequest
    ) -> list[ListAppointmentsItem]:
        org_id = UUID(request.organization_id)

        memberships = await self._org_member_repo.list_by_user_id(UUID(request.user_id))
        if not any(m.organization_id == org_id for m in memberships):
            raise ApplicationError("Organization not found")

        appointments = await self._appointment_repo.list_by_organization_id(org_id)
        return [
            ListAppointmentsItem(
                id=str(a.id),
                organization_id=str(a.organization_id),
                employee_id=str(a.employee_id),
                client_id=str(a.client_id),
                service_id=str(a.service_id),
                starts_at=a.starts_at,
                ends_at=a.ends_at,
                status=a.status.value,
                notes=a.notes,
            )
            for a in appointments
        ]
