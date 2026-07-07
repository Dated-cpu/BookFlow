from abc import ABC, abstractmethod

from src.domain.entities.user import User
from src.domain.repositories.base import AbstractBaseRepository


class UserRepository(AbstractBaseRepository[User], ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...
