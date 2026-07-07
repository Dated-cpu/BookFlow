from src.domain.entities.client import Client
from src.domain.repositories.client_repository import ClientRepository
from src.infrastructure.database.models.client import ClientModel
from src.infrastructure.database.repositories.base import SQLAlchemyRepository


class SQLAlchemyClientRepository(SQLAlchemyRepository[ClientModel], ClientRepository):
    model_class = ClientModel

    def _to_domain(self, model: ClientModel) -> Client:
        return Client(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            organization_id=model.organization_id,
            name=model.name,
            email=model.email,
            phone=model.phone,
            notes=model.notes,
        )

    def _to_orm(self, entity: Client) -> ClientModel:
        return ClientModel(
            id=entity.id,
            organization_id=entity.organization_id,
            name=entity.name,
            email=entity.email,
            phone=entity.phone,
            notes=entity.notes,
        )

    async def get_by_id(self, id) -> Client | None:
        model = await self._get(id)
        return self._to_domain(model) if model else None

    async def add(self, entity: Client) -> Client:
        model = self._to_orm(entity)
        saved = await self._save(model)
        return self._to_domain(saved)

    async def update(self, entity: Client) -> Client:
        model = await self._get(entity.id)
        if not model:
            raise ValueError(f"Client {entity.id} not found")
        model.name = entity.name
        model.email = entity.email
        model.phone = entity.phone
        model.notes = entity.notes
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, entity: Client) -> None:
        model = await self._get(entity.id)
        if model:
            await self._delete(model)

    async def list(self) -> list[Client]:
        return [self._to_domain(m) for m in await self._list()]
