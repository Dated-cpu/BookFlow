from __future__ import annotations

import uuid

from sqlalchemy import select

from src.domain.entities.organization_member import (
    OrganizationMember,
    OrganizationRole,
)
from src.domain.repositories.organization_member_repository import OrganizationMemberRepository
from src.infrastructure.database.models.organization_member import OrganizationMemberModel
from src.infrastructure.database.repositories.base import SQLAlchemyRepository


class SQLAlchemyOrganizationMemberRepository(
    SQLAlchemyRepository[OrganizationMemberModel], OrganizationMemberRepository
):
    model_class = OrganizationMemberModel

    def _to_domain(self, model: OrganizationMemberModel) -> OrganizationMember:
        return OrganizationMember(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            user_id=model.user_id,
            organization_id=model.organization_id,
            role=OrganizationRole(model.role),
        )

    def _to_orm(self, entity: OrganizationMember) -> OrganizationMemberModel:
        return OrganizationMemberModel(
            id=entity.id,
            user_id=entity.user_id,
            organization_id=entity.organization_id,
            role=entity.role.value,
        )

    async def get_by_id(self, id) -> OrganizationMember | None:
        model = await self._get(id)
        return self._to_domain(model) if model else None

    async def add(self, entity: OrganizationMember) -> OrganizationMember:
        model = self._to_orm(entity)
        saved = await self._save(model)
        return self._to_domain(saved)

    async def update(self, entity: OrganizationMember) -> OrganizationMember:
        model = await self._get(entity.id)
        if not model:
            raise ValueError(f"OrganizationMember {entity.id} not found")
        model.user_id = entity.user_id
        model.organization_id = entity.organization_id
        model.role = entity.role.value
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, entity: OrganizationMember) -> None:
        model = await self._get(entity.id)
        if model:
            await self._delete(model)

    async def list(self) -> list[OrganizationMember]:
        return [self._to_domain(m) for m in await self._list()]

    async def list_by_user_id(self, user_id: uuid.UUID) -> list[OrganizationMember]:
        result = await self._session.execute(
            select(OrganizationMemberModel).where(OrganizationMemberModel.user_id == user_id)
        )
        return [self._to_domain(m) for m in result.scalars().all()]
