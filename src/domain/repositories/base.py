from abc import ABC, abstractmethod

from src.domain.base import BaseEntity


class AbstractBaseRepository[T: BaseEntity](ABC):
    @abstractmethod
    async def get_by_id(self, id) -> T | None: ...

    @abstractmethod
    async def add(self, entity: T) -> T: ...

    @abstractmethod
    async def update(self, entity: T) -> T: ...

    @abstractmethod
    async def delete(self, entity: T) -> None: ...

    @abstractmethod
    async def list(self) -> list[T]: ...
