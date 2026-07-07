from __future__ import annotations

import uuid

from sqlalchemy import select

from src.domain.entities.service import Service
from src.domain.repositories.service_repository import ServiceRepository
from src.infrastructure.database.models.service import ServiceModel
from src.infrastructure.database.repositories.base import SQLAlchemyRepository


class SQLAlchemyServiceRepository(SQLAlchemyRepository[ServiceModel], ServiceRepository):
    model_class = ServiceModel

    def _to_domain(self, model: ServiceModel) -> Service:
        return Service(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            organization_id=model.organization_id,
            name=model.name,
            price=model.price,
            duration_minutes=model.duration_minutes,
            description=model.description,
            is_active=model.is_active,
        )

    def _to_orm(self, entity: Service) -> ServiceModel:
        return ServiceModel(
            id=entity.id,
            organization_id=entity.organization_id,
            name=entity.name,
            price=entity.price,
            duration_minutes=entity.duration_minutes,
            description=entity.description,
            is_active=entity.is_active,
        )

    async def get_by_id(self, id) -> Service | None:
        model = await self._get(id)
        return self._to_domain(model) if model else None

    async def add(self, entity: Service) -> Service:
        model = self._to_orm(entity)
        saved = await self._save(model)
        return self._to_domain(saved)

    async def update(self, entity: Service) -> Service:
        model = await self._get(entity.id)
        if not model:
            raise ValueError(f"Service {entity.id} not found")
        model.name = entity.name
        model.price = entity.price
        model.duration_minutes = entity.duration_minutes
        model.description = entity.description
        model.is_active = entity.is_active
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, entity: Service) -> None:
        model = await self._get(entity.id)
        if model:
            await self._delete(model)

    async def list(self) -> list[Service]:
        return [self._to_domain(m) for m in await self._list()]

    async def list_by_organization_id(self, organization_id: uuid.UUID) -> list[Service]:
        result = await self._session.execute(
            select(ServiceModel).where(ServiceModel.organization_id == organization_id)
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_by_name_and_org(self, name: str, organization_id: uuid.UUID) -> Service | None:
        result = await self._session.execute(
            select(ServiceModel).where(
                ServiceModel.name == name,
                ServiceModel.organization_id == organization_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None
