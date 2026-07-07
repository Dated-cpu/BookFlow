from abc import ABC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.base import Base


class SQLAlchemyRepository[T: Base](ABC):
    model_class: type[T]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get(self, id) -> T | None:
        return await self._session.get(self.model_class, id)

    async def _list(self) -> list[T]:
        result = await self._session.execute(select(self.model_class))
        return list(result.scalars().all())

    async def _save(self, model: T) -> T:
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model

    async def _delete(self, model: T) -> None:
        await self._session.delete(model)
        await self._session.flush()
