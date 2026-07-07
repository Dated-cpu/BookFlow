from __future__ import annotations

import uuid

from sqlalchemy import select

from src.domain.entities.employee import Employee
from src.domain.repositories.employee_repository import EmployeeRepository
from src.infrastructure.database.models.employee import EmployeeModel
from src.infrastructure.database.repositories.base import SQLAlchemyRepository


class SQLAlchemyEmployeeRepository(SQLAlchemyRepository[EmployeeModel], EmployeeRepository):
    model_class = EmployeeModel

    def _to_domain(self, model: EmployeeModel) -> Employee:
        return Employee(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            organization_id=model.organization_id,
            name=model.name,
            email=model.email,
            phone=model.phone,
            user_id=model.user_id,
            is_active=model.is_active,
        )

    def _to_orm(self, entity: Employee) -> EmployeeModel:
        return EmployeeModel(
            id=entity.id,
            organization_id=entity.organization_id,
            name=entity.name,
            email=entity.email,
            phone=entity.phone,
            user_id=entity.user_id,
            is_active=entity.is_active,
        )

    async def get_by_id(self, id) -> Employee | None:
        model = await self._get(id)
        return self._to_domain(model) if model else None

    async def add(self, entity: Employee) -> Employee:
        model = self._to_orm(entity)
        saved = await self._save(model)
        return self._to_domain(saved)

    async def update(self, entity: Employee) -> Employee:
        model = await self._get(entity.id)
        if not model:
            raise ValueError(f"Employee {entity.id} not found")
        model.name = entity.name
        model.email = entity.email
        model.phone = entity.phone
        model.user_id = entity.user_id
        model.is_active = entity.is_active
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, entity: Employee) -> None:
        model = await self._get(entity.id)
        if model:
            await self._delete(model)

    async def list(self) -> list[Employee]:
        return [self._to_domain(m) for m in await self._list()]

    async def list_by_organization_id(self, organization_id: uuid.UUID) -> list[Employee]:
        result = await self._session.execute(
            select(EmployeeModel).where(EmployeeModel.organization_id == organization_id)
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_by_email_and_org(self, email: str, organization_id: uuid.UUID) -> Employee | None:
        result = await self._session.execute(
            select(EmployeeModel).where(
                EmployeeModel.email == email,
                EmployeeModel.organization_id == organization_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None
