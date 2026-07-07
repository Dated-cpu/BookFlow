from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select

from src.domain.entities.appointment import Appointment, AppointmentStatus
from src.domain.repositories.appointment_repository import AppointmentRepository
from src.infrastructure.database.models.appointment import AppointmentModel
from src.infrastructure.database.repositories.base import SQLAlchemyRepository


class SQLAlchemyAppointmentRepository(
    SQLAlchemyRepository[AppointmentModel], AppointmentRepository
):
    model_class = AppointmentModel

    def _to_domain(self, model: AppointmentModel) -> Appointment:
        return Appointment(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            organization_id=model.organization_id,
            employee_id=model.employee_id,
            client_id=model.client_id,
            service_id=model.service_id,
            starts_at=model.starts_at,
            ends_at=model.ends_at,
            status=AppointmentStatus(model.status),
            notes=model.notes,
        )

    def _to_orm(self, entity: Appointment) -> AppointmentModel:
        return AppointmentModel(
            id=entity.id,
            organization_id=entity.organization_id,
            employee_id=entity.employee_id,
            client_id=entity.client_id,
            service_id=entity.service_id,
            starts_at=entity.starts_at,
            ends_at=entity.ends_at,
            status=entity.status.value,
            notes=entity.notes,
        )

    async def get_by_id(self, id) -> Appointment | None:
        model = await self._get(id)
        return self._to_domain(model) if model else None

    async def add(self, entity: Appointment) -> Appointment:
        model = self._to_orm(entity)
        saved = await self._save(model)
        return self._to_domain(saved)

    async def update(self, entity: Appointment) -> Appointment:
        model = await self._get(entity.id)
        if not model:
            raise ValueError(f"Appointment {entity.id} not found")
        model.organization_id = entity.organization_id
        model.employee_id = entity.employee_id
        model.client_id = entity.client_id
        model.service_id = entity.service_id
        model.starts_at = entity.starts_at
        model.ends_at = entity.ends_at
        model.status = entity.status.value
        model.notes = entity.notes
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, entity: Appointment) -> None:
        model = await self._get(entity.id)
        if model:
            await self._delete(model)

    async def list(self) -> list[Appointment]:
        return [self._to_domain(m) for m in await self._list()]

    async def list_by_organization_id(self, organization_id: uuid.UUID) -> list[Appointment]:
        result = await self._session.execute(
            select(AppointmentModel).where(
                AppointmentModel.organization_id == organization_id
            )
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def list_for_employee(self, employee_id, limit: int = 100) -> list[Appointment]:
        result = await self._session.execute(
            select(AppointmentModel).where(AppointmentModel.employee_id == employee_id).limit(limit)
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def list_for_client(self, client_id, limit: int = 100) -> list[Appointment]:
        result = await self._session.execute(
            select(AppointmentModel).where(AppointmentModel.client_id == client_id).limit(limit)
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def list_between_dates(self, start: datetime, end: datetime) -> list[Appointment]:
        result = await self._session.execute(
            select(AppointmentModel)
            .where(AppointmentModel.starts_at >= start)
            .where(AppointmentModel.ends_at <= end)
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def find_overlapping(
        self,
        employee_id: uuid.UUID,
        starts_at: datetime,
        ends_at: datetime,
        exclude_id: uuid.UUID | None = None,
    ) -> list[Appointment]:
        stmt = select(AppointmentModel).where(
            AppointmentModel.employee_id == employee_id,
            AppointmentModel.status != AppointmentStatus.CANCELLED.value,
            AppointmentModel.starts_at < ends_at,
            AppointmentModel.ends_at > starts_at,
        )
        if exclude_id:
            stmt = stmt.where(AppointmentModel.id != exclude_id)
        result = await self._session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]
