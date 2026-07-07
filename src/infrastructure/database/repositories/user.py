from sqlalchemy import select

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.models.user import UserModel
from src.infrastructure.database.repositories.base import SQLAlchemyRepository


class SQLAlchemyUserRepository(SQLAlchemyRepository[UserModel], UserRepository):
    model_class = UserModel

    def _to_domain(self, model: UserModel) -> User:
        return User(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            email=model.email,
            hashed_password=model.hashed_password,
            is_active=model.is_active,
        )

    def _to_orm(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email,
            hashed_password=entity.hashed_password,
            is_active=entity.is_active,
        )

    async def get_by_id(self, id) -> User | None:
        model = await self._get(id)
        return self._to_domain(model) if model else None

    async def add(self, entity: User) -> User:
        model = self._to_orm(entity)
        saved = await self._save(model)
        return self._to_domain(saved)

    async def update(self, entity: User) -> User:
        model = await self._get(entity.id)
        if not model:
            raise ValueError(f"User {entity.id} not found")
        model.email = entity.email
        model.hashed_password = entity.hashed_password
        model.is_active = entity.is_active
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, entity: User) -> None:
        model = await self._get(entity.id)
        if model:
            await self._delete(model)

    async def list(self) -> list[User]:
        return [self._to_domain(m) for m in await self._list()]

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None
