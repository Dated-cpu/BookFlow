from sqlalchemy import select

from src.domain.entities.organization import Organization
from src.domain.repositories.organization_repository import OrganizationRepository
from src.infrastructure.database.models.organization import OrganizationModel
from src.infrastructure.database.repositories.base import SQLAlchemyRepository


class SQLAlchemyOrganizationRepository(
    SQLAlchemyRepository[OrganizationModel], OrganizationRepository
):
    model_class = OrganizationModel

    def _to_domain(self, model: OrganizationModel) -> Organization:
        return Organization(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            name=model.name,
            slug=model.slug,
            is_active=model.is_active,
        )

    def _to_orm(self, entity: Organization) -> OrganizationModel:
        return OrganizationModel(
            id=entity.id,
            name=entity.name,
            slug=entity.slug,
            is_active=entity.is_active,
        )

    async def get_by_id(self, id) -> Organization | None:
        model = await self._get(id)
        return self._to_domain(model) if model else None

    async def add(self, entity: Organization) -> Organization:
        model = self._to_orm(entity)
        saved = await self._save(model)
        return self._to_domain(saved)

    async def update(self, entity: Organization) -> Organization:
        model = await self._get(entity.id)
        if not model:
            raise ValueError(f"Organization {entity.id} not found")
        model.name = entity.name
        model.slug = entity.slug
        model.is_active = entity.is_active
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, entity: Organization) -> None:
        model = await self._get(entity.id)
        if model:
            await self._delete(model)

    async def list(self) -> list[Organization]:
        return [self._to_domain(m) for m in await self._list()]

    async def get_by_slug(self, slug: str) -> Organization | None:
        result = await self._session.execute(
            select(OrganizationModel).where(OrganizationModel.slug == slug)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None
