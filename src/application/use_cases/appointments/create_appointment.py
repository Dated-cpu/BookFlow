from uuid import UUID

from src.application.base import BaseUseCase
from src.application.dtos.appointments.create_appointment import (
    CreateAppointmentRequest,
    CreateAppointmentResponse,
)
from src.application.exceptions import ApplicationError
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.entities.appointment import Appointment
from src.domain.repositories.appointment_repository import AppointmentRepository
from src.domain.repositories.client_repository import ClientRepository
from src.domain.repositories.employee_repository import EmployeeRepository
from src.domain.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from src.domain.repositories.service_repository import ServiceRepository


class CreateAppointment(BaseUseCase[CreateAppointmentRequest, CreateAppointmentResponse]):
    def __init__(
        self,
        appointment_repo: AppointmentRepository,
        employee_repo: EmployeeRepository,
        client_repo: ClientRepository,
        service_repo: ServiceRepository,
        org_member_repo: OrganizationMemberRepository,
        uow: UnitOfWork,
    ) -> None:
        self._appointment_repo = appointment_repo
        self._employee_repo = employee_repo
        self._client_repo = client_repo
        self._service_repo = service_repo
        self._org_member_repo = org_member_repo
        self._uow = uow

    async def execute(self, request: CreateAppointmentRequest) -> CreateAppointmentResponse:
        org_id = UUID(request.organization_id)

        memberships = await self._org_member_repo.list_by_user_id(UUID(request.owner_user_id))
        if not any(m.organization_id == org_id for m in memberships):
            raise ApplicationError("Organization not found")

        employee = await self._employee_repo.get_by_id(UUID(request.employee_id))
        if not employee or employee.organization_id != org_id:
            raise ApplicationError("Employee not found in this organization")
        if not employee.is_active:
            raise ApplicationError("Employee is not active")

        client = await self._client_repo.get_by_id(UUID(request.client_id))
        if not client or client.organization_id != org_id:
            raise ApplicationError("Client not found in this organization")

        service = await self._service_repo.get_by_id(UUID(request.service_id))
        if not service or service.organization_id != org_id:
            raise ApplicationError("Service not found in this organization")
        if not service.is_active:
            raise ApplicationError("Service is not active")

        overlapping = await self._appointment_repo.find_overlapping(
            employee_id=employee.id,
            starts_at=request.starts_at,
            ends_at=request.ends_at,
        )
        if overlapping:
            raise ApplicationError("Employee already has an appointment in this time slot")

        appointment = Appointment(
            organization_id=org_id,
            employee_id=employee.id,
            client_id=client.id,
            service_id=service.id,
            starts_at=request.starts_at,
            ends_at=request.ends_at,
            notes=request.notes,
        )

        async with self._uow:
            saved = await self._appointment_repo.add(appointment)

        return CreateAppointmentResponse(
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
